"""This module contains the GeneFlow LocalWorkflow class."""

class LocalWorkflow:
    """
    A class that represents the Local Workflow objects.
    """

    def __init__(
            self,
            job,
            config,
            parsed_job_work_uri
    ):
        """
        Instantiate LocalWorkflow class.
        """
        self._job = job
        self._config = config
        self._parsed_job_work_uri = parsed_job_work_uri


    def initialize(self):
        """
        Initialize the LocalWorkflow class.

        This workflow class has no additional functionality.

        Args:
            None.

        Returns:
            True.

        """
        return True


    def init_data(self):
        """
        Initialize any data specific to this context.

        """
        return True


    def get_context_options(self):
        """
        Return dict of options specific for this context.

        Args:
            None.

        Returns:
            {} - no options specific for this context.

        """
        return {}
