"""This module contains the GeneFlow LocalStep class."""


from slugify import slugify

from geneflow.log import Log
from geneflow.workflow_step import WorkflowStep
from geneflow.data_manager import DataManager
from geneflow.uri_parser import URIParser
from geneflow.shell_wrapper import ShellWrapper


class LocalStep(WorkflowStep):
    """
    A class that represents Local Workflow step objects.

    Inherits from the "WorkflowStep" class.
    """

    def __init__(
            self,
            job,
            step,
            app,
            inputs,
            parameters,
            config,
            depend_uris,
            data_uris,
            source_context,
            clean=False,
            local={}
    ):
        """
        Instantiate LocalStep class by calling the super class constructor.

        See documentation for WorkflowStep __init__().
        """
        super(LocalStep, self).__init__(
            job,
            step,
            app,
            inputs,
            parameters,
            config,
            depend_uris,
            data_uris,
            source_context,
            clean
        )


    def initialize(self):
        """
        Initialize the LocalStep class.

        Validate that the step context is appropriate for this "local" context.
        And that the app contains a "local" definition.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        # make sure the step context is local
        if self._step['execution']['context'] != 'local':
            msg = (
                '"local" step class can only be instantiated with a'
                ' step definition that has a "local" execution context'
            )
            Log.an().error(msg)
            return self._fatal(msg)

        # make sure app has a local definition
        if 'local' not in self._app['definition']:
            msg = (
                '"local" step class can only be instantiated with an app that'
                ' has a "local" definition'
            )
            Log.an().error(msg)
            return self._fatal(msg)

        if not super(LocalStep, self).initialize():
            msg = 'cannot initialize workflow step'
            Log.an().error(msg)
            return self._fatal(msg)

        return True


    def _init_data_uri(self):
        """
        Create output data URI for the source context (local).

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        # make sure the source data URI has a compatible scheme (local)
        if self._parsed_data_uris[self._source_context]['scheme'] != 'local':
            msg = 'invalid data uri scheme for this step: {}'.format(
                self._parsed_data_uris[self._source_context]['scheme']
            )
            Log.an().error(msg)
            return self._fatal(msg)

        # delete old folder if it exists and clean==True
        if (
                DataManager.exists(
                    parsed_uri=self._parsed_data_uris[self._source_context]
                )
                and self._clean
        ):
            if not DataManager.delete(
                    parsed_uri=self._parsed_data_uris[self._source_context]
            ):
                Log.a().warning(
                    'cannot delete existing data uri: %s',
                    self._parsed_data_uris[self._source_context]['chopped_uri']
                )

        # create folder
        if not DataManager.mkdir(
                parsed_uri=self._parsed_data_uris[self._source_context],
                recursive=True
        ):
            msg = 'cannot create data uri: {}'.format(
                self._parsed_data_uris[self._source_context]['chopped_uri']
            )
            Log.an().error(msg)
            return self._fatal(msg)

        # create _log folder
        if not DataManager.mkdir(
                uri='{}/_log'.format(
                    self._parsed_data_uris[self._source_context]['chopped_uri']
                ),
                recursive=True
        ):
            msg = 'cannot create _log folder in data uri: {}/_log'.format(
                self._parsed_data_uris[self._source_context]['chopped_uri']
            )
            Log.an().error(msg)
            return self._fatal(msg)

        return True


    def _get_map_uri_list(self):
        """
        Get the contents of the map URI (local URI).

        Args:
            self: class instance.

        Returns:
            Array of base file names in the map URI. Returns False on
            exception.

        """
        # make sure map URI is compatible scheme (local)
        if self._parsed_map_uri['scheme'] != 'local':
            msg = 'invalid map uri scheme for this step: {}'.format(
                self._parsed_map_uri['scheme']
            )
            Log.an().error(msg)
            return self._fatal(msg)

        # get file list from URI
        file_list = DataManager.list(parsed_uri=self._parsed_map_uri)
        if file_list is False:
            msg = 'cannot get contents of map uri: {}'\
                .format(self._parsed_map_uri['chopped_uri'])
            Log.an().error(msg)
            return self._fatal(msg)

        return file_list


    def _run_map(self, map_item):
        """
        Run a job for each map item and store the proc and PID.

        Args:
            self: class instance.
            map_item: map item object (item of self._map).

        Returns:
            On success: True.
            On failure: False.

        """
        # load default app inputs, overwrite with template inputs
        inputs = {}
        for input_key in self._app['inputs']:
            if input_key in map_item['template']:
                inputs[input_key] = map_item['template'][input_key]
            else:
                inputs[input_key] = self._app['inputs'][input_key]['default']

        # load default app parameters, overwrite with template parameters
        parameters = {}
        for param_key in self._app['parameters']:
            if param_key in map_item['template']:
                parameters[param_key] = map_item['template'][param_key]
            else:
                parameters[param_key] \
                    = self._app['parameters'][param_key]['default']

        # construct shell command
        cmd = self._app['definition']['local']['script']
        for input_key in inputs:
            if inputs[input_key]:
                cmd += ' --{}="{}"'.format(
                    input_key,
                    URIParser.parse(inputs[input_key])['chopped_path']
                )
        for param_key in parameters:
            if param_key == 'output':
                cmd += ' --output="{}/{}"'.format(
                    self._parsed_data_uris[self._source_context]\
                        ['chopped_path'],
                    parameters['output']
                )

            else:
                cmd += ' --{}="{}"'.format(
                    param_key, parameters[param_key]
                )

        # add exeuction method
        cmd += ' --exec_method="{}"'.format(self._step['execution']['method'])

        # add stdout and stderr
        log_path = '{}/_log/gf-{}-{}-{}'.format(
            self._parsed_data_uris[self._source_context]['chopped_path'],
            map_item['attempt'],
            slugify(self._step['name']),
            slugify(map_item['template']['output'])
        )
        cmd += ' > "{}.out" 2> "{}.err"'.format(log_path, log_path)

        Log.a().debug('command: %s', cmd)

        # launch process
        proc = ShellWrapper.spawn(cmd)
        if proc is False:
            msg = 'shell process error: {}'.format(cmd)
            Log.an().error(msg)
            return self._fatal(msg)

        # record job info
        map_item['run'][map_item['attempt']]['proc'] = proc
        map_item['run'][map_item['attempt']]['pid'] = proc.pid

        # set status of process
        map_item['status'] = 'RUNNING'
        map_item['run'][map_item['attempt']]['status'] = 'RUNNING'

        return True


    def run(self):
        """
        Execute shell scripts for each of the map items.

        Then store PIDs in run detail.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        for map_item in self._map:

            if not self._run_map(map_item):
                msg = 'cannot run script for map item "{}"'\
                    .format(map_item['filename'])
                Log.an().error(msg)
                return self._fatal(msg)

        self._update_status_db('RUNNING', '')

        return True


    def _serialize_detail(self):
        """
        Serialize map-reduce items.

        But leave out non-serializable Popen proc item, keep pid.

        Args:
            self: class instance.

        Returns:
            A dict of all map items and their run histories.

        """
        return {
            map_item['filename']: [
                {
                    'status': run_item['status'],
                    'pid': run_item['pid']
                } for run_item in map_item['run']
            ] for map_item in self._map
        }


    def check_running_jobs(self):
        """
        Check the status/progress of all map-reduce items and update _map status.

        Args:
            self: class instance.

        Returns:
            True.

        """
        # check if procs are running, finished, or failed
        for map_item in self._map:
            try:
                if ShellWrapper.is_running(
                        map_item['run'][map_item['attempt']]['proc']
                ):
                    map_item['status'] = 'RUNNING'
                else:
                    if map_item['run'][map_item['attempt']]['proc'].returncode:
                        map_item['status'] = 'FAILED'
                    else:
                        map_item['status'] = 'FINISHED'
                map_item['run'][map_item['attempt']]['status']\
                    = map_item['status']
            except (OSError, AttributeError) as err:
                Log.a().warning(
                    'process polling failed for map item "%s" [%s]',
                    map_item['filename'], str(err)
                )
                map_item['status'] = 'FAILED'

        self._update_status_db(self._status, '')

        return True


    def retry_failed(self):
        """
        Retry any map-reduce jobs that failed.

        This is not-yet supported for local apps.

        Args:
            self: class instance.

        Returns:
            False.

        """
        msg = 'retry not yet supported for local apps'
        Log.an().error(msg)
        return self._fatal(msg)
