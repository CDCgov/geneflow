"""This module contains the GeneFlow WorkflowStep class."""

import json
import regex as re

from geneflow.log import Log
from geneflow.data import DataSource, DataSourceException
from geneflow.stageable_data import StageableData
from geneflow.uri_parser import URIParser

class WorkflowStep(StageableData):
    """
    A class that represents Workflow step objects.

    Inherits from the "StageableData" class.
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
            clean=False
    ):
        """
        Instantiate WorkflowStep class, save input variables.

        Args:
            job: workflow job definition
            step: dict of the normalized database record for step:
                {
                    step_id:
                    name:
                    number:
                    letter:
                    app_id:
                    app_name:
                    map:
                        uri:
                        regex:
                    template: (dict from json)
                        item: value,
                        item: value,...
                    depend: [step1, step2, ...]
                }
            app: dict of normalized record for app
                {
                    app_id:
                    name:
                    description:
                    username:
                    type:
                    definition:
                    inputs: (dict from json)
                    parameters: (dict from json)
                    public:
                }
            inputs: dict of workflow-level inputs (in the correct step context).
            parameters: dict of workflow-level parameters.
            config: workflow config info, including database connection.
            depend_uris: dict of URIs for each dependent step:
                {step-name: URI struct,
                 step-name: URI struct, ...}
            data_uris: dict of all output data URIs, including source.
                Formatted as:
                {context: URI, context: URI, ...}
            source_context: source context of data (e.g., local). This can be
                different from the URI scheme
            clean: remove old data directories? (default = False)

        Returns:
            WorkflowStep object.

        """
        # database records for job, step, and app
        self._job = job
        self._step = step
        self._app = app

        # step status
        self._status = 'PENDING'

        # workflow-level inputs and parameters
        self._inputs = inputs
        self._parameters = parameters

        # workflow config info
        self._config = config

        # parsed URIs of dependent steps
        self._depend_uris = depend_uris

        # remove old data URI during init?
        self._clean = clean

        # map/reduce
        self._map = []
        self._map_uri = ''  # expanded map_uri
        self._parsed_map_uri = {}
        self._replace = {}

        # init StageableData base class
        StageableData.__init__(self, data_uris, source_context, clean)


    def initialize(self):
        """
        Initialize the WorkflowStep class.

        By creating the source data URI, and
        parsing the step templates.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        # parse data uris in StageableData class
        if not StageableData.initialize(self):
            msg = 'cannot initialize data staging'
            Log.an().error(msg)
            return self._fatal(msg)

        # create data uri in the source context
        if not self._init_data_uri():
            msg = 'cannot create data uris'
            Log.an().error(msg)
            return self._fatal(msg)

        # make sure URIs for dependent steps match step dict
        # and app context
        if not self._validate_depend_uris():
            msg = 'validation failed for dependent step uris'
            Log.an().error(msg)
            return self._fatal(msg)

        # build template replacement list
        if not self._build_replace():
            msg = 'cannot build replacement strings for templates'
            Log.an().error(msg)
            return self._fatal(msg)

        # parse map uri
        if not self._parse_map_uri():
            msg = 'cannot parse map uri'
            Log.an().error(msg)
            return self._fatal(msg)

        return True


    def __str__(self):
        """
        Create a string representation of the workflow step.

        Args:
            self: class instance.

        Returns:
            String representation of the workflow step.

        """
        str_rep = (
            "    Step: "+self._step['name']+" ("+self._step['step_id']+")"
            "\n        App: "+self._app['name']+
            "\n        Map URI: "+str(self._map_uri)+
            "\n        Data URI: "+str(self._data_uris[self._source_context])+
            "\n        Depends: "+str(self._step['depend'])
        )

        return str_rep


    def _init_data_uri(self):
        """
        Create the output data URI for the step.

        This method must be overridden by a child class
        for a specific context (i.e., local, agave).

        """
        raise NotImplementedError


    def _validate_depend_uris(self):
        """
        Validate the depend URI list against depend list of the step definition.

        Also validate that the scheme of each depend URI matches
        that of this step's output (i.e., the data URI of the source context.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        for depend in self._step['depend']:
            if depend in self._depend_uris:
                # check if depend URI scheme is the same as that of this
                # step's output
                if (
                        self._depend_uris[depend]['scheme']
                        != self._parsed_data_uris[self._source_context]\
                            ['scheme']
                ):
                    msg = 'incompatible scheme for depend uri {} of step {}'\
                        .format(
                            self._depend_uris[depend]['chopped_uri'],
                            depend
                        )
                    Log.an().error(msg)
                    return self._fatal(msg)

            else:
                msg = 'uri missing for dependent step {}'.format(depend)
                Log.an().error(msg)
                return self._fatal(msg)

        return True


    def _parse_map_uri(self):
        """
        Parse and validate the map URI, for map-reduce processing.

        The map URI can point to the output URIs of previous workflow steps.

        The map URI template value can take the following forms:
            {workflow->input-name}: 'input-name' must be part of workflow-level
                inputs (i.e., self._inputs)
            {step-name->output}: 'step-name' must be a valid step name, and
                must be listed in the 'depend' list.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        if not self._step['map']['uri']:
            # map URI is an optional definition field
            self._map_uri = ''
        else:
            match = re.match(r'{([^{}]+)->([^{}]+)}', self._step['map']['uri'])
            if match:
                if match.group(1) == 'workflow': # use workflow-level input uri
                    # check if uri name is in input list
                    if match.group(2) in self._inputs:
                        # make sure the input URI to be used as the map URI
                        # is valid
                        self._parsed_map_uri = URIParser.parse(
                            self._inputs[match.group(2)]
                        )
                        if not self._parsed_map_uri:
                            msg = 'invalid map uri for inputs.{}: {}'\
                                .format(
                                    match.group(2),
                                    self._inputs[match.group(2)]
                                )
                            Log.an().error(msg)
                            return self._fatal(msg)

                        self._map_uri = self._parsed_map_uri['chopped_uri']

                    else:
                        msg = 'invalid template reference to input: {}'\
                            .format(self._step['map']['uri'])
                        Log.an().error(msg)
                        return self._fatal(msg)

                else: # use uri from previous step
                    # check if previous step is a dependency
                    if match.group(1) in self._step['depend']:
                        if match.group(2) == 'output':
                            self._map_uri = self._depend_uris[match.group(1)]\
                                ['chopped_uri']
                            self._parsed_map_uri \
                                = self._depend_uris[match.group(1)]

                        else:
                            msg = 'invalid template reference, must be "output": {}'\
                                .format(self._step['map']['uri'])
                            Log.an().error(msg)
                            return self._fatal(msg)

                    else:
                        # error, not a dependency
                        msg = 'template reference to step must be listed as dependent: {}'\
                            .format(self._step['map']['uri'])
                        Log.an().error(msg)
                        return self._fatal(msg)

            else:
                # invalid format
                msg = 'invalid template value for step map uri: {}'.format(
                    self._step['map']['uri']
                )
                Log.an().error(msg)
                return self._fatal(msg)

        return True


    def _get_map_uri_list(self):
        """
        Get the contents of the map URI.

        This method must be overridden by a child class for the specific
        context.

        """
        raise NotImplementedError


    def iterate_map_uri(self):
        """
        Expand step templates for each map-reduce item.

        Items must match the map-reduce regex to be included,
        and are stored in the self._map list.
        If no map_uri is given, only one item "." is included in _map.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        def multiple_replace(string, rep_dict):
            """
            Replace multiple string patterns simultaneously.

            Args:
                string: The string to be replaced.
                rep_dict: Dictionary containing key and values as patterns that
                    should be replaced.

            Returns:
                On success: The string with all the patterns replaced.
                On failure: False.

            """
            pattern = re.compile(
                "|".join([re.escape(k) for k in rep_dict.keys()]),
                re.M
            )
            return pattern.sub(lambda x: rep_dict[x.group(0)], string)

        # iterate map items
        if self._map_uri == '':
            # no mapping, run only one job
            self._map = [{
                'filename': 'root',
                'replace': {},
                'template': {},
                'status': 'PENDING',
                'attempt': 0,
                'run': [{}]
            }]

        else:
            # list uri contents and place into matched files
            file_list = self._get_map_uri_list()
            if file_list is False:
                msg = 'cannot get list of items from map uri: {}'.format(
                    self._map_uri
                )
                Log.an().error(msg)
                return self._fatal(msg)

            if file_list == []: # this folder should never be empty
                msg = 'map uri contents cannot be empty: {}'.format(
                    self._map_uri
                )
                Log.an().error(msg)
                return self._fatal(msg)

            for filename in file_list:
                # check if file matches regex
                match = re.match(self._step['map']['regex'], filename)
                if match:
                    groups = list(match.groups())
                    replace = {}
                    for i, group in enumerate(groups):
                        replace[str('{'+str(i+1)+'}')] = str(group)
                    self._map.append({
                        'filename': filename,
                        'replace': replace,
                        'template': {},
                        'status': 'PENDING',
                        'attempt': 0,
                        'run': [{}]
                    })

            if not self._map:
                msg = (
                    'map uri contents must include at least'
                    ' one item matching regex: {}'
                ).format(self._map_uri)
                Log.an().error(msg)
                return self._fatal(msg)

        # iterate through items, expand templates
        for map_item in self._map:
            replace = map_item['replace'].copy()
            replace.update(self._replace)
            for template_key in self._step['template']:
                if isinstance(self._step['template'][template_key], str):
                    map_item['template'][template_key] = multiple_replace(
                        self._step['template'][template_key],
                        replace
                    )
                else:
                    map_item['template'][template_key]\
                        = self._step['template'][template_key]

        return True


    def _build_replace(self):
        """
        Build a list of string replacements for template items.

        Result is stored in the self._replace dict.

        Args:
            self: class instance.

        Returns:
            On success: True.
            On failure: False.

        """
        for template_item in self._step['template']:
            if not isinstance(self._step['template'][template_item], str):
                continue

            matches = re.findall(
                r'{([^{}]+)->([^{}]+)}',
                self._step['template'][template_item]
            )

            if matches:

                for match in matches:
                    key = '{'+match[0]+'->'+match[1]+'}'
                    if match[0] == 'workflow':
                        # replace with workflow-level input or parameter
                        if match[1] in self._inputs:
                            self._replace[str(key)] \
                                = str(self._inputs[match[1]])

                        elif match[1] in self._parameters:
                            self._replace[str(key)] \
                                = str(self._parameters[match[1]])

                        else:
                            msg = (
                                'invalid template reference,'
                                ' must be a workflow input/parameter key: {}'
                            ).format(key)
                            Log.an().error(msg)
                            return self._fatal(msg)

                    else:
                        # replace with output URI of previous step
                        if match[0] in self._step['depend']:
                            if match[1] == 'output':
                                self._replace[str(key)] \
                                    = self._depend_uris[match[0]]\
                                        ['chopped_uri']

                            else:
                                msg = (
                                    'invalid template reference,'
                                    ' must be "output": {}'
                                ).format(key)
                                Log.an().error(msg)
                                return self._fatal(msg)

                        else:
                            msg = (
                                'template reference to step must be'
                                ' listed as dependent: {}'
                            ).format(key)
                            Log.an().error(msg)
                            return self._fatal(msg)

        return True


    def get_step(self):
        """
        Return the step dict.

        Args:
            self: class instance.

        Returns:
            _step dict

        """
        return self._step


    def get_status_struct(self):
        """
        Return a dict structure with the status of all map items.

        Args:
            self: class instance.

        Returns:
            A dict with the following structure:
                {
                    id: step id
                    name: step name
                    map:
                        filename: status,
                        filename: status,...
                }
            Each filename: status combination indicates the status of the job
            processing one of the map-reduce items.

        """
        struct = {
            'id': self._step['step_id'][:8],
            'name': self._step['name'],
            'map': {}
        }
        for map_item in self._map:
            struct['map'][map_item['filename']] = map_item['status']

        return struct


    def run(self):
        """
        Execute the app for this step.

        This method must be overridden by the
        child class for a specific context.

        """
        raise NotImplementedError


    def _serialize_detail(self):
        """
        Serialize all map-reduce items.

        This method can be overridden and customized
        if any map items have non-serializable objects. See
        the LocalStep class for an example.

        Args:
            self: class instance.

        Returns:
            A dict of all map items and their run histories.

        """
        return {
            map_item['filename']: map_item['run'] for map_item in self._map
        }


    def _fatal(self, msg):
        """
        Update database with error message and set status.

        Args:
            msg: status message.

        Returns:
            False

        """
        self._update_status_db('ERROR', msg)

        return False


    def _update_status_db(self, status, msg):
        """
        Update the status of the step, and the status record in the database.

        Args:
            status: new step status.
            msg: message associated with step status.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            data_source = DataSource(self._config['database'])
        except DataSourceException as err:
            msg = 'data source initialization error [{}]'.format(str(err))
            Log.an().error(msg)
            return False

        self._status = status
        detail = self._serialize_detail()

        if not data_source.update_job_step_status(
                self._step['step_id'],
                self._job['job_id'],
                self._status,
                json.dumps(detail),
                msg
        ):
            Log.an().warning('cannot update job status in data source')
            data_source.rollback()

        data_source.commit()
        return True


    def check_running_jobs(self):
        """
        Check status/progress of all map-reduce items and update _map status.

        This method must be overridden by the child class for a
        specific context.

        """
        raise NotImplementedError


    def all_finished(self):
        """
        Check if all map-reduce jobs have finished.

        Args:
            self: class instance.

        Returns:
            True if all map-reduce items are in the 'FINISHED' state.
            False if at least one job is not in the 'FINISHED' state.

        """
        finished = [map_item['status'] == 'FINISHED' for map_item in self._map]

        return all(finished)


    def all_done(self):
        """
        Check if all map-reduce jobs have finished.

        Args:
            self: class instance.

        Returns:
            True if all map-reduce items are in the 'FINISHED', 'FAILED', or
                'STOPPED' state.
            False if at least one job is not in the 'FINISHED', 'FAILED', or
                'STOPPED' state.

        """
        done = [
            map_item['status'] == 'FINISHED'\
            or map_item['status'] == 'FAILED'\
            or map_item['status'] == 'STOPPED'\
            for map_item in self._map
        ]

        return all(done)


    def any_failed(self):
        """
        Check if any map-reduce jobs failed or stopped.

        Args:
            self: class instance.

        Returns:
            True if any map-reduce item is in the 'FAILED' state.
            False if no map-reduce item is in the 'FAILED' state.

        """
        failed = [
            map_item['status'] == 'FAILED'\
            or map_item['status'] == 'STOPPED'\
            for map_item in self._map
        ]

        return any(failed)


    def retry_failed(self):
        """
        Retry any map-reduce jobs that failed.

        This method must be overridden by the child class for a specific
        context.

        """
        raise NotImplementedError


    def clean_up(self):
        """
        Perform post-job cleanup, if necessary.

        This method can be overridden for context-specific cleanup.

        """
        self._update_status_db('FINISHED', '')

        return True
