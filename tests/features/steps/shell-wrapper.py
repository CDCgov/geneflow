import os
from pprint import pprint
import sys


from geneflow.shell_wrapper import ShellWrapper

@given('I create a "{shell}" Shell instance')
def step_impl(context, shell):

    context.shell[shell] = {}
    context.shell[shell]['shell'] = ShellWrapper()

@when('I run the invoke method for the "{shell}" Shell instance with a valid argument')
def step_impl(context, shell):

    context.shell[shell]['invoke_correct_result'] = context.shell[shell]['shell'].invoke("echo 'Hello World!'")

@then('I see a valid response for invoke method of the "{shell}" Shell instance')
def step_impl(context, shell):

    assert context.shell[shell]['invoke_correct_result'] == b'Hello World!\n'

@when('I run the invoke method for the "{shell}" Shell instance with an invalid argument')
def step_impl(context, shell):

    context.shell[shell]['invoke_incorrect_result'] = context.shell[shell]['shell'].invoke("echo-invalid 'Hello World!'")

@then('I see a False return value for the invoke method of the "{shell}" Shell instance')
def step_impl(context, shell):

    assert context.shell[shell]['invoke_incorrect_result'] == False

@when('I run the spawn method for the "{shell}" Shell instance with a valid argument')
def step_impl(context, shell):

    context.shell[shell]['spawn_proc'] = context.shell[shell]['shell'].spawn("sleep 30")

@then('I see a valid response for the spawn method of the "{shell}" Shell instance')
def step_impl(context, shell):

    assert context.shell[shell]['spawn_proc']
    context.shell[shell]['spawn_proc'].wait()
    assert context.shell[shell]['spawn_proc'].returncode == 0

@when('I run the spawn method for the "{shell}" Shell instance with an invalid argument')
def step_impl(context, shell):

    context.shell[shell]['spawn_proc'] = context.shell[shell]['shell'].spawn("sleep-invalid 30")

@then('I see a negative result for the spawn method of the "{shell}" Shell instance')
def step_impl(context, shell):

    if context.shell[shell]['spawn_proc']:
        # valid process, check return value
        context.shell[shell]['spawn_proc'].wait()
        assert context.shell[shell]['spawn_proc'].returncode != 0
    else:
        assert context.shell[shell]['spawn_proc'] == False

@when('I call the is_running method for the "{shell}" Shell instance')
def step_impl(context, shell):

    context.shell[shell]['process_status'] = context.shell[shell]['shell'].is_running(context.shell[shell]['spawn_proc'])

@then('I see a value of True returned for is_running method of the "{shell}" Shell instance')
def step_impl(context, shell):

    assert context.shell[shell]['process_status'] == True


