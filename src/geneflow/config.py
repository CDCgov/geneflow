"""This module contains the GeneFlow Config class."""

import pprint
import cerberus
import yaml

from geneflow.log import Log

GF_VERSION = 'v1.0'

CONFIG_MAIN_SCHEMA = {
    GF_VERSION: {
        'gfVersion': {
            'type': 'string', 'default': GF_VERSION, 'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string', 'default': 'config', 'allowed': ['config']
        }
    }
}

ENV_SCHEMA = {
    GF_VERSION: {
        'run_poll_delay': {'type': 'integer', 'default': 2},
        'database': {
            'type': 'dict',
            'default': {
                'type': 'sqlite',
                'path': 'database.db'
            }
        },
        'agave': {
            'type': 'dict',
            'default': {
                'connection_type': 'agave-cli'
            }
        }
    }
}

DATABASE_SCHEMA = {
    GF_VERSION: {
        'sqlite': {
            'type': {'type': 'string', 'required': True, 'allowed': ['sqlite']},
            'path': {'type': 'string', 'required': True}
        },
        'mysql': {
            'type': {'type': 'string', 'required': True, 'allowed': ['mysql']},
            'host': {'type': 'string', 'required': True},
            'database': {'type': 'string', 'required': True},
            'user': {'type': 'string', 'required': True},
            'password': {'type': 'string', 'required': True}
        }
    }
}

AGAVE_SCHEMA = {
    GF_VERSION: {
        'impersonate': {
            'connection_type': {
                'type': 'string',
                'required': True,
                'allowed': ['impersonate']
            },
            'client': {'type': 'string', 'required': True},
            'key': {'type': 'string', 'required': True},
            'secret': {'type': 'string', 'required': True},
            'server': {'type': 'string', 'required': True},
            'username': {'type': 'string', 'required': True},
            'password': {'type': 'string', 'required': True},
            'token_username': {'type': 'string'},
            'retry': {'type': 'integer', 'default': 5},
            'retry_delay': {'type': 'integer', 'default': 3},
            'token_retry': {'type': 'integer', 'default': 3},
            'token_retry_delay': {'type': 'integer', 'default': 1},
            'mkdir_retry': {'type': 'integer', 'default': 3},
            'mkdir_retry_delay': {'type': 'integer', 'default': 5},
            'import_retry': {'type': 'integer', 'default': 3},
            'import_retry_delay': {'type': 'integer', 'default': 5},
            'job_submit_retry': {'type': 'integer', 'default': 5},
            'job_submit_retry_delay': {'type': 'integer', 'default': 5},
            'job_retry': {'type': 'integer', 'default': 3},
            'files_list_retry': {'type': 'integer', 'default': 5},
            'files_list_retry_delay': {'type': 'integer', 'default': 5},
            'files_delete_retry': {'type': 'integer', 'default': 3},
            'files_delete_retry_delay': {'type': 'integer', 'default': 1}
        },
        'agave-cli': {
            'connection_type': {
                'type': 'string',
                'required': True,
                'allowed': ['agave-cli']
            },
            'retry': {'type': 'integer', 'default': 5},
            'retry_delay': {'type': 'integer', 'default': 3},
            'token_retry': {'type': 'integer', 'default': 3},
            'token_retry_delay': {'type': 'integer', 'default': 1},
            'mkdir_retry': {'type': 'integer', 'default': 3},
            'mkdir_retry_delay': {'type': 'integer', 'default': 5},
            'import_retry': {'type': 'integer', 'default': 3},
            'import_retry_delay': {'type': 'integer', 'default': 5},
            'job_submit_retry': {'type': 'integer', 'default': 5},
            'job_submit_retry_delay': {'type': 'integer', 'default': 5},
            'job_retry': {'type': 'integer', 'default': 3},
            'files_list_retry': {'type': 'integer', 'default': 5},
            'files_list_retry_delay': {'type': 'integer', 'default': 5},
            'files_delete_retry': {'type': 'integer', 'default': 3},
            'files_delete_retry_delay': {'type': 'integer', 'default': 1}
        }
    }
}


