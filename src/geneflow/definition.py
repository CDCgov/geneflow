"""This module contains the GeneFlow Definition class."""

import copy
import pprint

import cerberus
import yaml

from geneflow.log import Log

GF_VERSION = 'v1.0'

WORKFLOW_SCHEMA = {
    'v1.0': {
        'gfVersion': {
            'type': 'string', 'default': GF_VERSION, 'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string', 'default': 'workflow', 'allowed': ['workflow']
        },
        'workflow_id': {'type': 'string', 'default': ''},
        'name': {'type': 'string', 'required': True},
        'description': {'type': 'string', 'required': True},
        'repo_uri': {'type': 'string', 'default': ''},
        'documentation_uri': {'type': 'string', 'default': ''},
        'version': {'type': 'string', 'required': True},
        'public': {'type': 'boolean', 'default': False},
        'enable': {'type': 'boolean', 'default': True},
        'username': {'type': 'string', 'default': 'user'},
        'inputs': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': ['File', 'Directory', 'Any']
                    },
                    'default': {'type': 'string', 'default': ''},
                    'enable': {'type': 'boolean', 'default': True},
                    'visible': {'type': 'boolean', 'default': True},
                    'value': {'type': 'string', 'default': ''}
                }
            }
        },
        'parameters': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': [
                            'File', 'Directory', 'string', 'int',
                            'float', 'double', 'long', 'Any'
                        ]
                    },
                    'default': {'nullable': True, 'default': None},
                    'enable': {'type': 'boolean', 'default': True},
                    'visible': {'type': 'boolean', 'default': True},
                    'value': {'nullable': True, 'default': None}
                }
            }
        },
        'final_output': {
            'type': 'list', 'schema': {'type': 'string'}, 'default': []
        },
        'steps': {
            'type': 'dict',
            'required': True,
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'step_id': {'type': 'string', 'default': ''},
                    'name': {'type': 'string', 'default': ''},
                    'app_id': {'type': 'string', 'default': ''},
                    'app_name': {
                        'type': 'string',
                        'required': True,
                        'excludes': 'app'
                    },
                    'app': {
                        'type': 'string',
                        'required': True,
                        'excludes': 'app_name'
                    },
                    'depend': {'type': 'list', 'default': []},
                    'number': {'type': 'integer', 'default': 0},
                    'letter': {'type': 'string', 'default': ''},
                    'map': {
                        'type': 'dict',
                        'default': {'uri': '', 'regex': ''},
                        'schema': {
                            'uri': {'type': 'string', 'default': ''},
                            'regex': {'type': 'string', 'default': ''}
                        }
                    },
                    'template': {
                        'type': 'dict',
                        'allow_unknown': True,
                        'schema': {
                            'output': {'type': 'string', 'required': True}
                        }
                    },
                    'execution': {
                        'type': 'dict',
                        'default': {'context': 'local', 'method': 'auto'},
                        'schema': {
                            'context': {
                                'type': 'string',
                                'default': 'local',
                                'allowed': ['local', 'agave']
                            },
                            'method': {
                                'type': 'string',
                                'default': 'auto',
                                'allowed': [
                                    'auto',
                                    'package',
                                    'cdc-shared-package',
                                    'singularity',
                                    'cdc-shared-singularity',
                                    'docker',
                                    'environment',
                                    'module'
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
}

APP_SCHEMA = {
    'v1.0': {
        'gfVersion': {
            'type': 'string',
            'default': GF_VERSION,
            'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string',
            'default': 'app',
            'allowed': ['app']
        },
        'app_id': {'type': 'string', 'default': ''},
        'name': {'type': 'string', 'required': True},
        'description': {'type': 'string', 'maxlength': 64, 'required': True},
        'repo_uri': {'type': 'string', 'default': ''},
        'version': {'type': 'string', 'default': ''},
        'public': {'type': 'boolean', 'default': True},
        'username': {'type': 'string', 'default': 'user'},
        'inputs': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': ['File', 'Directory', 'Any']
                    },
                    'default': {'type': 'string', 'default': ''},
                    'value': {'type': 'string', 'default': ''}
                }
            }
        },
        'parameters': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'label': {'type': 'string', 'required': True},
                    'description': {'type': 'string', 'default': ''},
                    'type': {
                        'type': 'string',
                        'required': True,
                        'default': 'Any',
                        'allowed': [
                            'File', 'Directory', 'string', 'int',
                            'float', 'double', 'long', 'Any'
                        ]
                    },
                    'default': {'nullable': True, 'default': None},
                    'value': {'nullable': True, 'default': None}
                }
            }
        },
        'definition': {
            'type': 'dict',
            'required': True,
            'valueschema': {'type': 'dict'}
        }
    }
}

