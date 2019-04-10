"""This module contains the GeneFlow WorkflowInput class."""


from geneflow.log import Log
from geneflow.stageable_data import StageableData


class WorkflowInput(StageableData):
    """
    A class that represents Workflow inputs.

    Inherits from the "StageableData" class.
    """

    def __init__(
            self,
            name,
            data_uris,
            source_context,
            clean=False
    ):
        """
        Instantiate WorkflowInput class.

        Args:
            self: class instance.
            name: name of the input.
            data_uris: dict of all data URIs, including source.
                Formatted as:
                {context: URI, context: URI, ...}
            source_context: source context of data (e.g., local). This can be
                different from the URI scheme
            clean: remove old data directories? (default = False)

        Returns:
            WorkflowInput object.

        """
        # input name
        self._name = name

        # init StageableData base class
        StageableData.__init__(self, data_uris, source_context, clean)


    def initialize(self):
        """
        Initialize the WorkflowInput class.

        Initialize the base classes and checking for the
        existence of the source data URI.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse data URIs in StageableData class
        if not StageableData.initialize(self):
            msg = 'cannot initialize data staging'
            Log.an().error(msg)
            return False

        return True
