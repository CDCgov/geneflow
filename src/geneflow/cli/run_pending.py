"""This module contains methods for the run-pending CLI command."""


from pathlib import Path
from multiprocessing import Pool
from functools import partial
import pprint

import geneflow.cli.common
from geneflow.config import Config
from geneflow.log import Log
from geneflow.data import DataSource, DataSourceException


def init_subparser(subparsers):
    """Initialize the run-pending CLI subparser."""
    parser = subparsers.add_parser(
        'run-pending', help='run pending workflow jobs'
    )
    parser.add_argument(
        '-c', '--config_file',
        type=str,
        required=True,
        help='geneflow config file path'
    )
    parser.add_argument(
        '-e', '--environment',
        type=str,
        required=True,
        help='environment'
    )
    parser.add_argument(
        '--log_location',
        type=str,
        required=True,
        help='log location'
    )
    parser.set_defaults(func=run_pending)


def run_pending(args):
    """
    Run any jobs in database in the PENDING state.

    Args:
        args.config_file: GeneFlow config file path.
        args.environment: Config environment.

    Returns:
        On success: True.
        On failure: False.

    """
    config_file = args.config_file
    environment = args.environment
    log_location = args.log_location

    # load config file
    cfg = Config()
    if not cfg.load(config_file):
        Log.an().error('cannot load config file: %s', config_file)
        return False

    config_dict = cfg.config(environment)
    if not config_dict:
        Log.an().error('invalid config environment: %s', environment)
        return False

    # connect to data source
    try:
        data_source = DataSource(config_dict['database'])
    except DataSourceException as err:
        Log.an().error('data source initialization error [%s]', str(err))
        return False

    # get pending jobs from database
    pending_jobs = data_source.get_pending_jobs()
    if pending_jobs is False:
        Log.an().error('cannot query for pending jobs')
        return False

    if not pending_jobs:
        # no jobs found
        return True

    Log.some().info(
        'pending jobs found:\n%s', pprint.pformat(pending_jobs)
    )

    pool = Pool(min(5, len(pending_jobs)))
    jobs = [
        {
            'name': job['name'],
            'id': job['id'],
            'log': str(Path(log_location) / (job['id']+'.log'))
        } for job in pending_jobs
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