JOB_SCHEMA = {
    'v1.0': {
        'gfVersion': {
            'type': 'string',
            'default': GF_VERSION,
            'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string',
            'default': 'job',
            'allowed': ['job']
        },
        'job_id': {'type': 'string', 'default': ''},
        'username': {'type': 'string', 'default': 'user'},
        'name': {'type': 'string', 'required': True},
        'workflow_id': {'type': 'string', 'default': ''},
        'workflow_name': {'type': 'string', 'default': ''},
        'output_uri': {'type': 'string', 'required': True},
        'work_uri': {
            'type': 'dict',
            'required': True,
            'valueschema': {'type': 'string'}
        },
        'no_output_hash': {
            'type': 'boolean',
            'default': False,
            'coerce': (lambda s: str(s).lower() in ['true','yes','1'])
        },
        'inputs': {
            'type': 'dict', 'default': {}, 'valueschema': {'type': 'string'}
        },
        'parameters': {
            'type': 'dict', 'default': {}
        },
        'final_output': {
            'type': 'list', 'schema': {'type': 'string'}, 'default': []
        },
        'execution': {
            'type': 'dict',
            'default': {
                'context': {'default': 'local'},
                'method': {'default': 'auto'}
            },
            'schema': {
                'context': {
                    'type': 'dict',
                    'default': {'default': 'local'},
                    'allow_unknown': True,
                    'schema': {
                        'default': {
                            'type': 'string',
                            'default': 'local',
                        }
                    },
                    'valueschema': {
                        'type': 'string',
                        'default': 'local',
                        'allowed': ['local', 'agave']
                    }
                },
                'method': {
                    'type': 'dict',
                    'default': {'default': 'auto'},
                    'allow_unknown': True,
                    'schema': {
                        'default': {
                            'type': 'string',
                            'default': 'auto'
                        }
                    },
                    'valueschema': {
                        'type': 'string',
                        'default': 'auto',
                        'allowed': [
                            'auto',
                            'package',
                            'cdc-shared-package',
                            'singularity',
                            'cdc-shared-singularity',
                            'docker',
                            'environment',
                            'module'
                        ]
                    }
                }
            }
        },
        'notifications': {
            'type': 'list',
            'default': [],
            'schema': {
                'type': 'dict',
                'default': {},
                'schema': {
                    'url': {'type': 'string', 'required': True},
                    'to': {
                        'anyof': [
                            {'type': 'string', 'required': True},
                            {'type': 'list', 'required': True}
                        ],
                    },
                    'events': {'type': 'string', 'default': '*'}
                }
            }
        }
    }
}


