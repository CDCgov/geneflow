"""This module contains the GeneFlow GridEngineWorkflow class."""


import drmaa

from geneflow.log import Log


class GridEngineWorkflow:
    """
    A class that represents the Grid Engine Workflow objects.
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

        # drmaa library for grid engine
        self._drmaa_session = drmaa.Session()

    def __del__(self):
        """
        Disconnect from drmaa session when workflow class is deleted.

        Args:
            None.

        Returns:
            Nothing.

        """
        try:
            self._drmaa_session.exit()
        except drmaa.errors.DrmaaException as err:
            Log.a().warning()
                'cannot exit drmaa session: [%s]', str(err)
            )


    def initialize(self):
        """
        Initialize the GridEngineWorkflow class.

        This workflow class has no additional functionality.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._drmaa_session.initialize()
        except drmaa.errors.DrmaaException as err:
            Log.an().error(
                'cannot initialize drmaa session: [%s]', str(err)
            )
            return False

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
            Dict containing drmaa session.

        """
        return {
            'drmaa_session': self._drmaa_session
        }
