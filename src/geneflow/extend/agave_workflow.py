"""This module contains the GeneFlow AgaveWorkflow class."""


from agavepy.agave import Agave
import requests

from geneflow.data_manager import DataManager
from geneflow.log import Log
from geneflow.uri_parser import URIParser
from geneflow.extend.agave_wrapper import AgaveWrapper


requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


class AgaveWorkflow:
    """GeneFlow workflow extension class to support Agave."""

    def __init__(
            self,
            config,
            job,
            parsed_job_work_uri
    ):
        """
        Initialize the GeneFlow AgaveWorkflow class.

        Args:
            self: class instance
            config: GeneFlow config
            job: job dictionary
            parsed_job_work_uri: job work URI

        Returns:
            Class instance.

        """
        self._job = job
        self._config = config
        self._parsed_job_work_uri = parsed_job_work_uri

        # init agave wrapper object
        self._agave_wrapper = AgaveWrapper(config['agave'], token_username=self._job['username'])
        self._parsed_archive_uri = None


    def initialize(self):
        """
        Initialize the GeneFlow AgaveWorkflow class.

        Initialize by connecting to Agave.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._agave_wrapper.connect():
            Log.an().error('cannot connect to agave')
            return False

        return True


    def init_data(self):
        """
        Initialize any data specific to this context.

        Create the archive URI in Agave.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._init_archive_uri():
            Log.an().error('cannot create archive uri')
            return False

        return True


    def _init_archive_uri(self):
        """
        Initialize and validate Agave job archive URI.

        Args:
            None.

        Returns:
            On success: True.
            On failure: False.

        """
        if 'agave' not in self._parsed_job_work_uri:
            Log.an().error(
                'job work uri must include an agave context'
            )
            return False

        # construct archive URI
        self._parsed_archive_uri = URIParser.parse(
            '{}/_agave_jobs'.format(
                self._parsed_job_work_uri['agave']['chopped_uri']
            )
        )
        if not self._parsed_archive_uri:
            Log.an().error(
                'invalid job work uri: %s', self._parsed_job_work_uri['agave']
            )
            return False

        # create URI
        if not DataManager.mkdir(
                parsed_uri=self._parsed_archive_uri,
                recursive=True,
                agave=self.get_context_options()
        ):
            Log.an().error(
                'cannot create agave archive uri: %s',
                self._parsed_archive_uri['chopped_uri']
            )
            return False

        return True


    def get_context_options(self):
        """
        Return dict of options specific for this context.

        Args:
            None.

        Returns:
            Dict containing agave connection object and agave options.

        """
        return {
            'agave_wrapper': self._agave_wrapper,
            'parsed_archive_uri': self._parsed_archive_uri
        }
