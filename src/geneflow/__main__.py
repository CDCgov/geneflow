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
        '--log_level',
        type=str,
        default='info',
        help='logging level'
    )
    parser.add_argument(
        '--log_file',
        type=str,
        default=None,
        help='log file'
    )

    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help='Functions')

    # configure arguments for sub-commands
    geneflow.cli.add_apps.init_subparser(subparsers)
    geneflow.cli.add_workflows.init_subparser(subparsers)
    geneflow.cli.help.init_subparser(subparsers)
    geneflow.cli.init_db.init_subparser(subparsers)
    geneflow.cli.install_workflow.init_subparser(subparsers)
    geneflow.cli.make_app.init_subparser(subparsers)
    geneflow.cli.migrate_db.init_subparser(subparsers)
    geneflow.cli.run.init_subparser(subparsers)
    geneflow.cli.run_pending.init_subparser(subparsers)

    # parse arguments
    args = parser.parse_args()
    if not args.func:
        parser.print_help()
        return False

    return args


def main():
    """
    Geneflow CLI main entrypoint.

    Args:
        None.

    Returns:
        Nothing.

    """
    args = parse_args()
    if not args:
        sys.exit(1)

    # configure logging
    Log.config(args.log_level, args.log_file)

    # call the appropriate command
    if not args.func(args):
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':

    main()
