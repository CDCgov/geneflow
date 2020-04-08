"""This module contains methods for the init-db CLI command."""


from geneflow.config import Config
from geneflow.environment import Environment
from geneflow.log import Log


def init_subparser(subparsers):
    """Initialize the init-db CLI subparser."""
    parser = subparsers.add_parser(
        'init-db', help='initialize database'
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
    parser.set_defaults(func=init_db)

    return parser


def init_db(args, other_args, subparser=None):
    """
    Initialize SQLite DB schema.

    Args:
        args.config: GeneFlow config file path.
        args.environment: Config environment.

    Returns:
        On success: True.
        On failure: False.

    """
    config = args.config
    environment = args.environment

    cfg = Config()
    if not cfg.load(config):
        Log.an().error('cannot load config file: %s', config)
        return False

    config_dict = cfg.config(environment)
    if not config_dict:
        Log.an().error('invalid config environment: %s', environment)
        return False

    if config_dict['database']['type'] != 'sqlite':
        Log.an().error('only sqlite databases can be initialized')
        return False

    if not Environment.init_sqlite_db(config_dict['database']['path']):
        Log.an().error(
            'cannot initialize sqlite database: %s',
            config_dict['database']['path']
        )
        return False

    return True
