"""This module contains methods for the install-workflow CLI command."""


from pathlib import Path
import yaml

from geneflow.config import Config
from geneflow.log import Log
from geneflow.workflow_installer import WorkflowInstaller


def init_subparser(subparsers):
    """
    Initialize argument sub-parser for install-workflow sub-command.

    Args:
        subparsers: list of argparse subparsers

    Returns:
        None

    """
    parser = subparsers.add_parser(
        'install-workflow', help='install workflow'
    )
    parser.add_argument(
        'workflow_path',
        type=str,
        help='GeneFlow workflow package path'
    )
    parser.add_argument(
        '-g', '--git',
        type=str,
        required=False,
        default=None,
        help='URL of git repo from which to clone workflow'
    )
    parser.add_argument(
        '--git_branch',
        type=str,
        required=False,
        default=None,
        help='git tag or branch to clone'
    )
    parser.add_argument(
        '-f', '--force', action='store_true',
        required=False,
        help='Overwrite existing workflow folder'
    )
    parser.add_argument(
        '-n', '--name',
        type=str,
        required=False,
        default=None,
        help='Name of app to install. If omitted, all apps are installed'
    )
    parser.add_argument(
        '-a', '--asset',
        type=str,
        required=False,
        default=None,
        help=(
            'Package asset type to install '
            '(package, singularity, build-package, build-singularity, none)'
        )
    )
    parser.add_argument(
        '-p', '--prefix',
        type=str,
        required=False,
        default=None,
        help='Package or container prefix for copy installs'
    )
    parser.add_argument(
        '-c', '--clean', action='store_true',
        required=False,
        help='Clean apps folder before install'
    )
    parser.set_defaults(clean=False)
    parser.add_argument(
        '--make_apps', action='store_true',
        required=False,
        default=None,
        help='Auto-generate app files during install'
    )
    parser.set_defaults(make_apps=False)
    parser.add_argument(
        '--config',
        type=str,
        required=False,
        default=None,
        help='GeneFlow config file with agave connection information'
    )
    parser.add_argument(
        '-e', '--environment',
        type=str,
        required=False,
        default=None,
        help='config environment'
    )
    parser.add_argument(
        '--agave_params',
        type=str,
        required=False,
        default=None,
        help='Agave params file for registration'
    )
    parser.add_argument(
        '--agave_username',
        type=str,
        required=False,
        default=None,
        help='Agave username to impersonate'
    )
    parser.add_argument(
        '--agave_apps_prefix',
        type=str,
        required=False,
        default=None,
        help='App name prefix for Agave registration'
    )
    parser.add_argument(
        '--agave_execution_system',
        type=str,
        required=False,
        default=None,
        help='Execution system for Agave registration'
    )
    parser.add_argument(
        '--agave_deployment_system',
        type=str,
        required=False,
        default=None,
        help='Deployment system for Agave registration'
    )
    parser.add_argument(
        '--agave_apps_dir',
        type=str,
        required=False,
        default=None,
        help='Apps directory for Agave registration'
    )
    parser.add_argument(
        '--agave_test_data_dir',
        type=str,
        required=False,
        default=None,
        help='Test data directory for Agave registration'
    )
    parser.add_argument(
        '--agave_publish', action='store_true',
        required=False,
        help='Publish Agave app'
    )
    parser.add_argument(
        '--agave_test_data', action='store_true',
        required=False,
        help='Upload Agave test data'
    )
    parser.set_defaults(agave_publish=False)
    parser.set_defaults(agave_test_data=False)
    parser.set_defaults(func=install_workflow)


def install_workflow(args):
    """
    Install a GeneFlow workflow.

    Args:
        args: contains all command-line arguments.

    Returns:
        On success: True.
        On failure: False.

    """
    # load config if specified
    config_dict = None
    cfg = Config()
    if args.config:
        if not args.environment:
            Log.an().error(
                'must specify environment if specifying a config file'
            )
            return False

        if not cfg.load(Path(args.config).resolve()):
            Log.an().error('cannot load config file: %s', args.config)
            return False

        config_dict = cfg.config(args.environment)
        if not config_dict:
            Log.an().error('invalid config environment: %s', args.environment)
            return False

    else:
        # load default config
        cfg.default('database.db')
        config_dict = cfg.config('local')

    # load agave params if specified
    agave_params = {}
    if args.agave_params:
        try:
            with open(args.agave_params, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().error(
                'cannot read agave params file: %s [%s]',
                args.params,
                str(err)
            )
            return False

        try:
            agave_params = yaml.safe_load(yaml_data)
        except yaml.YAMLError as err:
            Log.an().error(
                'invalid yaml: %s [%s]', yaml_data, str(err)
            )
            return False

    if not agave_params.get('agave'):
        agave_params['agave'] = {}

    # override any agave_params keys with command line options
    if args.agave_apps_prefix:
        agave_params['agave']['appsPrefix'] = args.agave_apps_prefix
    if args.agave_execution_system:
        agave_params['agave']['executionSystem'] = args.agave_execution_system
    if args.agave_deployment_system:
        agave_params['agave']['deploymentSystem'] = args.agave_deployment_system
    if args.agave_apps_dir:
        agave_params['agave']['appsDir'] = args.agave_apps_dir
    if args.agave_test_data_dir:
        agave_params['agave']['testDataDir'] = args.agave_test_data_dir

    # initialize workflow installer object and install apps
    wf_installer = WorkflowInstaller(
        str(Path(args.workflow_path).resolve()),
        git=args.git,
        git_branch=args.git_branch,
        force=args.force,
        app_name=args.name,
        app_asset=args.asset,
        copy_prefix=args.prefix,
        clean=args.clean,
        config=config_dict,
        agave_params=agave_params,
        agave_username=args.agave_username,
        agave_publish=args.agave_publish,
        make_apps=args.make_apps
    )

    if not wf_installer.initialize():
        Log.an().error('cannot initialize workflow installer')
        return False

    if not wf_installer.install_apps():
        Log.an().error('cannot install workflow apps')
        return False

    if args.agave_test_data:
        if not wf_installer.upload_agave_test_data():
            Log.an().error('cannot upload agave test data')
            return False

    return True
