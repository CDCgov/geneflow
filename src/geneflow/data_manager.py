"""This module contains the GeneFlow DataManager class."""


import inspect

from geneflow.uri_parser import URIParser
from geneflow.log import Log
from geneflow.extend import data_manager_contexts


class DataManager:
    """
    Copy/move, list, delete data for various contexts.

    Currently, these contexts include: local, agave.
    """

    @classmethod
    def list(cls, uri=None, parsed_uri=None, **kwargs):
        """
        List data in various contexts.

        URIs are parsed to extract contexts, and the appropriate method is
        called. Either uri or parsed_uri may be specified, but not both. If
        both are specified, parsed_uri is used.

        Args:
            uri: URI to list.
            parsed_uri: URI to list, already parsed.
            **kwargs: Other arguments specific to context.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse and validate URI
        if not parsed_uri:
            parsed_uri = URIParser.parse(uri)
            if not parsed_uri:
                Log.an().error('invalid uri: %s', uri)
                return False

        # check if list method exists for context
        try:
            list_func = getattr(cls, '_list_{}'.format(parsed_uri['scheme']))
        except AttributeError:
            Log.an().error('_list_%s method not defined', parsed_uri['scheme'])
            return False

        return list_func(parsed_uri, **kwargs)


    @classmethod
    def exists(cls, uri=None, parsed_uri=None, **kwargs):
        """
        Check if URI exists.

        URIs are parsed to extract contexts, and the appropriate method is
        called. Either uri or parsed_uri may be specified, but not both, if
        both are specified, parsed_uri is used.

        Args:
            uri: URI to check.
            parsed_uri: URI to check, already parsed.
            **kwargs: Other arguments specific to context.

        Returns:
            True if the URI exists, False if it doesn't exist, None if
            an exception occurs.

        """
        # parse and validate URI
        if not parsed_uri:
            parsed_uri = URIParser.parse(uri)
            if not parsed_uri:
                Log.an().error('invalid uri: %s', uri)
                return None

        # check if the exists method exists for context
        try:
            exists_func = getattr(cls, '_exists_{}'\
                .format(parsed_uri['scheme']))

        except AttributeError:
            Log.an().error(
                '_exists_%s method not defined', parsed_uri['scheme']
            )
            return None

        return exists_func(parsed_uri, **kwargs)


    @classmethod
    def delete(cls, uri=None, parsed_uri=None, **kwargs):
        """
        Delete URI.

        URIs are parsed to extract contexts, and the appropriate method is
        called. Either uri or parsed_uri may be specified, but not both, if
        both are specified, parsed_uri is used.

        Args:
            uri: URI to delete.
            parsed_uri: URI to delete, already parsed.
            **kwargs: Other arguments specific to context.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse and validate URI
        if not parsed_uri:
            parsed_uri = URIParser.parse(uri)
            if not parsed_uri:
                Log.an().error('invalid uri: %s', uri)
                return False

        # check if the delete method exists for context
        try:
            delete_func = getattr(cls, '_delete_{}'\
                .format(parsed_uri['scheme']))

        except AttributeError:
            Log.an().error(
                '_delete_%s method not defined', parsed_uri['scheme']
            )
            return False

        return delete_func(parsed_uri, **kwargs)


    @classmethod
    def mkdir(cls, uri=None, parsed_uri=None, recursive=False, **kwargs):

        """
        Create directory at URI.

        URIs are parsed to extract contexts, and the appropriate method is
        called. Either uri or parsed_uri may be specified, but not both, if
        both are specified, parsed_uri is used.

        Args:
            uri: URI to create.
            parsed_uri: URI to create, already parsed.
            recursive: If true, recursively create parent directories.
            **kwargs: Other arguments specific to context.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse and validate URI
        if not parsed_uri:
            parsed_uri = URIParser.parse(uri)
            if not parsed_uri:
                Log.an().error('invalid uri: %s', uri)
                return False

        # check if the mkdir method exists for context
        if recursive:
            try:
                mkdir_func = getattr(cls, '_mkdir_recursive_{}'\
                    .format(parsed_uri['scheme']))

            except AttributeError:
                Log.an().error(
                    '_mkdir_recursive_%s method not defined',
                    parsed_uri['scheme']
                )
                return False

        else:
            try:
                mkdir_func = getattr(cls, '_mkdir_{}'\
                    .format(parsed_uri['scheme']))

            except AttributeError:
                Log.an().error(
                    '_mkdir_%s method not defined', parsed_uri['scheme']
                )
                return False

        # always remove final slash from URI before calling mkdir
        return mkdir_func(URIParser.parse(parsed_uri['chopped_uri']), **kwargs)


    @classmethod
    def copy(
            cls,
            src_uri=None,
            parsed_src_uri=None,
            dest_uri=None,
            parsed_dest_uri=None,
            **kwargs
    ):
        """
        Copy data to/from/within workflow contexts.

        Source and destination URIs are parsed to extract contexts, and
        the appropriate methods are called accordingly.

        Args:
            src: Source URI.
            dest: Destination URI.
            **kwargs: Other arguments specific to context.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse and validate src URI
        if not parsed_src_uri:
            parsed_src_uri = URIParser.parse(src_uri)
            if not parsed_src_uri:
                Log.an().error('invalid src uri: %s', src_uri)
                return False

        # parse and validate dest URI
        if not parsed_dest_uri:
            parsed_dest_uri = URIParser.parse(dest_uri)
            if not parsed_dest_uri:
                Log.an().error('invalid dest uri: %s', dest_uri)
                return False

        # check if copy method exists for contexts
        try:
            copy_func = getattr(cls, '_copy_{}_{}'.format(
                parsed_src_uri['scheme'], parsed_dest_uri['scheme']
            ))
        except AttributeError:
            Log.an().error(
                '_copy_%s_%s method not defined',
                parsed_src_uri['scheme'],
                parsed_dest_uri['scheme']
            )
            return False

        return copy_func(
            parsed_src_uri,
            parsed_dest_uri,
            **{
                list_item: kwargs[list_item]
                for list_item in set(
                    [parsed_src_uri['scheme'], parsed_dest_uri['scheme']]
                )
            }
        )


def init():
    """Import methods in the data_manager_contexts module as static methods."""
    all_funcs = inspect.getmembers(data_manager_contexts, inspect.isfunction)
    for func in all_funcs:
        setattr(DataManager, func[0], staticmethod(func[1]))

# initialize the module when imported
init()
