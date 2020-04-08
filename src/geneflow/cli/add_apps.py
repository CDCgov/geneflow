"""This module contains methods for the add-apps CLI command."""


from geneflow.config import Config
from geneflow.data import DataSource, DataSourceException
from geneflow.log import Log


def init_subparser(subparsers):
    """Initialize the add-apps CLI subparser."""
    parser = subparsers.add_parser(
        'add-apps', help='add apps to database'
    )
    parser.add_argument(
        'app_yaml',
        type=str,
        help='geneflow definition yaml with apps'
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
    parser.set_defaults(func=add_apps)

    return parser


def add_apps(args, other_args, subparser=None):
    """
    Add GeneFlow apps to database.

    Args:
        args.app_yaml: GeneFlow definition with apps.
        args.config_file: GeneFlow config file path.
        args.environment: Config environment.

    Returns:
        On success: True.
        On failure: False.

    """
    app_yaml = args.app_yaml
    config_file = args.config_file
    environment = args.environment

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

    # import apps
    defs = data_source.import_apps_from_def(app_yaml)
    if not defs:
        Log.an().error('app definition load failed: %s', app_yaml)
        return False

    data_source.commit()

    # display new IDs
    for app in defs:
        Log.some().info(
            'app loaded: %s -> %s', app, defs[app]
        )

    return True
