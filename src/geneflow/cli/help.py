"""This module contains methods for the help CLI command."""


import os
from pathlib import Path

from geneflow.definition import Definition
from geneflow.log import Log


def init_subparser(subparsers):
    """Initialize the help CLI subparser."""
    parser = subparsers.add_parser('help', help='GeneFlow workflow help')
    parser.add_argument(
        'workflow',
        type=str,
        help='GeneFlow workflow definition or package directory'
    )
    parser.set_defaults(func=help_func)


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


def help_func(args):
    """
    GeneFlow workflow help.

    Args:
        args.workflow: workflow definition or package directory.

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

    # load workflow
    gf_def = Definition()
    if not gf_def.load(workflow_yaml):
        Log.an().error('workflow definition load failed: %s', workflow_yaml)
        return False

    # get first workflow dict
    workflow_dict = next(iter(gf_def.workflows().values()))
    print()
    print('GeneFlow: {}'.format(workflow_dict['name']))
    print()
    print('{}'.format(workflow_dict['description']))
    print()
    print('Inputs:')
    for input_key in workflow_dict['inputs']:
        print(
            '\t--{}: {}: {}'.format(
                input_key,
                workflow_dict['inputs'][input_key]['label'],
                workflow_dict['inputs'][input_key]['description']
            )
        )
        print(
            '\t\ttype: {}, default: {}'.format(
                workflow_dict['inputs'][input_key]['type'],
                workflow_dict['inputs'][input_key]['default']
            )
        )
    print()
    print('Parameters:')
    for param_key in workflow_dict['parameters']:
        print(
            '\t--{}: {}: {}'.format(
                param_key,
                workflow_dict['parameters'][param_key]['label'],
                workflow_dict['parameters'][param_key]['description']
            )
        )
        print(
            '\t\ttype: {}, default: {}'.format(
                workflow_dict['parameters'][param_key]['type'],
                workflow_dict['parameters'][param_key]['default']
            )
        )

    return True
