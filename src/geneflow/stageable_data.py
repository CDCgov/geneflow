"""This module contains the GeneFlow StageableData class."""


from geneflow.data_manager import DataManager
from geneflow.log import Log
from geneflow.uri_parser import URIParser


class StageableData:
    """
    StageableData class.

    Serves as a base class for workflow input data and one of the base classes
    for workflow steps.
    """

    def __init__(self, data_uris, source_context, clean=False):
        """
        Instantiate StageableData class, save input variables.

        Args:
            self: class instance.
            data_uris: dict of all data URIs, including source. Formatted as
                {context: URI, context: URI, ...}
            source_context: source context of data (e.g., local). This can be
                different from the URI scheme
            clean: remove target URIs before staging? (default = False)

        Returns:
            StageableData object.

        """
        # dict of data URIs, including source
        # format: {context: URI, context: URI, ..}
        # context can be different from URI scheme
        self._data_uris = data_uris
        # URIs expanded and validated w/ URIParser
        self._parsed_data_uris = {}
        # source context of data
        self._source_context = source_context
        # not staged by default
        self._staged = False
        # rm (clean) folders before staging?
        self._clean = clean


    def initialize(self):
        """
        Initialize instance of StageableData.

        By parsing URIs with GeneFlow.URIParser & checking source context
        validity.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse data uris
        for context in self._data_uris:
            parsed_uri = URIParser.parse(self._data_uris[context])
            if not parsed_uri:
                msg = 'invalid data uri for context: {}->{}'.format(
                    context, self._data_uris[context]
                )
                Log.an().error(msg)
                return self._fatal(msg)

            # path cannot be root (/)
            if parsed_uri['chopped_path'] == '/':
                msg = 'context data uri cannot be root (/): {}->{}'.format(
                    context, self._data_uris[context]
                )
                Log.an().error(msg)
                return self._fatal(msg)

            self._parsed_data_uris[context] = parsed_uri

        # make sure source_context is one of the listed of URIs
        if self._source_context not in self._parsed_data_uris:
            msg = 'source context must one of the data uri contexts: {}'.\
                format(self._source_context)
            Log.an().error(msg)
            return self._fatal(msg)

        return True


    def stage(self, **kwargs):
        """
        Copy data to all contexts from source URI.

        Set _staged indicator to True on success.

        Args:
            self: class instance.
            **kwargs: additional arguments required by DataManager.copy().

        Returns:
            True or False.

        """
        for context in self._parsed_data_uris:
            if context != self._source_context:
                if self._clean:
                    # remove target URI first
                    pass

                Log.some().debug(
                    'staging data: {}->{} to {}->{}'.format(
                        self._source_context,
                        self._parsed_data_uris[self._source_context]['chopped_uri'],
                        context,
                        self._parsed_data_uris[context]['chopped_uri']
                    )
                )

                if not DataManager.copy(
                        parsed_src_uri=self._parsed_data_uris\
                            [self._source_context],
                        parsed_dest_uri=self._parsed_data_uris[context],
                        **kwargs
                ):
                    msg = 'cannot stage data by copying from {} to {}'.format(
                        self._parsed_data_uris[self._source_context]\
                            ['chopped_uri'],
                        self._parsed_data_uris[context]['chopped_uri']
                    )
                    Log.an().error(msg)
                    return self._fatal(msg)

        self._staged = True

        return True


    def is_staged(self):
        """
        Check if data has been staged to contexts.

        Args:
            self: class instance.

        Returns:
            True if staged, False if not staged.

        """
        return self._staged


    def get_data_uri(self, context):
        """
        Return the URI for a specific context.

        Args:
            self: class instance.
            context: context of requested data URI.

        Returns:
            On success: data URI for given context.
            On failure: False.

        """
        if context not in self._parsed_data_uris:
            msg = 'invalid data uri context: {}'.format(context)
            Log.an().error(msg)
            return self._fatal(msg)

        return self._parsed_data_uris[context]


    def _fatal(self, msg):
        """
        Returns false

        This method is overridden by methods in the workflow step and input
        classes.

        Args:
            msg: status message, not used unless method is overridden.

        Returns:
            False

        """
        return False
