

import geneflow.cli.run
import geneflow.cli.install_workflow
from geneflow.data_manager import DataManager

from argparse import Namespace
from pathlib import Path
from pprint import pprint
from slugify import slugify


@given('The "{wf_context}" "{workflow}" workflow has been installed')
def step_impl(context, wf_context, workflow):

    args = None
    if wf_context == 'local':
        args = Namespace(
            workflow_path='./data/workflows/{}-local'.format(workflow),
            git=context.config.userdata.get('workflows_{}'.format(workflow)),
            git_branch=None,
            force=True,
            name=None,
            asset=None,
            prefix=None,
            clean=True,
            make_apps=True,
            config=None,
            environment=None,
            agave_params=None,
            agave_username=None,
            agave_apps_prefix=None,
            agave_execution_system=None,
            agave_deployment_system=None,
            agave_apps_dir=None,
            agave_test_data_dir=None,
            agave_publish=False,
            agave_test_data=False
        )
    elif wf_context == 'agave':
        args = Namespace(
            workflow_path='./data/workflows/{}-agave'.format(workflow),
            git=context.config.userdata.get('workflows_{}'.format(workflow)),
            git_branch=None,
            force=True,
            name=None,
            asset=None,
            prefix=None,
            clean=True,
            make_apps=True,
            config='./test.conf',
            environment='local',
            agave_params=None,
            agave_username=None,
            agave_apps_prefix=context.config.userdata.get('agave_apps_prefix'),
            agave_execution_system=context.config.userdata.get('agave_execution_system'),
            agave_deployment_system=context.config.userdata.get('agave_deployment_system'),
            agave_apps_dir=context.config.userdata.get('agave_apps_dir'),
            agave_test_data_dir=None,
            agave_publish=False,
            agave_test_data=False
        )
    else:
        print('Invalid workflow context: {}'.format(wf_context))
        assert False

    wf_name = '{}-{}'.format(workflow, wf_context)
    context.workflows[wf_name] = {}

    assert geneflow.cli.install_workflow.install_workflow(args)


@then('The "{wf_context}" "{workflow}" workflow cannot be installed')
def step_impl(context, wf_context, workflow):

    args = None
    if wf_context == 'local':
        args = Namespace(
            workflow_path='./data/workflows/{}-local'.format(workflow),
            git=context.config.userdata.get('workflows_{}'.format(workflow)),
            git_branch=None,
            force=True,
            name=None,
            asset=None,
            prefix=None,
            clean=True,
            make_apps=True,
            config=None,
            environment=None,
            agave_params=None,
            agave_username=None,
            agave_apps_prefix=None,
            agave_execution_system=None,
            agave_deployment_system=None,
            agave_apps_dir=None,
            agave_test_data_dir=None,
            agave_publish=False,
            agave_test_data=False
        )
    elif wf_context == 'agave':
        args = Namespace(
            workflow_path='./data/workflows/{}-agave'.format(workflow),
            git=context.config.userdata.get('workflows_{}'.format(workflow)),
            git_branch=None,
            force=True,
            name=None,
            asset=None,
            prefix=None,
            clean=True,
            make_apps=True,
            config='./test.conf',
            environment='local',
            agave_params=None,
            agave_username=None,
            agave_apps_prefix=context.config.userdata.get('agave_apps_prefix'),
            agave_execution_system=context.config.userdata.get('agave_execution_system'),
            agave_deployment_system=context.config.userdata.get('agave_deployment_system'),
            agave_apps_dir=context.config.userdata.get('agave_apps_dir'),
            agave_test_data_dir=None,
            agave_publish=False,
            agave_test_data=False
        )
    else:
        print('Invalid workflow context: {}'.format(wf_context))
        assert False

    wf_name = '{}-{}'.format(workflow, wf_context)
    context.workflows[wf_name] = {}

    assert geneflow.cli.install_workflow.install_workflow(args) == False


@when('I run the "{wf_context}" "{workflow}" workflow with the following inputs and parameters')
def step_impl(context, wf_context, workflow):

    args = None
    data = None
    if wf_context == 'local':
        data = [
            'output_uri=./data/workflows/output'
        ]
    elif wf_context == 'agave':
        data = [
            'output_uri=./data/workflows/output',
            'work_uri.agave={}'.format(context.config.userdata.get('agave_work_uri')),
            'execution.context.default=agave'
        ]
    else:
        print('Invalid workflow context: {}'.format(wf_context))
        assert False

    for row in context.table:
        if row['type'] == 'input':
            data.append(
                'inputs.{}=./data/workflows/{}-{}/{}'.format(
                    row['name'],
                    workflow,
                    wf_context,
                    row['value']
                )
            )
        elif row['type'] == 'parameter':
            data.append('parameters.{}={}'.format(row['name'], row['value']))
        else:
            print('Invalid input or parameter type: {}'.format(row['type']))
            assert False

    args = Namespace(
        workflow='./data/workflows/{}-{}'.format(workflow, wf_context),
        job_yaml=None,
        data=data,
        log_level='debug'
    )

    result = geneflow.cli.run.run(args)
    wf_name = '{}-{}'.format(workflow, wf_context)
    context.workflows[wf_name]['result'] = result
    assert all(result)


@then('The "{wf_context}" "{workflow}" workflow "{step}" step produces an output file called "{output_name}" with the following contents')
def step_impl(context, wf_context, workflow, step, output_name):

    wf_name = '{}-{}'.format(workflow, wf_context)
    job = context.workflows[wf_name]['result'][0]

    # construct path of expected output file
    step_output_file = '{}/{}-{}/{}/{}'.format(
        job['output_uri'],
        slugify(job['name']), job['job_id'][:8],
        slugify(step),
        output_name
    )

    # make sure it exists
    assert Path(step_output_file).exists()

    # read file
    with open(step_output_file) as f:
        file_contents = [line.strip() for line in f]

    # convert table into list
    expected_contents = [row['line'] for row in context.table]

    assert file_contents == expected_contents
