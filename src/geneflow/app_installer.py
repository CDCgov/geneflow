"""This module contains the GeneFlow App Installer class."""


from pathlib import Path
import pprint
import cerberus
import shutil
from git import Repo
from git.exc import GitError
import yaml

from geneflow.data_manager import DataManager
from geneflow.log import Log
from geneflow.shell_wrapper import ShellWrapper
from geneflow.template_compiler import TemplateCompiler
from geneflow.uri_parser import URIParser
from geneflow.extend.agave_wrapper import AgaveWrapper

GF_VERSION = 'v1.0'

CONFIG_SCHEMA = {
    'v1.0': {
        'name': {'type': 'string', 'required': True},
        'description': {'type': 'string', 'maxlength': 64, 'required': True},
        'repo_uri': {'type': 'string', 'default': ''},
        'version': {'type': 'string', 'required': True},
        'inputs': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': ['File', 'Directory', 'Any']
                    },
                    'default': {'type': 'string', 'nullable': True},
                    'script_default': {'type': 'string', 'nullable': True},
                    'required': {'type': 'boolean', 'required': True},
                    'test_value': {'type': 'string', 'nullable': True},
                    'post_exec': {
                        'type': 'list',
                        'schema': {'type': 'dict'},
                        'nullable': True
                    }
                }
            }
        },
        'parameters': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': [
                            'File', 'Directory', 'string', 'int',
                            'float', 'double', 'long', 'Any'
                        ]
                    },
                    'default': {'nullable': True, 'default': None},
                    'required': {'type': 'boolean', 'required': True},
                    'test_value': {'nullable': True},
                    'post_exec': {
                        'type': 'list',
                        'schema': {'type': 'dict'},
                        'nullable': True
                    }
                }
            }
        },
        'default_exec_method': {'type': 'string', 'default': 'auto'},
        'pre_exec': {'type': 'list', 'default': []},
        'exec_methods': {'type': 'list', 'default': []},
        'post_exec': {'type': 'list', 'default': []},
        'default_asset': {'type': 'string', 'default': 'singularity'},
        'assets': {'type': 'dict', 'default': {}}
    }
}


