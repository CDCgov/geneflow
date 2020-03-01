"""This module contains methods for the run CLI command."""


import os
from pathlib import Path
from multiprocessing import Pool
from functools import partial

import geneflow.cli.common
from geneflow.config import Config
from geneflow.definition import Definition
from geneflow.environment import Environment
from geneflow.log import Log
from geneflow.data import DataSource, DataSourceException
from geneflow.uri_parser import URIParser


def init_subparser(subparsers):
    """Initialize the run CLI subparser."""
    parser = subparsers.add_parser('run', help='run a GeneFlow workflow')
    parser.add_argument(
        'workflow',
        type=str,
        help='GeneFlow workflow definition or package directory'
    )
    parser.add_argument(
        '-j', '--job_yaml',
        type=str,
        default=None,
        help='geneflow definition yaml for job(s)'
    )
    parser.add_argument(
        '-d', '--data',
        type=str,
        action='append',
        help='job definition modifier'
    )
    parser.set_defaults(func=run)


def resolve_workflow_path(workflow_identifier):
    """
    Search GENEFLOW_PATH env var to find workflow definition.

    Args:
        workflow_identifier: workflow identifier

    Returns:
        On success: Full path of workflow yaml file (str).
        On failure: False.

    """
    # check if abs path or in current directory first (.)
    abs_path = Path.absolute(Path(workflow_identifier))
    if abs_path.is_file():
        return str(abs_path)

    if abs_path.is_dir(): # assume this is the name of workflow package dir
        yaml_path = Path(abs_path / 'workflow' / 'workflow.yaml')
        if yaml_path.is_file():
            return str(yaml_path)

    # search GENEFLOW_PATH
    gf_path = os.environ.get('GENEFLOW_PATH')

    if gf_path:
        for path in gf_path.split(':'):
            if path:
                wf_path = Path(path) / workflow_identifier
                if wf_path.is_dir():
                    yaml_path = Path(wf_path / 'workflow' / 'workflow.yaml')
                    if yaml_path.is_file():
                        return str(yaml_path)

    Log.an().error(
        'workflow "%s" not found, check GENEFLOW_PATH', workflow_identifier
    )
    return False


def set_dict_key_list(dict_obj, keys, val):
    """Update a dict based on given hierarchy of keys and val."""
    for key in keys[:-1]:
        dict_obj = dict_obj.setdefault(key, {})
    dict_obj[keys[-1]] = val


def apply_job_modifiers(jobs_dict, job_mods):
    """Update the jobs_dict with the given modifiers."""
    for mod in job_mods:
        # split at =
        try:
            parts = mod.split('=')
        except ValueError as err:
            Log.a().warning('job mod "%s" is malformed [%s]', mod, str(err))
            continue # skip mod

        key = parts[0]
        if not key:
            Log.a().warning('empty job mod')
            continue # skip mod

        val = None
        if len(parts) == 1:
            # only one key, treat as bool switch
            val = True
        elif len(parts) == 2:
            # two parts, key & value
            val = parts[1]
        else:
            # multiple '=', include '=' in value
            val = '='.join(parts[1:])

        # split key at .
        keys = key.split('.')

        # apply to all jobs
        for job in jobs_dict.values():
            set_dict_key_list(job, keys, val)