class Config:
    """
    GeneFlow Config class.

    Config stores information about the database, Agave connection, and
    end-point access. It also validates config definitions.

    """

    def __init__(self):
        """Initialize class."""
        self._config = None


    def __repr__(self):
        """Return string representation of Config class."""
        str_repr = (
            "Config class:"
            "\n\t{}"
        ).format(str(self._config))

        return str_repr


    def load(self, config_file):
        """
        Load and validate GeneFlow config file.

        Args:
            config_file: Config file containing GeneFlow settings.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            with open(config_file, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().error(
                'cannot read yaml file: %s [%s]', config_file, str(err)
            )
            return False

        try:
            yaml_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as err:
            Log.an().error('invalid yaml: %s [%s]', config_file, str(err))
            return False

        if not yaml_dict:
            Log.an().error('cannot load/parse config file: %s', config_file)
            return False

        self._config = Config.validate(yaml_dict)
        if not self._config:
            Log.an().error('invalid geneflow config file: %s', config_file)
            return False

        return True


    @staticmethod
    def validate(config_def):
        """
        Validate config schema.

        Args:
            config_def: dict of config to validate.

        Returns:
            On success: validated/normalized config dict.
            On failure: False.

        """
        # validate main schema
        validator = cerberus.Validator(allow_unknown=True)
        valid_def = validator.validated(
            config_def,
            CONFIG_MAIN_SCHEMA[GF_VERSION]
        )

        if not valid_def:
            Log.an().error(
                'config validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        for env in valid_def:
            if env not in ['gfVersion', 'class']:

                # validate environment section
                valid_env_def = validator.validated(
                    valid_def[env],
                    ENV_SCHEMA[GF_VERSION]
                )

                if not valid_env_def:
                    Log.an().error(
                        'config environment validation error: env=%s\n%s',
                        env,
                        pprint.pformat(validator.errors)
                    )
                    return False

                valid_def[env] = valid_env_def

                # validate database section
                if valid_def[env]['database']['type']\
                        not in ['sqlite', 'mysql']:
                    Log.an().error(
                        'invalid database type "%s" in environment "%s"',
                        valid_def[env]['database']['type'],
                        env
                    )
                    return False

                valid_db_def = validator.validated(
                    valid_def[env]['database'],
                    DATABASE_SCHEMA[GF_VERSION][
                        valid_def[env]['database']['type']
                    ]
                )

                if not valid_db_def:
                    Log.an().error(
                        'config database validation error: env=%s\n%s',
                        env,
                        pprint.pformat(validator.errors)
                    )
                    return False

                valid_def[env]['database'] = valid_db_def

                # validate agave section
                if valid_def[env]['agave']['connection_type']\
                        not in ['impersonate', 'agave-cli']:
                    Log.an().error(
                        'invalid agave connection type "%s" in environment "%s"',
                        valid_def[env]['agave']['connection_type'],
                        env
                    )
                    return False

                valid_agave_def = validator.validated(
                    valid_def[env]['agave'],
                    AGAVE_SCHEMA[GF_VERSION][
                        valid_def[env]['agave']['connection_type']
                    ]
                )

                if not valid_agave_def:
                    Log.an().error(
                        'config agave validation error: env=%s\n%s',
                        env,
                        pprint.pformat(validator.errors)
                    )
                    return False

                valid_def[env]['agave'] = valid_agave_def

        return valid_def


    def config(self, env=None):
        """
        Config environment definition.

        Args:
            env: environment section to return, if None, return entire config.

        Returns:
            Dict of environment section or entire config. False if env doesn't
                exist in config.

        """
        if not env:
            return self._config

        if env not in self._config:
            Log.an().error('invalid config environment: %s', env)
            return False

        return self._config[env]


    def default(self, sqlite_path):
        """
        Load default config definition given sqlite path.

        Args:
            sqlite_path: path to SQLite DB.

        Returns:
            On success: True.
            On failure: False.

        """
        default_def = {
            'local': {
                'database': {
                    'type': 'sqlite',
                    'path': sqlite_path
                }
            }
        }

        valid_def = Config.validate(default_def)
        if not valid_def:
            Log.an().error('invalid default definition generated')
            return False

        self._config = valid_def

        return True


    def write(self, config_path):
        """
        Write current config to file.

        Args:
            config_path: file to write config.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            with open(config_path, 'w') as out_file:
                yaml.dump(self._config, out_file, default_flow_style=False)

        except IOError as err:
            Log.an().error(
                'cannot write yaml file to %s [%s]', config_path, str(err)
            )
            return False

        return True
