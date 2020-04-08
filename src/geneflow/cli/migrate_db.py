"""Module containing GeneFlow migrate-db sub-command."""


from pathlib import Path
from yoyo import read_migrations, get_backend

from geneflow.config import Config
from geneflow.log import Log
from geneflow import GF_PACKAGE_PATH


def init_subparser(subparsers):
    """
    Initialize argument sub-parser for migrate-db sub-command.

    Args:
        subparsers: list of argument subparsers.

    Returns:
        None

    """
    parser = subparsers.add_parser(
        'migrate-db', help='migrate database'
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
    parser.set_defaults(func=migrate_db)

    return parser


def migrate_db(args, other_args, subparser=None):
    """
    Migrate SQL DB schema. Currently only works for MySQL databases.

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

    if config_dict['database']['type'] != 'mysql':
        Log.an().error('only mysql databases can be migrated')
        return False

    migrations_path = str(Path(GF_PACKAGE_PATH, 'data/migrations'))

    try:
        database = get_backend('{}://{}:{}@{}/{}'.format(
            config_dict['database']['type'],
            config_dict['database']['user'],
            config_dict['database']['password'],
            config_dict['database']['host'],
            config_dict['database']['database']
        ))
        migrations = read_migrations(migrations_path)
        with database.lock():
            database.apply_migrations(database.to_apply(migrations))
    except Exception as err:
        Log.an().error('cannot migrate database [%s]', str(err))
        return False

    return True
