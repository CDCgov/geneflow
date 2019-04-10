"""
GeneFlow Environment Class.

This module contains the GeneFlow Environment class, which sets up the
environment for running GeneFlow from the CLI.
"""

import os
from uuid import uuid1
from pathlib import Path
import sqlite3
import unittest

from geneflow.log import Log
from geneflow.uri_parser import URIParser
from geneflow.data_manager import DataManager
from geneflow import GF_PACKAGE_PATH


class Environment:
    """
    GeneFlow Environment Class.

    Setup the user enviroment, including directories for running the GeneFlow
    CLI:
    1) user's home directories
    2) enviroment paths for local workflow apps
    3) initialize database
    """

    def __init__(
            self,
            user_home='~',
            geneflow_base='.geneflow',
            session_id=None,
            workflow_path=None
    ):
        """
        Class object initialization with based on user name.

        Args:
            user_home: user home directory
            geneflow_base: geneflow base directory appended to user home
            session_id: randomly generated if not provided
            workflow_path: path to workflow definition

        Output:
            Environment class object.

        """
        # user home directory (or some other directory)
        self._user_home = user_home
        # geneflow base directory appended to user home
        self._geneflow_base = geneflow_base
        # session id, randomly generated if not provided
        self._session_id = session_id
        # path to workflow definition, which should be in the
        #   same folder as all apps that the workflow references
        self._workflow_path = workflow_path

        # working directories
        self._gf_home = None
        self._gf_tmp = None
        self._gf_log = None
        self._gf_work = None

        # config and db files
        self._config_path = None
        self._sqlite_db_path = None


    def initialize(self):
        """
        Initialize environment.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._init_user_home():
            Log.an().error('cannot initialize user home directory')
            return False

        if not self._init_dirs():
            Log.an().error(
                'cannot initialize geneflow directories in user home'
            )
            return False

        if not self._init_session():
            Log.an().error('cannot initialize geneflow session')
            return False

        if not self.init_sqlite_db(self._sqlite_db_path):
            Log.an().error('cannot initialize sqlite db')
            return False

        if not self._init_app_paths():
            Log.an().error('cannot initialize workflow app paths')
            return False

        return True


    def _init_user_home(self):
        """
        Initialize user home directory.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._user_home = str(Path(self._user_home).expanduser())
        except TypeError as err:
            Log.an().error(
                'invalid user home: %s [%s]', self._user_home, str(err)
            )
            return False

        if self._user_home == '~':
            Log.an().error('cannot expand user home')
            return False

        return True


    def _init_dirs(self):
        """
        Create .geneflow/tmp, .geneflow/log, and .geneflow/work directories.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._gf_home = str(Path(self._user_home)/self._geneflow_base)
            self._gf_tmp = str(Path(self._gf_home)/'tmp')
            self._gf_log = str(Path(self._gf_home)/'log')
            self._gf_work = str(Path(self._gf_home)/'work')
        except TypeError as err:
            Log.an().error(
                'invalid geneflow home (%s) or user home (%s) [%s]',
                self._gf_home, self._user_home, str(err)
            )
            return False

        for directory in [
                self._gf_home, self._gf_tmp, self._gf_log, self._gf_work
        ]:
            try:
                if not Path(directory).is_dir():
                    Path(directory).mkdir()

            except OSError as err:
                Log.an().error(
                    'cannot create directory: %s [%s]', directory, str(err)
                )
                return False

        return True


    def _init_session(self):
        """
        Set session id, sqlite db path, and config path.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._session_id:
            self._session_id = str(uuid1())

        try:
            self._sqlite_db_path\
                = str(Path(self._gf_tmp)/self._session_id)+'.db'
            self._config_path\
                = str(Path(self._gf_tmp)/self._session_id)+'.yaml'
        except TypeError as err:
            Log.an().error(
                'invalid geneflow tmp path: %s [%s]', self._gf_tmp, str(err)
            )
            return False

        return True


    @staticmethod
    def init_sqlite_db(sqlite_db_path):
        """
        Intialize the SQLite database.

        Args:
            None.

        Output:
            On success: True.
            On failure: False.

        """
        sqlite_sql_path = str(
            GF_PACKAGE_PATH / Path('data/sql/geneflow-sqlite.sql')
        )

        # create database
        try:
            dbh = sqlite3.connect(sqlite_db_path)

        except sqlite3.Error as err:
            Log.an().error(
                'cannot connect to sqlite db: %s [%s]', sqlite_db_path, str(err)
            )
            return False

        # initialize db structure
        try:
            cursor = dbh.cursor()
            with open(sqlite_sql_path, 'r') as sql_file:
                query = sql_file.read()
                cursor.executescript(query)
                sql_file.close()
            dbh.commit()

        except sqlite3.Error as err:
            Log.an().error(
                'cannot create sqlite db: %s [%s]', sqlite_db_path, str(err)
            )
            dbh.close()
            return False

        except FileNotFoundError as err:
            Log.an().error(
                'cannot load geneflow sql file: %s [%s]',
                sqlite_sql_path, str(err)
            )
            dbh.close()
            return False

        dbh.close()

        return True


    def _init_app_paths(self):
        """
        Add app paths to environment PATH for local workflows.

        The package path contains the workflow definition YAML file and shell
        scripts for calling individual apps used in a workflow.

        Args:
            None.

        Output:
            On success: True.
            On failure: False.

        """
        parsed_uri = URIParser.parse(self._workflow_path)
        if not parsed_uri:
            Log.an().error('invalid workflow path: %s', self._workflow_path)
            return False

        apps_uri = ('{}{}' if parsed_uri['folder'] == '/' else '{}/{}')\
            .format(parsed_uri['folder'], 'apps')
        parsed_apps_uri = URIParser.parse(
            ('{}{}' if parsed_uri['folder'] == '/' else '{}/{}')\
            .format(parsed_uri['folder'], 'apps')
        )
        if not parsed_apps_uri:
            Log.an().error('cannot construct apps uri: %s', apps_uri)
            return False

        if not DataManager.exists(parsed_uri=parsed_apps_uri):
            # no apps directory
            return True

        for app_dir in DataManager.list(parsed_uri=parsed_apps_uri):
            try:
                os.environ['PATH'] = '{}{}{}'.format(
                    os.path.join(
                        parsed_apps_uri['chopped_path'], app_dir, 'assets'
                    ),
                    os.pathsep,
                    os.environ['PATH']
                )

            except OSError as err:
                Log.an().error('workflow app pathmunge error [%s]', str(err))
                return False

        return True


    def __repr__(self):
        """Return string representation of the class object."""
        str_rep = (
            "Environment setting:"
            "\n\tUser Home: {}"
            "\n\tGeneFlow Base: {}"
            "\n\tSession ID: {}"
            "\n\tWorkflow Path: {}"
            "\n\tGeneFlow Home: {}"
            "\n\tGeneFlow Log: {}"
            "\n\tGeneFlow TMP: {}"
            "\n\tConfig Path: {}"
            "\n\tSQLite DB Path: {}"
        ).format(
            self._user_home,
            self._geneflow_base,
            self._session_id,
            self._workflow_path,
            self._gf_home,
            self._gf_tmp,
            self._gf_log,
            self._config_path,
            self._sqlite_db_path
        )

        return str_rep


    def get_config_path(self):
        """Return session config file path."""
        return self._config_path


    def get_sqlite_db_path(self):
        """Return session SQLite DB path."""
        return self._sqlite_db_path


    def get_log_dir(self):
        """Return session log directory."""
        return self._gf_log


if __name__ == '__main__':
    class TestEnvironment(unittest.TestCase):
        """Unittest."""

        def test_env(self):
            """Test environment class."""
            from pprint import pprint
            env = Environment(
                workflow_path='/sub/in/absolute/workflow/path'
            )
            self.assertTrue(env.initialize())
            pprint(str(env))
            pprint(os.environ['PATH'])

    unittest.main()
