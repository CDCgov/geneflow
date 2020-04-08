"""This module contains methods for the add-workflows CLI command."""


from geneflow.config import Config
from geneflow.data import DataSource, DataSourceException
from geneflow.log import Log


def init_subparser(subparsers):
    """Initialize the add-workflows CLI subparser."""
    parser = subparsers.add_parser(
        'add-workflows', help='add workflows to database'
    )
    parser.add_argument(
        'workflow_yaml',
        type=str,
        help='geneflow definition yaml with workflows'
    )
    parser.add_argument(
        '-c', '--config',
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
    parser.set_defaults(func=add_workflows)

    return parser


def add_workflows(args, other_args, subparser=None):
    """
    Add GeneFlow workflows to database.

    Args:
        args.workflow_yaml: GeneFlow definition with workflows.
        args.config: GeneFlow config file path.
        args.environment: Config environment.

    Returns:
        On success: True.
        On failure: False.

    """
    workflow_yaml = args.workflow_yaml
    config = args.config
    environment = args.environment

    # load config file
    cfg = Config()
    if not cfg.load(config):
        Log.an().error('cannot load config file: %s', config)
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

    # import workflow
    defs = data_source.import_workflows_from_def(workflow_yaml)
    if not defs:
        Log.an().error('workflow definition load failed: %s', workflow_yaml)
        return False

    data_source.commit()

    # display new IDs
    for workflow in defs:
        Log.some().info(
            'workflow loaded: %s -> %s', workflow, defs[workflow]
        )

    return True