def run(args):
    """
    Run GeneFlow workflow engine.

    Args:
        args.workflow: workflow definition or package directory.
        args.job_yaml: job definition.

    Returns:
        On success: True.
        On failure: False.

    """
    # get absolute path to workflow
    workflow_yaml = resolve_workflow_path(args.workflow)
    if workflow_yaml:
        Log.some().info('workflow definition found: %s', workflow_yaml)
    else:
        Log.an().error('cannot find workflow definition: %s', args.workflow)
        return False

    # get absolute path to job file if provided
    job_yaml = None
    if args.job_yaml:
        job_yaml = Path(args.job_yaml).absolute()

    # setup environment
    env = Environment(workflow_path=workflow_yaml)
    if not env.initialize():
        Log.an().error('cannot initialize geneflow environment')
        return False

    # create default config file and SQLite db
    cfg = Config()
    cfg.default(env.get_sqlite_db_path())
    cfg.write(env.get_config_path())
    config_dict = cfg.config('local')

    # load workflow into db
    try:
        data_source = DataSource(config_dict['database'])
    except DataSourceException as err:
        Log.an().error('data source initialization error [%s]', str(err))
        return False

    defs = data_source.import_definition(workflow_yaml)
    if not defs:
        Log.an().error('workflow definition load failed: %s', workflow_yaml)
        return False

    if not defs['workflows']:
        Log.an().error('workflow definition load failed: %s', workflow_yaml)
        return False

    data_source.commit()

    for workflow in defs['workflows']:
        Log.some().info(
            'workflow loaded: %s -> %s', workflow, defs['workflows'][workflow]
        )

    # load job definition if provided
    jobs_dict = {}
    gf_def = Definition()
    if job_yaml:
        if not gf_def.load(job_yaml):
            Log.an().error('Job definition load failed')
            return False
        jobs_dict = gf_def.jobs()
    else:
        # create default definition
        jobs_dict = {
            'job': {
                'name': 'GeneFlow job',
                'output_uri': 'geneflow_output',
                'work_uri': {
                    'local': '~/.geneflow/work'
                }
            }
        }

    # override with cli parameters
    if args.data:
        apply_job_modifiers(jobs_dict, args.data)

    # insert workflow name, if not provided
    workflow_name = next(iter(defs['workflows']))
    for job in jobs_dict.values():
        if 'workflow_name' not in job:
            job['workflow_name'] = workflow_name

    # extract workflow defaults for inputs and parameters if not provided
    # in job definition
    workflow_id = next(iter(defs['workflows'].values()))
    workflow_dict = data_source.get_workflow_def_by_id(workflow_id)
    if not workflow_dict:
        Log.an().error(
            'cannot get workflow definition from data source: workflow_id=%s',
            workflow_id
        )
        return False

    for job in jobs_dict.values():
        if 'inputs' not in job:
            job['inputs'] = {}
        if 'parameters' not in job:
            job['parameters'] = {}
        for input_key in workflow_dict['inputs']:
            if input_key not in job['inputs']:
                job['inputs'][input_key]\
                    = workflow_dict['inputs'][input_key]['default']
        for param_key in workflow_dict['parameters']:
            if param_key not in job['parameters']:
                job['parameters'][param_key]\
                    = workflow_dict['parameters'][param_key]['default']

    # expand URIs
    for job in jobs_dict.values():
        # output URI
        parsed_uri = URIParser.parse(job['output_uri'])
        if not parsed_uri:
            Log.an().error('invalid output uri: %s', job['output_uri'])
            return False
        # expand relative path if local
        if parsed_uri['scheme'] == 'local':
            job['output_uri'] = str(
                Path(parsed_uri['chopped_path']).expanduser().resolve()
            )
        # work URIs
        for context in job['work_uri']:
            parsed_uri = URIParser.parse(job['work_uri'][context])
            if not parsed_uri:
                Log.an().error('invalid work uri: %s', job['work_uri'])
                return False
            # expand relative path if local
            if parsed_uri['scheme'] == 'local':
                job['work_uri'][context] = str(
                    Path(parsed_uri['chopped_path']).expanduser().resolve()
                )
        # input URIs
        for input_key in job['inputs']:
            parsed_uri = URIParser.parse(job['inputs'][input_key])
            if not parsed_uri:
                Log.an().error(
                    'invalid input uri: %s', job['inputs'][input_key]
                )
                return False
            # expand relative path if local
            if parsed_uri['scheme'] == 'local':
                job['inputs'][input_key] = str(
                    Path(parsed_uri['chopped_path']).expanduser().resolve()
                )

    # import jobs into database
    job_ids = data_source.import_jobs_from_dict(jobs_dict)
    if job_ids is False:
        Log.an().error('cannot import jobs')
        return False
    data_source.commit()

    # create process pool to run workflows in parallel
    pool = Pool(min(5, len(job_ids)))
    jobs = [
        {
            'name': job,
            'id': job_ids[job],
            'log': None
        } for job in job_ids
    ]

    result = pool.map(
        partial(
            geneflow.cli.common.run_workflow,
            config=config_dict,
            log_level=args.log_level
        ),
        jobs
    )

    pool.close()
    pool.join()

    if not all(result):
        Log.an().error('some jobs failed')

    return result
