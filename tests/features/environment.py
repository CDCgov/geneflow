

import inspect, os, shutil, sys
from behave import *
from pprint import pprint

from geneflow.config import Config
from geneflow.data import DataSource
from geneflow.uri_parser import URIParser



def clear_database(context):

    try: gfdb = DataSource(context.geneflow_config['database'])
    except Exception as err:
        assert False

    # delete all workflows from database
    workflows = gfdb.get_workflows()
    assert workflows is not False

    for workflow in workflows:
        assert gfdb.delete_workflow_by_id(workflow['id'])

    gfdb.commit()

    # delete all apps from database
    apps = gfdb.get_apps()
    assert apps is not False

    for app in apps:
        assert gfdb.delete_app_by_id(app['id'])

    gfdb.commit()


def before_all(context):

    # load workflow config file based on env
    cfg = Config()
    assert cfg.load('./test.conf')
    geneflow_config = cfg.config(
        env=context.config.userdata.get('environment', 'local')
    )
    if not geneflow_config:
        raise ValueError('Error loading geneflow config file')
    context.geneflow_config = geneflow_config

    # delete all items from database
    clear_database(context)

    # setup dict key for agave connection
    context.agave = {}


def before_feature(context, feature):

    if feature.name == 'Shell Wrapper':
        context.shell = {}

    elif feature.name == 'Workflows':
        context.workflows = {}


def after_feature(context, feature):

    if feature.name == 'Workflows':
        # delete workflows and runs
        for workflow in context.workflows:
            shutil.rmtree('./data/workflows/{}'.format(workflow))
        shutil.rmtree('./data/workflows/output')


def before_scenario(context, scenario):

    # delete all items from database
    clear_database(context)