class Definition:
    """
    GeneFlow Definition class.

    The Definition class is used to load and validate workflow
    definition YAML file and job definition YAML file.
    """

    def __init__(self):
        """Initialize Definition class with default values."""
        self._apps = {}
        self._workflows = {}
        self._jobs = {}


    @classmethod
    def load_yaml(cls, yaml_path):
        """
        Load a multi-doc yaml file.

        Read a multi-doc yaml file and return a list of dicts. Only basic YAML
        validation is performed in this method.

        Args:
            yaml_path: path to multi-doc YAML file.

        Returns:
            List of dicts.

        """
        try:
            with open(yaml_path, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().error(
                'cannot read yaml file: %s [%s]', yaml_path, str(err)
            )
            return False

        try:
            yaml_dict = list(yaml.safe_load_all(yaml_data))
        except yaml.YAMLError as err:
            Log.an().error('invalid yaml: %s [%s]', yaml_path, str(err))
            return False

        return yaml_dict


    def load(self, yaml_path):
        """
        Load and validate GeneFlow definition from a multi-doc YAML file.

        Read a GeneFlow definition file, which can contain apps, workflows,
        and jobs. Loaded docs are appended to the _apps, _workflows, and _jobs
        arrays. Load may be called multiple times. Docs are only added if
        successfully validated.

        Args:
            yaml_path: path to GeneFlow YAML definition file.

        Returns:
            On success: True
            On failure: False.

        """
        # load multi-doc yaml file
        gf_def = self.load_yaml(yaml_path)
        if gf_def is False:
            Log.an().error('cannot load yaml file: %s', yaml_path)
            return False

        # iterate through yaml docs
        for gf_doc in gf_def:
            # class must be specified, either app or workflow
            if 'class' not in gf_doc:
                Log.a().error('unspecified document class')
                return False

            if gf_doc['class'] == 'app':
                if 'apps' in gf_doc:
                    # this is a list of apps
                    for app in gf_doc['apps']:
                        if not self.add_app(app):
                            Log.an().error(
                                'invalid app in definition: %s', yaml_path
                            )
                            return False

                else:
                    # only one app
                    if not self.add_app(gf_doc):
                        Log.an().error(
                            'invalid app in definition: %s', yaml_path
                        )
                        return False

            elif gf_doc['class'] == 'workflow':
                # only one workflow per yaml file allowed
                if not self.add_workflow(gf_doc):
                    Log.an().error(
                        'invalid workflow in definition: %s', yaml_path
                    )
                    return False

            elif gf_doc['class'] == 'job':
                if 'jobs' in gf_doc:
                    # this is a list of jobs
                    for job in gf_doc['jobs']:
                        if not self.add_job(job):
                            Log.an().error(
                                'invalid job in definition: %s', yaml_path
                            )
                            return False

                else:
                    # only one job
                    if not self.add_job(gf_doc):
                        Log.an().error(
                            'invalid job in definition: %s', yaml_path
                        )
                        return False

            else:
                Log.a().error('invalid document class: %s', gf_doc['class'])
                return False

        return True


    @classmethod
    def validate_app(cls, app_def):
        """Validate app definition."""
        validator = cerberus.Validator(APP_SCHEMA[GF_VERSION])
        valid_def = validator.validated(app_def)

        if not valid_def:
            Log.an().error(
                'app validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        return valid_def


    @classmethod
    def calculate_step_numbering(cls, workflow_dict):
        """
        Calculate step numbering for a workflow.

        Use a topological sort algorithm to calculate step number and validate
        the DAG. Return a workflow dict with populated 'number' and 'letter'
        numbering.

        Args:
            workflow_dict: Dict of workflow to number.

        Returns:
            On success: A workflow dict with step numbers.
            On failure: False.

        """
        # initial step number
        number = 1

        steps = workflow_dict['steps']

        # indicate if step has been traversed
        step_status = {}
        for step in steps:
            step_status[step] = False

        all_done = False
        while not all_done:
            all_done = True
            steps_done = [] # steps to be set to done on next iter
            for step in steps:
                if not step_status[step]:
                    all_done = False # at least one step found
                    # get status of all dependencies, and make sure they're
                    # valid
                    dep_list = []
                    for depend in steps[step]['depend']:
                        if depend not in step_status:
                            Log.an().error(
                                'invalid step dependency: %s', depend
                            )
                            return False

                        dep_list.append(step_status[depend])

                    if not dep_list or all(dep_list):
                        # either no dependencies, or all have been traversed
                        # set step number, allowing ties
                        steps[step]['number'] = number
                        # add step to list of traversed
                        steps_done.append(step)

            if not all_done and not steps_done:
                # if steps remaining, but none have satisfied dependencies
                Log.an().error('cycles found in graph')
                return False

            # mark all steps in steps_done as done, set letter if duplicate
            # step number
            letter = ord('a') # parallel steps labeled starting at 'a'
            for step in sorted(steps_done):
                step_status[step] = True
                if len(steps_done) > 1:
                    steps[step]['letter'] = chr(letter)
                    letter += 1

            # increment step number
            number += 1

        return workflow_dict


    @classmethod
    def validate_workflow(cls, workflow_def):
        """Validate workflow definition."""
        validator = cerberus.Validator(WORKFLOW_SCHEMA[GF_VERSION])
        valid_def = validator.validated(workflow_def)

        if not valid_def:
            Log.an().error(
                'workflow validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        numbered_def = cls.calculate_step_numbering(copy.deepcopy(valid_def))
        if not numbered_def:
            Log.an().error('invalid workflow step dependencies')
            return False

        for step_name, step in valid_def['steps'].items():
            step['name'] = step_name

        return numbered_def


    @classmethod
    def validate_job(cls, job_def):
        """Validate job definition."""
        validator = cerberus.Validator(JOB_SCHEMA[GF_VERSION])
        valid_def = validator.validated(job_def)

        if not valid_def:
            Log.an().error(
                'job validation error: \n%s',
                pprint.pformat(validator.errors)
            )
            return False

        return valid_def


    def add_app(self, app_def):
        """
        Validate and add app to list.

        Args:
            app_def: dict of app definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_app(app_def)
        if not valid_def:
            Log.an().error('invalid app:\n%s', yaml.dump(app_def))
            return False

        if valid_def['name'] in self._apps:
            Log.an().error('duplicate app name: %s', valid_def['name'])
            return False

        self._apps[valid_def['name']] = valid_def

        return True


    def add_workflow(self, workflow_def):
        """
        Validate and add workflow to list.

        Args:
            workflow_def: dict of workflow definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_workflow(workflow_def)
        if not valid_def:
            Log.an().error('invalid workflow:\n%s', yaml.dump(workflow_def))
            return False

        if valid_def['name'] in self._workflows:
            Log.an().error('duplicate workflow name: %s', valid_def['name'])
            return False

        self._workflows[valid_def['name']] = valid_def

        return True


    def add_job(self, job_def):
        """
        Validate and add job to list.

        Args:
            job_def: dict of job definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_job(job_def)
        if not valid_def:
            Log.an().error('invalid job:\n%s', yaml.dump(job_def))
            return False

        if valid_def['name'] in self._jobs:
            Log.an().error('duplicate job name: %s', valid_def['name'])
            return False

        self._jobs[valid_def['name']] = valid_def

        return True


    def apps(self, name=None):
        """
        Get app dicts.

        Return either all apps (name=None), or a specific app from dict. If
        dict key doesn't exist, an empty dict is returned and an error is
        logged.

        Args:
            name: name of app to return, None (default) indicates all apps.

        Returns:
            Dict of apps.

        """
        if name is None:
            return self._apps

        if name not in self._apps:
            Log.an().error('app not found: %s', name)
            return {}

        return self._apps[name]


    def workflows(self, name=None):
        """
        Get workflow dicts.

        Return either all workflows (name=None), or a specific workflow from
        dict. If dict key doesn't exist, an empty dict is returned and an error
        is logged.

        Args:
            name: name of workflow to return, None (default) indicates all
            workflows.

        Returns:
            Dict of workflows.

        """
        if name is None:
            return self._workflows

        if name not in self._workflows:
            Log.an().error('workflow not found: %s', name)
            return {}

        return self._workflows[name]


    def jobs(self, name=None):
        """
        Get job dicts.

        Return either all jobs (name=None), or a specific job from dict. If
        dict key doesn't exist, an empty dict is returned and an error is
        logged.

        Args:
            name: name of job to return, None (default) indicates all
            jobs.

        Returns:
            Dict of jobs.

        """
        if name is None:
            return self._jobs

        if name not in self._jobs:
            Log.an().error('job not found: %s', name)
            return {}

        return self._jobs[name]