class AppInstaller:
    """
    GeneFlow AppInstaller class.

    The AppInstaller class is used to download, generate, and install apps
    from a GeneFlow git repo.
    """

    def __init__(
            self,
            path,
            app,
            app_asset=None,
            copy_prefix='/apps/standalone'
    ):
        """
        Initialize the GeneFlow AppInstaller class.

        Args:
            self: class instance
            path: local path to the app package
            app: app information (git repo, tag, folder)

        Returns:
            None

        """
        self._path = Path(path)
        self._app = app
        self._app_asset = app_asset
        self._copy_prefix = copy_prefix

        # config file, which should be in the root of the app package
        self._config = None


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


    def clone_git_repo(self):
        """
        Clone app from git repo.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        # remove app folder if it exists
        if self._path.is_dir():
            shutil.rmtree(str(self._path))

        # recreate app folder
        self._path.mkdir()

        # clone app's git repo into target location
        try:
            if self._app['tag']:
                Repo.clone_from(
                    self._app['repo'], str(self._path), branch=self._app['tag'],
                    config='http.sslVerify=false'
                )
            else:
                Repo.clone_from(
                    self._app['repo'], str(self._path),
                    config='http.sslVerify=false'
                )
        except GitError as err:
            Log.an().error(
                'cannot clone app git repo: %s [%s]',
                self._app['repo'], str(err)
            )
            return False

        return True


    def load_config(self):
        """
        Load app config.yaml file.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        # read yaml file
        self._config = self._yaml_to_dict(
            str(Path(self._path / 'config.yaml'))
        )

        # empty dict?
        if not self._config:
            Log.an().error(
                'cannot load/parse config.yaml file in app: %s', self._path
            )
            return False

        validator = cerberus.Validator(allow_unknown=False)
        valid_def = validator.validated(
            self._config,
            CONFIG_SCHEMA[GF_VERSION]
        )

        if not valid_def:
            Log.an().error(
                'app config validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        return True


    def make(self):
        """
        Generate GeneFlow app files from templates.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        if not self.make_def():
            return False
        if not self.make_agave():
            return False
        if not self.make_wrapper():
            return False
        if not self.make_test():
            return False

        return True


    def make_def(self):
        """
        Generate the GeneFlow app definition.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        Log.some().info('compiling %s', str(self._path / 'app.yaml.j2'))

        if not TemplateCompiler.compile_template(
                None,
                'app.yaml.j2.j2',
                str(self._path / 'app.yaml.j2'),
                **self._config
        ):
            Log.an().error('cannot compile GeneFlow app definition template')
            return False

        return True


    def make_agave(self):
        """
        Generate the GeneFlow Agave app definition.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        Log.some().info('compiling %s', str(self._path / 'agave-app-def.json.j2'))

        if not TemplateCompiler.compile_template(
                None,
                'agave-app-def.json.j2.j2',
                str(self._path / 'agave-app-def.json.j2'),
                **self._config
        ):
            Log.an().error('cannot compile GeneFlow Agave app definition template')
            return False

        return True


    def make_wrapper(self):
        """
        Generate the GeneFlow app wrapper script.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # make assets folder, if it doesn't already exist
        asset_path = Path(self._path / 'assets')
        asset_path.mkdir(exist_ok=True)

        Log.some().info(
            'compiling %s',
            str(asset_path / '{}.sh'.format(self._config['name']))
        )

        # compile jinja2 template
        if not TemplateCompiler.compile_template(
                None,
                'wrapper-script.sh.j2',
                str(asset_path / '{}.sh'.format(self._config['name'])),
                **self._config
        ):
            Log.an().error('cannot compile GeneFlow app wrapper script')
            return False

        return True


    def make_test(self):
        """
        Generate the GeneFlow app test script.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # make test folder, if it doesn't already exist
        test_path = Path(self._path / 'test')
        test_path.mkdir(exist_ok=True)

        Log.some().info('compiling %s', str(test_path / 'test.sh'))

        # compile jinja2 template
        if not TemplateCompiler.compile_template(
                None,
                'test.sh.j2',
                str(test_path / 'test.sh'),
                **self._config
        ):
            Log.an().error('cannot compile GeneFlow app test script')
            return False

        return True


    def _copy_asset(self, asset):
        """
        Copy app assets.

        Args:
            self: class instance
            asset: what to copy

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._copy_prefix:
            Log.a().warning(
                'copy prefix must be specified when copying app assets'
            )
            return False

        if not asset.get('dst'):
            Log.a().warning('asset dst required for app %s', self._app['name'])
            return False

        if not asset.get('src'):
            Log.a().warning('asset src required for app %s', self._app['name'])
            return False

        # create asset destination
        asset_path = Path(self._path / asset['dst'])
        asset_path.mkdir(exist_ok=True)

        if 'zip' in asset:
            # create a tar.gz of src
            cmd = 'tar -czf "{}" --directory="{}" .'.format(
                str(Path(asset_path / '{}.tar.gz'.format(asset['zip']))),
                str(Path(self._copy_prefix) / asset['src'])
            )
            Log.some().info('zipping: %s', cmd)
            cmd_result = ShellWrapper.invoke(cmd)
            if cmd_result is False:
                Log.a().warning('cannot zip asset src: %s', cmd)
                return False

            Log.some().info('tar stdout: %s', cmd_result)

        else:
            # move without creating tar.gz
            cmd = 'cp -R "{}" "{}"'.format(
                str(Path(self._copy_prefix) / asset['src']),
                str(asset_path)
            )
            Log.some().info('copying: %s', cmd)
            cmd_result = ShellWrapper.invoke(cmd)
            if cmd_result is False:
                Log.a().warning('cannot copy asset src: %s', cmd)
                return False

            Log.some().info('copy stdout: %s', cmd_result)

        return True


    def _build_asset(self, asset):
        """
        Build app assets.

        Args:
            self: class instance
            asset: what to build

        Returns:
            On success: True.
            On failure: False.

        """
        # make sure the build path exists
        build_path = self._path / 'build'
        build_path.mkdir(exist_ok=True)

        build_repo_path = None
        if not asset.get('folder'):
            Log.a().warning(
                'repo folder must be set when specifying a build asset'
            )
            return False

        # clone build repo
        build_repo_path = build_path / asset['folder']

        if asset.get('repo'):
            # if repo is set, clone and build it
            try:
                if asset.get('tag'):
                    Repo.clone_from(
                        asset['repo'], str(build_repo_path),
                        branch=asset['tag'], config='http.sslVerify=false'
                    )
                else:
                    Repo.clone_from(
                        asset['repo'], str(build_repo_path),
                        config='http.sslVerify=false'
                    )
            except GitError as err:
                Log.an().error(
                    'cannot clone git repo for build: %s [%s]',
                    asset['repo'], str(err)
                )
                return False

        # if repo is not set, packaged build scripts are included with the
        # workflow in the build_repo_path

        # build
        cmd = 'make -C "{}"'.format(str(build_repo_path))
        Log.some().info('build command: %s', cmd)
        cmd_result = ShellWrapper.invoke(cmd)
        if cmd_result is False:
            Log.a().warning('cannot build app: %s', cmd)
            return False

        Log.some().info('make stdout: %s', cmd_result)

        # move built assets
        # make sure asset folder exists
        if not asset.get('dst'):
            Log.a().warning('asset dst required for app %s', self._app['name'])
            return False

        if not asset.get('src'):
            Log.a().warning('asset src required for app %s', self._app['name'])
            return False

        # create asset destination
        asset_path = self._path / asset['dst']
        asset_path.mkdir(exist_ok=True)

        # set src path
        src_path = self._path / asset['src']

        if 'zip' in asset:
            # create a tar.gz of src
            cmd = 'tar -czf "{}" --directory="{}" .'.format(
                str(asset_path / '{}.tar.gz'.format(asset['zip'])),
                str(src_path)
            )
            Log.some().info('zipping: %s', cmd)
            cmd_result = ShellWrapper.invoke(cmd)
            if cmd_result is False:
                Log.a().warning('cannot zip asset src: %s', cmd)
                return False

            Log.some().info('tar stdout: %s', cmd_result)

        else:
            # move without creating tar.gz
            cmd = 'mv "{}" "{}"'.format(str(src_path), str(asset_path))
            Log.some().info('moving: %s', cmd)
            cmd_result = ShellWrapper.invoke(cmd)
            if cmd_result is False:
                Log.a().warning('cannot move asset src: %s', cmd)
                return False

            Log.some().info('mv stdout: %s', cmd_result)

        return True


    def install_assets(self):
        """
        Install app assets.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # set asset type
        default_asset = self._app_asset
        # if not set on CLI, use asset type specified in workflow apps-repo
        if not default_asset:
            default_asset = self._app.get('asset')
        # if not set in workflow apps-repo, use app default
        if not default_asset:
            default_asset = self._config.get('default_asset')

        Log.some().info('installing app asset type: %s', str(default_asset))
        if not default_asset:
            # no asset type specified, nothing left to do
            return True

        if 'assets' not in self._config:
            # app is not configured with any assets
            return True

        if default_asset not in self._config['assets']:
            # if asset type is not listed in config, display warning and
            # continue
            Log.a().warning(
                'unconfigured asset type specified: %s', str(default_asset)
            )
            return True

        assets = self._config['assets'][default_asset]

        # install all components for asset
        for asset in assets:
            Log.some().info('app asset:\n%s', pprint.pformat(asset))

            if 'type' not in asset:
                Log.a().warning('asset type missing for app "%s"', self._app['name'])
                continue

            if asset['type'] == 'copy':
                if not self._copy_asset(asset):
                    Log.a().warning(
                        'cannot copy assets for app "%s"', self._app['name']
                    )
                    continue

            elif asset['type'] == 'build':
                if not self._build_asset(asset):
                    Log.a().warning(
                        'cannot build assets for app "%s"', self._app['name']
                    )
                    continue

            else:
                Log.a().warning(
                    'invalid asset type "%s" for app "%s"',
                    asset['type'], self._app['name']
                )

        return True


    def register_agave_app(self, agave_wrapper, agave_params, agave_publish):
        """
        Register app in Agave.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        Log.some().info('registering agave app %s', str(self._path))
        Log.some().info('app version: %s', self._config['version'])

        # compile agave app template
        if not TemplateCompiler.compile_template(
                self._path,
                'agave-app-def.json.j2',
                self._path / 'agave-app-def.json',
                version=self._config['version'],
                agave=agave_params['agave']
        ):
            Log.a().warning(
                'cannot compile agave app "%s" definition from template',
                self._app['name']
            )
            return False

        # create main apps URI
        parsed_agave_apps_uri = URIParser.parse(
            'agave://{}/{}'.format(
                agave_params['agave']['deploymentSystem'],
                agave_params['agave']['appsDir']
            )
        )
        Log.some().info(
            'creating main apps uri: %s',
            parsed_agave_apps_uri['chopped_uri']
        )
        if not DataManager.mkdir(
                parsed_uri=parsed_agave_apps_uri,
                recursive=True,
                agave={
                    'agave_wrapper': agave_wrapper
                }
        ):
            Log.a().warning('cannot create main agave apps uri')
            return False

        # delete app uri if it exists
        parsed_app_uri = URIParser.parse(
            'agave://{}/{}/{}'.format(
                agave_params['agave']['deploymentSystem'],
                agave_params['agave']['appsDir'],
                self._app['folder']
            )
        )
        Log.some().info(
            'deleting app uri if it exists: %s',
            parsed_app_uri['chopped_uri']
        )
        if not DataManager.delete(
                parsed_uri=parsed_app_uri,
                agave={
                    'agave_wrapper': agave_wrapper
                }
        ):
            # log warning, but ignore.. deleting non-existant uri returns False
            Log.a().warning(
                'cannot delete app uri: %s', parsed_app_uri['chopped_uri']
            )

        # upload app assets
        parsed_assets_uri = URIParser.parse(str(self._path / 'assets'))
        Log.some().info(
            'copying app assets from %s to %s',
            parsed_assets_uri['chopped_uri'],
            parsed_app_uri['chopped_uri']
        )

        if not DataManager.copy(
                parsed_src_uri=parsed_assets_uri,
                parsed_dest_uri=parsed_app_uri,
                local={},
                agave={
                    'agave_wrapper': agave_wrapper
                }
        ):
            Log.a().warning(
                'cannot copy app assets from %s to %s',
                parsed_assets_uri['chopped_uri'],
                parsed_app_uri['chopped_uri']
            )
            return False

        # upload test script
        parsed_test_uri = URIParser.parse(
            '{}/{}'.format(
                parsed_app_uri['chopped_uri'],
                'test'
            )
        )
        Log.some().info(
            'creating test uri: %s', parsed_test_uri['chopped_uri']
        )
        if not DataManager.mkdir(
                parsed_uri=parsed_test_uri,
                recursive=True,
                agave={
                    'agave_wrapper': agave_wrapper
                }
        ):
            Log.a().warning(
                'cannot create test uri: %s', parsed_test_uri['chopped_uri']
            )
            return False

        parsed_local_test_script = URIParser.parse(
            str(self._path / 'test' / 'test.sh')
        )
        parsed_agave_test_script = URIParser.parse(
            '{}/{}'.format(parsed_test_uri['chopped_uri'], 'test.sh')
        )
        Log.some().info(
            'copying test script from %s to %s',
            parsed_local_test_script['chopped_uri'],
            parsed_agave_test_script['chopped_uri']
        )
        if not DataManager.copy(
                parsed_src_uri=parsed_local_test_script,
                parsed_dest_uri=parsed_agave_test_script,
                local={},
                agave={
                    'agave_wrapper': agave_wrapper
                }
        ):
            Log.a().warning(
                'cannot copy test script from %s to %s',
                parsed_local_test_script['chopped_uri'],
                parsed_agave_test_script['chopped_uri']
            )
            return False

        # update existing app, or register new app
        Log.some().info('registering agave app')

        app_definition = self._yaml_to_dict(
            str(self._path / 'agave-app-def.json')
        )
        if not app_definition:
            Log.a().warning(
                'cannot load agave app definition: %s',
                str(self._path / 'agave-app-def.json')
            )
            return False

        app_add_result = agave_wrapper.apps_add_update(app_definition)
        if not app_add_result:
            Log.a().warning(
                'cannot register agave app:\n%s', pprint.pformat(app_definition)
            )
            return False

        register_result = {}

        # publish app
        if agave_publish:
            Log.some().info('publishing agave app')

            app_publish_result = agave_wrapper.apps_publish(app_add_result['id'])
            if not app_publish_result:
                Log.a().warning(
                    'cannot publish agave app: %s', app_add_result['id']
                )
                return False

            # return published id and revision
            register_result = {
                'id': app_publish_result['id'],
                'version': self._config['version'],
                'revision': 'u{}'.format(app_publish_result['revision'])
            }

        else:
            # return un-published id and blank revision
            register_result = {
                'id': app_add_result['id'],
                'version': self._config['version'],
                'revision': ''
            }

        return register_result
