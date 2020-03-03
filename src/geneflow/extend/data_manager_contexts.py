"""
This module contains data management extension functions for various contexts.
"""

import glob
import os
import shutil

from geneflow.log import Log
from geneflow.uri_parser import URIParser
from geneflow.extend.agave_wrapper import AgaveWrapper


### Local data management functions and move/copy with Local as source

def _list_local(uri, local=None):
    """
    List contents of local URI.

    Args:
        uri: parsed URI to list.
        local: local context options.

    Returns:
        On success: a list of filenames (basenames only).
        On failure: False.

    """
    try:
        file_list = [
            os.path.basename(item) for item in glob.glob(
                uri['chopped_path']+'/*'
            )
        ]

    except OSError as err:
        Log.an().error(
            'cannot get file list for uri: %s [%s]',
            uri['chopped_uri'], str(err)
        )
        return False

    return file_list


def _exists_local(uri, local=None):
    """
    Check if local URI exists.

    Args:
        uri: parsed URI to check.
        local: local context options.

    Returns:
        True if the URI exists, False otherwise.

    """
    return os.path.exists(uri['chopped_path'])


def _mkdir_local(uri, local=None):
    """
    Create local directory specified by URI.

    Args:
        uri: parsed URI to create.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        os.makedirs(uri['chopped_path'])

    except OSError as err:
        Log.an().error(
            'cannot create uri: %s [%s]', uri['chopped_uri'], str(err)
        )
        return False

    return True


def _mkdir_recursive_local(uri, local=None):
    """
    Recursively create local directory specified by URI.

    Args:
        uri: parsed URI to create.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    # same as the non-recursive call
    return _mkdir_local(uri, local)


def _delete_local(uri, local=None):
    """
    Delete local file/folder specified by URI.

    Args:
        uri: parsed URI to delete.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        shutil.rmtree(uri['chopped_path'])

    except OSError as err:
        Log.an().error(
            'cannot delete uri: %s [%s]', uri['chopped_uri'], str(err)
        )
        return False

    return True


def _copy_local_local(src_uri, dest_uri, local=None):
    """
    Copy local data with system shell.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        shutil.copytree(
            src_uri['path'],
            dest_uri['path']
        )
    except OSError as err:
        Log.an().error(
            'cannot copy from %s to %s [%s]',
            src_uri['uri'],
            dest_uri['uri'],
            str(err)
        )
        return False

    return True


### Agave data management functions and move/copy with Agave as source

def _list_agave(uri, agave):
    """
    List contents of agave URI.

    Args:
        uri: parsed URI to list.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: a list of filenames (basenames only).
        On failure: False.

    """
    file_list = agave['agave_wrapper'].files_list(uri['authority'], uri['chopped_path'])

    if file_list is False:
        Log.an().error(
            'cannot get file list for uri: %s', uri['chopped_uri']
        )
        return False

    return [file['name'] for file in file_list]


def _exists_agave(uri, agave):
    """
    Check if agave URI exists.

    Args:
        uri: parsed URI to check.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        True if the URI exists, False if it doesn't or if there's an error.

    """
    if agave['agave_wrapper'].files_exist(uri['authority'], uri['chopped_path']) is False:
        return False

    return True


def _mkdir_agave(uri, agave):
    """
    Create agave directory specified by URI.

    Args:
        uri: parsed URI to create.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if not agave['agave_wrapper'].files_mkdir(uri['authority'], uri['folder'], uri['name']):
        Log.an().error(
            'cannot create folder at uri: %s', uri['chopped_uri']
        )
        return False

    return True


def _mkdir_recursive_agave(uri, agave):
    """
    Recursively create agave directory specified by URI.

    Args:
        uri: parsed URI to create.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if uri['folder'] != '/':

        # make sure parent folder exists first
        parent_uri = URIParser.parse(
            '{}://{}{}'.format(
                uri['scheme'], uri['authority'], uri['folder']
            )
        )
        if not _exists_agave(parent_uri, agave):
            # parent folder does not exist, create
            if not _mkdir_recursive_agave(parent_uri, agave):
                Log.an().error(
                    'cannot create parent folder at uri: %s',
                    parent_uri['chopped_uri']
                )
                return False

    return _mkdir_agave(uri, agave)


def _delete_agave(uri, agave):
    """
    Delete agave file/folder specified by URI.

    Args:
        uri: parsed URI to delete.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if not agave['agave_wrapper'].files_delete(uri['authority'], uri['chopped_path']):
        Log.an().error('cannot delete uri: %s', uri['chopped_path'])
        return False

    return True


def _copy_agave_agave(src_uri, dest_uri, agave):
    """
    Copy Agave data using AgavePy Wrapper.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if not agave['agave_wrapper'].files_import_from_agave(
            dest_uri['authority'],
            dest_uri['folder'],
            dest_uri['name'],
            src_uri['uri']
    ):
        Log.an().error(
            'cannot copy from %s to %s',
            src_uri['uri'],
            dest_uri['uri']
        )
        return False

    return True


# local/Agave mixed methods

def _copy_local_agave(src_uri, dest_uri, agave, local=None):
    """
    Copy local data to Agave using AgavePy Wrapper.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if not agave['agave_wrapper'].files_import_from_local(
            dest_uri['authority'],
            dest_uri['folder'],
            dest_uri['name'],
            src_uri['chopped_path']
    ):
        Log.an().error(
            'cannot copy from %s to %s',
            src_uri['uri'],
            dest_uri['uri']
        )
        return False

    return True


def _copy_agave_local(src_uri, dest_uri, agave, local=None):
    """
    Copy Agave data to a local destination using AgavePy Wrapper.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        agave: dict that contains:
            agave_wrapper: Agave wrapper object.

    Returns:
        On success: True.
        On failure: False.

    """
    if not agave['agave_wrapper'].files_download(
            src_uri['authority'],
            src_uri['chopped_path'],
            dest_uri['chopped_path'],
            -1
    ):
        Log.an().error(
            'cannot copy from %s to %s',
            src_uri['uri'],
            dest_uri['uri']
        )
        return False

    return True
