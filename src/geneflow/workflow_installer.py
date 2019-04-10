"""This module contains the GeneFlow Workflow installer class."""


import shutil
from pathlib import Path
import pprint
import yaml

try:
    from agavepy.agave import Agave
except ImportError: pass

from git import Repo
from git.exc import GitError
import requests

from geneflow.app_installer import AppInstaller
from geneflow.data_manager import DataManager
from geneflow.log import Log
from geneflow.template_compiler import TemplateCompiler
from geneflow.uri_parser import URIParser


requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


class WorkflowInstaller:
    """
    GeneFlow WorkflowInstaller class.

    The WorkflowInstaller class is used to download and install workflows
    from a GeneFlow git repo.
    """

    def __init__(
            self,
            path,
            git=None,
            git_branch=None,
            app_name=None,
            app_asset=None,
            copy_prefix='/apps/standalone',
            clean=False,
            config=None,
            agave_params=None,
            agave_username=None,
            agave_publish=False,
            make_apps=True
    ):
        """
        Initialize the GeneFlow WorkflowInstaller class.

        Args:
            self: class instance
            path: local path to the workflow package
            git: git repo to clone
            git_branch: branch or tag of git repo
            app_name: name of app to install
            app_asset: type of app assets to install
            copy_prefix: prefix for copy installs
            clean: delete apps folder before install?
            config: GeneFlow config dict that contains Agave client if needed
            agave_params: dict that contains agave parameters for
                app registration
            agave_username: agave username to impersonate when installing apps
            agave_publish: publish agave app?
            make_apps: compile app templates

        Returns:
            None

        """
        self._path = path
        self._git = git
        self._git_branch = git_branch
        self._app_name = app_name
        self._app_asset = app_asset
        self._copy_prefix = copy_prefix
        self._clean = clean
        self._make_apps = make_apps

        self._apps_repo_path = None
        self._apps_repo = None

        # agave-related member variables
        self._agave = None # agave connection
        self._config = config
        self._agave_params = agave_params
        self._agave_username = agave_username
        self._agave_publish = agave_publish


    def initialize(self):
        """
        Initialize the GeneFlow WorkflowInstaller class.

        Initialize the class by cloning the workflow, validating the
        structure, loading apps config, and connecting to agave.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # clone workflow
        if self._git:
            if not self._clone_workflow():
                Log.an().error('cannot clone workflow from %s', self._git)
                return False

        # validate workflow structure
        if not self._validate_workflow_package():
            Log.an().error('invalid workflow package at %s', self._path)
            return False

        # load apps-repo
        if not self._load_apps_repo():
            Log.an().error('cannot load apps repo')
            return False

        # connect to agave
        if self._config and self._agave_params:
            if self._config.get('agave') and self._agave_params.get('agave'):
                if not self._agave_connect():
                    Log.an().error('cannot connect to agave')
                    return False

        return True


    def _agave_connect(self):
        """
        Connect to Agave.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        agave_connection_type = self._config['agave'].get(
            'connection_type', 'impersonate'
        )

        if agave_connection_type == 'impersonate':

            if not self._agave_username:
                Log.an().error('agave username required if impersonating')
                return False

            self._agave = Agave(
                api_server=self._config['agave']['server'],
                username=self._config['agave']['username'],
                password=self._config['agave']['password'],
                token_username=self._agave_username,
                client_name=self._config['agave']['client'],
                api_key=self._config['agave']['key'],
                api_secret=self._config['agave']['secret'],
                verify=False
            )

        elif agave_connection_type == 'agave-cli':

            # get credentials from ~/.agave/current
            agave_clients = Agave._read_clients()
            agave_clients[0]['verify'] = False # don't verify ssl
            self._agave = Agave(**agave_clients[0])
            # when using agave-cli, token_username must be the same as the
            # stored creds in user's home directory, this can be different
            # from job username
            self._agave_username = agave_clients[0]['username']

        else:
            Log.an().error(
                'invalid agave connection type: %s', agave_connection_type
            )
            return False

        return True


    def _validate_workflow_package(self):

        package_path = Path(self._path)
        if not Path(package_path / 'workflow').is_dir():
            Log.an().error('missing "workflow" directory in workflow package')
            return False

        if not Path(package_path / 'workflow' / 'workflow.yaml').is_file():
            Log.an().error('missing workflow.yaml file in workflow package')
            return False

        self._apps_repo_path = str(
            Path(package_path / 'workflow' / 'apps-repo.yaml')
        )
        if not Path(self._apps_repo_path).is_file():
            Log.an().error('missing apps-repo.yaml file in workflow package')
            return False

        return True


    @classmethod
    def _yaml_to_dict(cls, path):

        # read yaml file
        try:
            with open(path, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().warning('cannot read yaml file: %s [%s]', path, str(err))
            return False

        # convert to dict
        try:
            yaml_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as err:
            Log.an().warning('invalid yaml file: %s [%s]', path, str(err))
            return False

        return yaml_dict


    def _load_apps_repo(self):

        # read yaml file
        self._apps_repo = self._yaml_to_dict(self._apps_repo_path)

        # empty dict?
        if not self._apps_repo:
            Log.an().error(
                'cannot load/parse apps repo file: %s', self._apps_repo_path
            )
            return False

        # make sure it's a list with at least 1 app
        if not self._apps_repo.get('apps'):
            Log.an().error(
                'apps repo must have an "apps" section with at least one app'
            )
            return False

        return True


    def _clone_workflow(self):

        if not self._git:
            Log.an().error('must specify a git url to clone workflow')
            return False

        try:
            if self._git_branch:
                Repo.clone_from(
                    self._git, self._path, branch=self._git_branch,
                    config='http.sslVerify=false'
                )
            else:
                Repo.clone_from(
                    self._git, self._path,
                    config='http.sslVerify=false'
                )

        except GitError as err:
            Log.an().error(
                'cannot clone git repo: %s [%s]', self._git, str(err)
            )
            return False

        return True


    def install_apps(self):
        """
        Install apps for the workflow package.

        Args:
            self: class instance.

        Returns:
            None

        """
        apps_path = Path(self._path) / 'workflow' / 'apps'
        if self._clean:
            # remove apps folder
            if apps_path.is_dir():
                shutil.rmtree(str(apps_path))

        # create apps folder if not already there
        apps_path.mkdir(exist_ok=True)

        for app in self._apps_repo['apps']:
            if self._app_name == app['name'] or not self._app_name:

                Log.some().info('app:\n%s', pprint.pformat(app))

                repo_path = apps_path / app['folder']

                # create AppInstaller instance
                app_installer = AppInstaller(
                    str(repo_path),
                    app,
                    self._app_asset,
                    self._copy_prefix
                )

                # clone app into install location
                if not app_installer.clone_git_repo():
                    Log.an().error('cannot clone app to %s', str(repo_path))
                    # skip app
                    continue

                if not app_installer.load_config():
                    Log.an().error('cannot load app config.yaml')
                    # skip app
                    continue

                if self._make_apps:
                    if not app_installer.make():
                        Log.an().error('cannot compile app templates')
                        # skip app
                        continue

                if not app_installer.install_assets():
                    Log.an().error('cannot install app assets')
                    # skip app
                    continue

                # register in Agave
                if (
                        self._agave
                        and self._agave_params
                        and self._agave_params.get('agave')
                ):
                    register_result = app_installer.register_agave_app(
                        self._agave,
                        self._config['agave'],
                        self._agave_params,
                        self._agave_publish
                    )
                    if not register_result:
                        Log.a().warning(
                            'cannot register app "%s" in agave', app['name']
                        )
                        # skip app
                        continue

                    Log.some().info(
                        'registered agave app:\n%s',
                        pprint.pformat(register_result)
                    )

                    # compile jinja template for published app definition
                    if not TemplateCompiler.compile_template(
                            repo_path,
                            'app.yaml.j2',
                            repo_path / 'app.yaml',
                            agave=self._agave_params['agave'],
                            version=register_result['version'],
                            revision=register_result['revision']
                    ):
                        Log.a().warning(
                            'cannot compile app "%s" definition from template',
                            app['name']
                        )
                        # skip app
                        continue

                else:

                    # compile jinja template for app definition
                    if not TemplateCompiler.compile_template(
                            repo_path, 'app.yaml.j2', repo_path / 'app.yaml'
                    ):
                        Log.a().warning(
                            'cannot compile app "%s" definition from template',
                            app['name']
                        )
                        # skip app
                        continue

        return True


    def upload_agave_test_data(self):
        """
        Upload Agave test data from workflow package.

        Args:
            self: class instance.

        Returns:
            None

        """
        if (
                not self._agave
                or not self._agave_params
                or not self._agave_params.get('agave')
        ):
            Log.a().warning('must provide agave parameters to upload test data')
            return False

        # create main test data URI
        parsed_base_test_uri = URIParser.parse(
            'agave://{}/{}'.format(
                self._agave_params['agave']['deploymentSystem'],
                self._agave_params['agave']['testDataDir']
            )
        )
        Log.some().info(
            'creating base test data uri: %s',
            parsed_base_test_uri['chopped_uri']
        )
        if not DataManager.mkdir(
                parsed_uri=parsed_base_test_uri,
                recursive=True,
                agave={
                    'agave': self._agave,
                    'agave_config': self._config['agave']
                }
        ):
            Log.a().warning(
                'cannot create base test data uri: %s',
                parsed_base_test_uri['chopped_uri']
            )
            return False

        # upload test data
        parsed_local_test_uri = URIParser.parse(str(Path(self._path) / 'data'))
        parsed_agave_test_uri = URIParser.parse(
            '{}/{}'.format(
                parsed_base_test_uri['chopped_uri'],
                Path(self._path).name
            )
        )
        Log.some().info(
            'copying test data from %s to %s',
            parsed_local_test_uri['chopped_uri'],
            parsed_agave_test_uri['chopped_uri']
        )
        if not DataManager.copy(
                parsed_src_uri=parsed_local_test_uri,
                parsed_dest_uri=parsed_agave_test_uri,
                local={},
                agave={
                    'agave': self._agave,
                    'agave_config': self._config['agave']
                }
        ):
            Log.a().warning(
                'cannot copy test data from %s to %s',
                parsed_local_test_uri['chopped_uri'],
                parsed_agave_test_uri['chopped_uri']
            )
            return False

        return True
