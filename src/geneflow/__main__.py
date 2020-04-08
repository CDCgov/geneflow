#!/usr/bin/env python3
"""Command line interface for executing GeneFlow workflow."""

import sys
import argparse

import geneflow.cli.common
import geneflow.cli.add_apps
import geneflow.cli.add_workflows
import geneflow.cli.help
import geneflow.cli.init_db
import geneflow.cli.install_workflow
import geneflow.cli.make_app
import geneflow.cli.migrate_db
import geneflow.cli.run
import geneflow.cli.run_pending
from geneflow.log import Log
from geneflow import __version__


def parse_args():
    """
    Parse command line arguments.

    Args:
        None.

    Returns:
        Command line arguments.

    """
    parser = argparse.ArgumentParser(
        description='GeneFlow CLI',
        prog='GeneFlow'
    )

    # print version
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__)
    )

    # shared arguments
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        dest='log_level',
        help='logging level'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        dest='log_file',
        help='log file'
    )

    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help='Functions', dest='command')
    subparser_dict = {}

    # configure arguments for sub-commands
    subparser_dict['add-apps'] = geneflow.cli.add_apps.init_subparser(subparsers)
    subparser_dict['add-workflows'] = geneflow.cli.add_workflows.init_subparser(subparsers)
    subparser_dict['help'] = geneflow.cli.help.init_subparser(subparsers)
    subparser_dict['init-db'] = geneflow.cli.init_db.init_subparser(subparsers)
    subparser_dict['install-workflow'] = geneflow.cli.install_workflow.init_subparser(subparsers)
    subparser_dict['make-app'] = geneflow.cli.make_app.init_subparser(subparsers)
    subparser_dict['migrate-db'] = geneflow.cli.migrate_db.init_subparser(subparsers)
    subparser_dict['run'] = geneflow.cli.run.init_subparser(subparsers)
    subparser_dict['run-pending'] = geneflow.cli.run_pending.init_subparser(subparsers)

    # parse arguments
    args = parser.parse_known_args()
    if not args[0].func:
        parser.print_help()
        return False

    return args, subparser_dict[args[0].command]


def main():
    """
    Geneflow CLI main entrypoint.

    Args:
        None.

    Returns:
        Nothing.

    """
    args, subparser = parse_args()
    if not args:
        sys.exit(1)

    # configure logging
    Log.config(args[0].log_level, args[0].log_file)

    # display GeneFlo
    Log.some().info('GeneFlow %s', __version__)

    # call the appropriate command
    if not args[0].func(
            args=args[0],
            other_args=args[1],
            subparser=subparser
    ):
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':

    main()
