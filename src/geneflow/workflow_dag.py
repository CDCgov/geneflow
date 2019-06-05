"""This module contains the GeneFlow WorkflowDAG class."""

import networkx as nx
import regex as re
from slugify import slugify

from geneflow.data_manager import DataManager
from geneflow.log import Log
from geneflow.uri_parser import URIParser
from geneflow.workflow_input import WorkflowInput


class WorkflowDAGException(Exception):
    """Custom exception for WorkflowDAG."""


class WorkflowDAG:
    """GeneFlow WorkflowDAG class."""

    def __init__(
            self,
            job,
            workflow,
            apps,
            parsed_job_work_uri,
            parsed_job_output_uri,
            config,
            **kwargs
    ):
        """
        Init WorkflowDAG class.

        Args:
            workflow: dict of workflow, updated to include any inputs,
                parameters, and final_output specified in the job.
            apps: dict of apps:
                {
                    'app1': { app dict },
                    'app2': { app dict },
                    ...
                }
            parsed_job_work_uri: dict of parsed job work URIs, one URI per
                context.
            parsed_job_output_uri: string of job output URI.
            config: dict of workflow config
            **kwargs: additional arguments specific to contexts for this
                workflow (e.g., local or agave arguments)

        Returns:
            WorkflowDAG instance.

        """
        self._job = job
        self._workflow = workflow
        self._apps = apps
        self._parsed_job_work_uri = parsed_job_work_uri
        self._parsed_job_output_uri = parsed_job_output_uri
        self._config = config

        # flattened parameters (i.e., only key: value pairs)
        self._parameters = {}

        # NetworkX graph object and topological sort of graph as list
        self._graph = None
        self._topo_sort = None

        # dict of all step and input contexts used in this workflow
        self._context_uris = {}
        self._parsed_context_uris = {}

        # Step classes for each required context
        self._context_classes = {}

        # additional args for specific contexts
        self._context_options = kwargs


    def initialize(self):
        """
        Initialize Graph class instance.

        Initialization includes: create NetworkX DiGraph,
        populate it with input and step nodes, and directed edges.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        for context in self._parsed_job_work_uri:
            # set default empty values for context options
            if context not in self._context_options:
                self._context_options[context] = {}

        # references to step classes for each context
        try:
            self._load_context_classes()
        except WorkflowDAGException as err:
            msg = 'cannot load context-specific step classes'
            Log.an().error(msg)
            raise WorkflowDAGException(str(err)+'|'+msg) from err

        # flatten parameters
        self._parameters = {
            param_name: param['value']
            for param_name, param in self._workflow['parameters'].items()
        }

        # init DAG object with structure and empty nodes
        self._graph = nx.DiGraph()

        try:
            self._init_graph_structure()
        except WorkflowDAGException as err:
            msg = 'cannot initialize graph structure'
            Log.an().error(msg)
            raise WorkflowDAGException(str(err)+'|'+msg) from err

        # validate that graph is DAG
        if not nx.is_directed_acyclic_graph(self._graph):
            msg = 'graph contains cycles, check step dependencies'
            Log.an().error(msg)
            raise WorkflowDAGException(msg)

        # topological sort of graph nodes
        self._topo_sort = list(nx.topological_sort(self._graph))

        # create URIs for each input and step for all contexts
        try:
            self._init_context_uris()
        except WorkflowDAGException as err:
            msg = 'cannot initialize context uris'
            Log.an().error(msg)
            raise WorkflowDAGException(str(err)+'|'+msg) from err

        # initalize input nodes
        try:
            self._init_inputs()
        except WorkflowDAGException as err:
            msg = 'cannot initialize workflow inputs'
            Log.an().error(msg)
            raise WorkflowDAGException(str(err)+'|'+msg) from err

        # initialize step nodes
        try:
            self._init_steps()
        except WorkflowDAGException as err:
            msg = 'cannot initialize workflow steps'
            Log.an().error(msg)
            raise WorkflowDAGException(str(err)+'|'+msg) from err


    def get_topological_sort(self):
        """
        Get reference to topological sort of graph.

        Args:
            None.

        Returns:
            Topological sort of graph, which is a list of strings.

        """
        return self._topo_sort


    def graph(self):
        """
        Get reference to graph.

        Args:
            None.

        Returns:
            NetworkX graph object.

        """
        return self._graph


    @classmethod
    def _get_template_matches(cls, template_value):
        """
        Given a string, find all GeneFlow template matches.

        Args:
            template_value: string with template, formated as {a->b}, where
                a and b are strings that do no contain brackets ('{' or '}')

        Returns:
            Dict of matches in template string structured as follows:
                {
                    '{workflow->input}': {
                        'name': 'workflow',
                        'var': 'input'
                    },
                    ...
                }
            If no matches found, an empty dict is returned.

        """
        match = re.findall(r'({([^{}]+)->([^{}]+)})', template_value)
        if not match:
            return {}

        matches = {}
        for item in match:
            matches[item[0]] = {
                'name': item[1],
                'var': item[2]
            }

        return matches


    def _get_step_dependencies(self, step):
        """
        Determine input/step dependencies for a step.

        Given the GeneFlow step definition, parse the map URI and template
        items to determine step dependencies.

        Args:
            step: step definition dict.

        Returns:
            Dict of matches structured as follows:
                {
                    '{workflow->input}': {
                        'name': 'workflow',
                        'var': 'input'
                    },
                    ...
                }
            If no matches found, an empty dict is returned.

        """
        # check map uri
        matches = self._get_template_matches(step['map']['uri'])

        # merge with matches from template items
        for template_value in step['template'].values():
            if isinstance(template_value, str):
                matches.update(self._get_template_matches(template_value))

        return matches


    def _load_context_classes(self):
        """
        Import modules and load references to step classes.

        Dynamically load modules for step classes, and keep a reference to the
        step class in the _context_classes dict.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        for context in self._parsed_job_work_uri:

            mod_name = '{}_step'.format(context)
            cls_name = '{}Step'.format(context.capitalize())

            try:
                step_mod = __import__(
                    'geneflow.extend.{}'.format(mod_name),
                    fromlist=[mod_name]
                )
            except ImportError as err:
                msg = 'cannot import context-specific step module: {} [{}]'\
                    .format(mod_name, str(err))
                Log.an().error(msg)
                raise WorkflowDAGException(msg)

            try:
                step_class = getattr(step_mod, cls_name)
            except AttributeError as err:
                msg = 'cannot import context-specific step class: {} [{}]'\
                    .format(cls_name, str(err))
                Log.an().error(msg)
                raise WorkflowDAGException(msg)

            # reference to step class
            self._context_classes[context] = step_class


    def _init_context_uris(self):
        """
        Generate all context URIs for this workflow run.

        Context URIs are generated based on contexts given in
        _parsed_job_work_uri, and the "final" context for steps given in the
        _parsed_job_output_uri.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        self._context_uris['inputs'] = {}
        self._context_uris['steps'] = {'final': {}}
        self._parsed_context_uris['inputs'] = {}
        self._parsed_context_uris['steps'] = {'final': {}}

        # init contexts in parsed_job_work_uri for inputs and steps
        for context in self._parsed_job_work_uri:

            self._context_uris['inputs'][context] = {}
            self._context_uris['steps'][context] = {}
            self._parsed_context_uris['inputs'][context] = {}
            self._parsed_context_uris['steps'][context] = {}

            for node_name in self._topo_sort:

                node = self._graph.nodes[node_name]
                if node['type'] == 'input':
                    if node['source_context'] == context:
                        # use original input URI
                        parsed_uri = URIParser.parse(
                            self._workflow['inputs'][node['name']]['value']
                        )
                        if not parsed_uri:
                            msg = 'invalid input uri: {}'.format(
                                self._workflow['inputs'][node['name']]['value']
                            )
                            raise WorkflowDAGException(msg)

                        self._context_uris['inputs'][context][node['name']]\
                            = parsed_uri['chopped_uri']
                        self._parsed_context_uris['inputs'][context]\
                            [node['name']] = parsed_uri

                    else:
                        # switch context of input URI
                        new_base_uri = '{}/_input-{}'.format(
                            self._parsed_job_work_uri[context]['chopped_uri'],
                            slugify(node['name'])
                        )

                        # create new base URI
                        if not DataManager.mkdir(
                                uri=new_base_uri,
                                recursive=True,
                                **{
                                    context: self._context_options[context]
                                }
                        ):
                            msg = 'cannot create new base uri for input: {}'\
                                .format(new_base_uri)
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                        # switch input URI base
                        switched_uri = URIParser.switch_context(
                            self._workflow['inputs'][node['name']]['value'],
                            new_base_uri
                        )
                        if not switched_uri:
                            msg = (
                                'cannot switch input uri context to '
                                'new base URI: {}->{}'
                            ).format(
                                self._workflow['inputs'][node['name']]\
                                    ['value'],
                                new_base_uri
                            )
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                        self._context_uris['inputs'][context][node['name']]\
                            = switched_uri['chopped_uri']
                        self._parsed_context_uris['inputs'][context]\
                            [node['name']] = switched_uri

                else: # node['type'] == 'step'
                    self._context_uris['steps'][context][node['name']]\
                        = '{}/{}'.format(
                            self._parsed_job_work_uri[context]['chopped_uri'],
                            slugify(node['name'])
                        )
                    self._parsed_context_uris['steps'][context][node['name']]\
                        = URIParser.parse(
                            self._context_uris['steps'][context][node['name']]
                        )

        # init final contexts for steps
        for node_name in self._topo_sort:

            node = self._graph.nodes[node_name]

            if node['type'] == 'step':
                self._context_uris['steps']['final'][node['name']]\
                    = '{}/{}'.format(
                        self._parsed_job_output_uri['chopped_uri'],
                        slugify(node['name'])
                    )
                self._parsed_context_uris['steps']['final'][node['name']]\
                    = URIParser.parse(
                        self._context_uris['steps']['final'][node['name']]
                    )


    def _init_graph_structure(self):
        """
        Create empty nodes for each workflow input and step.

        Nodes contain attributes for type (e.g., input or step), contexts for
        data staging (e.g., local or agave), source context, and node.
        The node attribute is initialized as None, but will later be a
        reference to a WorkflowInput or WorkflowStep object.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        # add empty input nodes to graph
        for input_name in self._workflow['inputs']:

            # extract the input source context
            parsed_input_uri = URIParser.parse(
                self._workflow['inputs'][input_name]['value']
            )
            if not parsed_input_uri:
                msg = 'invalid input uri: {}'.format(
                    self._workflow['inputs'][input_name]['value']
                )
                Log.an().error(msg)
                raise WorkflowDAGException(msg)

            source_context = parsed_input_uri['scheme']

            try:
                self._graph.add_node(
                    'input.{}'.format(input_name),
                    name='{}'.format(input_name),
                    type='input',
                    contexts={source_context: ''},
                    source_context=source_context,
                    node=None
                )
            except nx.NetworkXException as err:
                msg = 'cannot add input node "{}" to graph [{}]'.format(
                    input_name, str(err)
                )
                Log.an().error(msg)
                raise WorkflowDAGException(msg)

        # add empty step nodes to graph
        for step_name, step in self._workflow['steps'].items():

            # extract the step source context
            source_context = step['execution']['context']

            contexts = {source_context: ''}
            if step_name in self._workflow['final_output']:
                contexts['final'] = ''

            try:
                self._graph.add_node(
                    'step.{}'.format(step_name),
                    name='{}'.format(step_name),
                    type='step',
                    step=step,
                    contexts=contexts,
                    source_context=source_context,
                    node=None
                )
            except nx.NetworkXException as err:
                msg = 'cannot add step node "{}" to graph [{}]'.format(
                    step_name, str(err)
                )
                Log.an().error(msg)
                raise WorkflowDAGException(msg)

        # create graph edges and determine contexts for each node based on
        #   dependencies
        for step_name, step in self._workflow['steps'].items():

            # name of this step node
            step_node = 'step.{}'.format(step_name)

            # get all input or step dependencies for this step
            deps = self._get_step_dependencies(step)

            for dep in deps:

                if deps[dep]['name'] == 'workflow':
                    # input or parameter dependency
                    input_node = 'input.{}'.format(deps[dep]['var'])

                    # only add edge if it's an input (not a parameter)
                    if input_node in self._graph.nodes:
                        # add graph edge from input to step
                        try:
                            self._graph.add_edge(input_node, step_node)
                        except nx.NetworkXException as err:
                            msg = (
                                'cannot add edge from node "{}" to '
                                'node "{}" [{}]'
                            ).format(input_node, step_node, str(err))
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                        # add context key to dict for input node
                        self._graph.nodes[input_node]['contexts'][
                            step['execution']['context']
                        ] = ''

                    else:
                        # if input not found, make sure var refers to
                        # a parameter
                        if not deps[dep]['var'] in self._parameters:
                            msg = (
                                'invalid dependency for step "{}", '
                                'parameter or input "{}" does not exist'
                            ).format(step_name, deps[dep]['var'])
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                else:
                    # step dependency
                    depend_node = 'step.{}'.format(deps[dep]['name'])

                    if not self._graph.has_node(depend_node):
                        msg = (
                            'invalid dependency for step "{}", '
                            'step "{}" does not exist'
                        ).format(step_name, depend_node)
                        Log.an().error(msg)
                        raise WorkflowDAGException(msg)

                    # add graph edge from step to step
                    try:
                        self._graph.add_edge(depend_node, step_node)
                    except nx.NetworkXException as err:
                        msg = (
                            'cannot add edge from node "{}" to '
                            'node "{}" [{}]'
                        ).format(depend_node, step_node, str(err))
                        Log.an().error(msg)
                        raise WorkflowDAGException(msg)

                    # add context key to dict for depend node
                    self._graph.nodes[depend_node]['contexts'][
                        step['execution']['context']
                    ] = ''


    def _init_inputs(self):
        """
        Initialize Graph input nodes by creating WorkflowInput instances.

        Also populate the remaining contexts with URIs.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        for node_name in self._topo_sort:
            node = self._graph.nodes[node_name]
            if node['type'] == 'input':

                # update source context URI
                try:
                    node['contexts'][node['source_context']]\
                        = self._context_uris['inputs']\
                            [node['source_context']][node['name']]
                except KeyError as err:
                    msg = 'invalid source context: {} [{}]'.format(
                        node['source_context'], str(err)
                    )
                    Log.an().error(msg)
                    raise WorkflowDAGException(msg)

                # construct other context URIs
                for context in node['contexts']:
                    if (
                            context != node['source_context']
                            and not node['contexts'][context]
                    ):
                        try:
                            node['contexts'][context]\
                                = self._context_uris['inputs'][context]\
                                    [node['name']]
                        except KeyError as err:
                            msg = 'invalid context: {} [{}]'.format(
                                context, str(err)
                            )
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                # create instance of WorkflowInput class
                node['node'] = WorkflowInput(
                    node['name'],
                    node['contexts'],
                    node['source_context']
                )

                if not node['node'].initialize():
                    msg = 'cannot initialize graph node: {}'.format(node_name)
                    Log.an().error(msg)
                    raise WorkflowDAGException(msg)


    def _init_steps(self):
        """
        Initialize Graph step nodes by creating WorkflowStep instances.

        Also populate the remaining contexts with URIs.

        Args:
            None.

        Returns:
            On failure: Raises WorkflowDAGException.

        """
        for node_name in self._topo_sort:
            node = self._graph.nodes[node_name]
            if node['type'] == 'step':

                # update source context URI
                try:
                    node['contexts'][node['source_context']]\
                        = self._context_uris['steps']\
                            [node['source_context']][node['name']]
                except KeyError as err:
                    msg = 'invalid source context: {} [{}]'.format(
                        node['source_context'], str(err)
                    )
                    Log.an().error(msg)
                    raise WorkflowDAGException(msg)

                # construct other context URIs
                for context in node['contexts']:
                    if (
                            context != node['source_context']
                            and not node['contexts'][context]
                    ):
                        try:
                            node['contexts'][context]\
                                = self._context_uris['steps'][context]\
                                    [node['name']]
                        except KeyError as err:
                            msg = 'invalid context: {} [{}]'.format(
                                context, str(err)
                            )
                            Log.an().error(msg)
                            raise WorkflowDAGException(msg)

                # create instance of WorkflowStep class depending on context
                node['node'] = self._context_classes[node['source_context']](
                    self._job,
                    node['step'],
                    self._apps[node['step']['app_name']],
                    self._context_uris['inputs'][node['source_context']],
                    self._parameters,
                    self._config,
                    self._parsed_context_uris['steps'][node['source_context']],
                    node['contexts'],
                    node['source_context'],
                    **{
                        node['source_context']:\
                            self._context_options[node['source_context']]
                    }
                )

                if not node['node'].initialize():
                    msg = 'cannot initialize graph node: {}'.format(node_name)
                    Log.an().error(msg)
                    raise WorkflowDAGException(msg)


    def to_dict(self):
        """
        Return dict representation of graph.

        Args:
            None.

        Returns:
            Dict representation of graph.

        """
        return nx.to_dict_of_dicts(self._graph)
