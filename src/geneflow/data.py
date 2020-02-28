"""
GeneFlow Data Classes.

This module contains SQLAlchemy classes for each GeneFlow table and the
GeneFlow DataSource class.
"""

import datetime
import json
import os
import uuid
import yaml

from sqlalchemy import create_engine, asc, desc, case
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from geneflow.definition import Definition
from geneflow.log import Log


# global SQLAlchemy objects
Base = declarative_base()
Session = sessionmaker()


#### SQLAlchemy table definitions

class WorkflowEntity(Base):
    """SQLAlchemy table definition for the GeneFlow workflow table."""

    __tablename__ = 'workflow'

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String, default='')
    repo_uri = Column(String, default='')
    version = Column(String, default='')
    username = Column(String, default='')
    documentation_uri = Column(Text, default='')
    inputs = Column(Text, default='')
    parameters = Column(Text, default='')
    final_output = Column(Text, default='')
    public = Column(Boolean, default=False)
    enable = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now)


class AppEntity(Base):
    """SQLAlchemy table definition for the GeneFlow app table."""

    __tablename__ = 'app'

    id = Column(String, primary_key=True)
    name = Column(String, default='')
    description = Column(String, default='')
    repo_uri = Column(String, default='')
    version = Column(String, default='')
    username = Column(String, default='')
    definition = Column(Text, default='')
    inputs = Column(Text, default='')
    parameters = Column(Text, default='')
    public = Column(Boolean, default=False)


class StepDependencyEntity(Base):
    """SQLAlchemy table definition for the GeneFlow depend table."""

    __tablename__ = 'depend'

    child_id = Column(String, primary_key=True)
    parent_id = Column(String, primary_key=True)


class StepEntity(Base):
    """SQLAlchemy table definition for the GeneFlow step table."""

    __tablename__ = 'step'

    id = Column(String, primary_key=True)
    name = Column(String, default='')
    number = Column(Integer, default=1)
    letter = Column(String, default='')
    workflow_id = Column(String)
    app_id = Column(String)
    map_uri = Column(String, default='')
    map_regex = Column(String, default='')
    template = Column(Text, default='')
    exec_context = Column(String, default='local')
    exec_method = Column(String, default='auto')


class JobEntity(Base):
    """SQLAlchemy table definition for the GeneFlow job table."""

    __tablename__ = 'job'

    id = Column(String, primary_key=True)
    workflow_id = Column(String, default='')
    name = Column(String, default='')
    username = Column(String, default='')
    work_uri = Column(String, default='')
    no_output_hash = Column(Boolean, default=False)
    status = Column(String, default='PENDING')
    queued = Column(DateTime, default=datetime.datetime.now)
    started = Column(DateTime)
    finished = Column(DateTime)
    msg = Column(String, default='')
    inputs = Column(Text, default='')
    parameters = Column(Text, default='')
    output_uri = Column(String, default='')
    final_output = Column(Text, default='')
    exec_context = Column(Text, default='')
    exec_method = Column(Text, default='')
    notifications = Column(Text, default='[]')


class JobStepEntity(Base):
    """SQLAlchemy table definition for the GeneFlow job_step table."""

    __tablename__ = 'job_step'

    job_id = Column(String, primary_key=True)
    step_id = Column(String, primary_key=True)
    status = Column(String, default='PENDING')
    detail = Column(Text)
    msg = Column(String, default='')


#### Main GeneFlow database class


class DataSourceException(Exception):
    """Custom exception for DataSource."""

    pass


class DataSource:
    """
    Main data class for GeneFlow.

    This class handles all reading/writing from/to the database.
    """

    def __init__(self, db_conf):
        """
        Instantiate the DataSource class.

        Args:
            self: class instance.
            db_conf: database configuration dict.

        Returns:
            Class instance.

        """
        self._db_conf = db_conf
        if db_conf['type'] == 'mysql':
            try:
                self._engine = create_engine(
                    'mysql+pymysql://{}:{}@{}/{}'.format(
                        db_conf['user'],
                        db_conf['password'],
                        db_conf['host'],
                        db_conf['database']
                    )
                )
            except SQLAlchemyError as err:
                Log.an().error('sql exception [%s]', str(err))
                raise DataSourceException('DataSource() init failed')

        elif db_conf['type'] == 'sqlite':
            try:
                self._engine = create_engine('sqlite:///{}'.format(
                    db_conf['path']
                ))
            except SQLAlchemyError as err:
                Log.an().error('sql exception [%s]', str(err))
                raise DataSourceException('DataSource() init failed')

        else:
            Log.an().error('invalid db type: %s', db_conf['type'])
            raise DataSourceException('DataSource() init failed')

        self._session = Session(bind=self._engine)


    def commit(self):
        """
        Commit current transaction to the database and closes the session.

        Args:
            self: class instance.

        Returns:
            True.

        """
        self._session.commit()
        self._session.close()

        return True


    def rollback(self):
        """
        Rollback current database transaction.

        Args:
            self: class instance.

        Returns:
            True.

        """
        self._session.rollback()

        return True


    @staticmethod
    def result_dict(result):
        """
        Convert SQLAlchemy result to dict array.

        Args:
            result: SQLAlchemy result to convert.

        Returns:
            Dict array of results.

        """
        result_dict = [row.__dict__ for row in result]

        return result_dict


    #### Methods for Normalized Definitions from DB ####


    def get_job_def_by_id(self, job_id):
        """
        Return normalized job definition.

        Args:
            job_id: ID of job.

        Returns:
            On success: normalized job definition.
            On failure: False.

        """
        try:
            result = self._session.query(
                JobEntity.id,
                JobEntity.username,
                JobEntity.name,
                JobEntity.workflow_id,
                WorkflowEntity.name,
                JobEntity.output_uri,
                JobEntity.work_uri,
                JobEntity.no_output_hash,
                JobEntity.inputs,
                JobEntity.parameters,
                JobEntity.final_output,
                JobEntity.exec_context,
                JobEntity.exec_method,
                JobEntity.notifications
            ).\
                filter(JobEntity.id == job_id).\
                filter(WorkflowEntity.id == JobEntity.workflow_id).\
                all()

            result_dict = [
                {
                    'job_id': row[0],
                    'username': row[1],
                    'name': row[2],
                    'workflow_id': row[3],
                    'workflow_name': row[4],
                    'output_uri': row[5],
                    'work_uri': json.loads(row[6]),
                    'no_output_hash': row[7],
                    'inputs': json.loads(row[8]),
                    'parameters': json.loads(row[9]),
                    'final_output': json.loads(row[10]),
                    'execution': {
                        'context': json.loads(row[11]),
                        'method': json.loads(row[12])
                    },
                    'notifications': json.loads(row[13])
                } for row in result
            ]

        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        # should have just one record
        if not result_dict:
            return {}

        return result_dict[0]


    def get_depend_def_by_step_id(self, step_id):
        """
        Get normalized dependency list for a step.

        Args:
            step_id: ID of step.

        Returns:
            On success: List of dependent step names.
            On failure: False.

        """
        try:
            result = self._session.query(StepEntity.name).\
                filter(StepEntity.id == StepDependencyEntity.parent_id).\
                filter(StepDependencyEntity.child_id == step_id).\
                all()

            result_list = [
                row[0] for row in result
            ]

        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_list


    def get_step_defs_by_workflow_id(self, workflow_id):
        """
        Get normalized step definitions for a workflow.

        Args:
            workflow_id: workflow ID.

        Returns:
            On success: normalized list of step dicts.
            On failure: False.

        """
        try:
            result = self._session.query(
                StepEntity.id,
                StepEntity.name,
                StepEntity.app_id,
                AppEntity.name,
                StepEntity.number,
                StepEntity.letter,
                StepEntity.map_uri,
                StepEntity.map_regex,
                StepEntity.template,
                StepEntity.exec_context,
                StepEntity.exec_method
            ).\
                filter(StepEntity.workflow_id == workflow_id).\
                filter(StepEntity.app_id == AppEntity.id).\
                all()

            result_dict = {
                row[1]: {
                    'step_id': row[0],
                    'name': row[1],
                    'app_id': row[2],
                    'app_name': row[3],
                    'number': row[4],
                    'letter': row[5],
                    'map': {
                        'uri': row[6],
                        'regex': row[7],
                    },
                    'template': json.loads(row[8]),
                    'execution': {
                        'context': row[9],
                        'method': row[10]
                    },
                    'depend': []
                } for row in result
            }
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        # get list of dependencies for each step
        for step in result_dict.values():
            depends = self.get_depend_def_by_step_id(step['step_id'])
            if depends is False:
                Log.an().error(
                    'cannot get dependencies for step: %s', step['name']
                )
                return False

            step['depend'] = depends

        return result_dict


    def get_workflow_def_by_id(self, workflow_id):
        """
        Get a normalized workflow definition.

        Includes step definitions.

        Args:
            workflow_id: workflow ID.

        Returns:
            On success: normalized workflow dict.
            On failure: False.

        """
        try:
            result = self._session.query(
                WorkflowEntity.id,
                WorkflowEntity.name,
                WorkflowEntity.description,
                WorkflowEntity.username,
                WorkflowEntity.repo_uri,
                WorkflowEntity.version,
                WorkflowEntity.documentation_uri,
                WorkflowEntity.inputs,
                WorkflowEntity.parameters,
                WorkflowEntity.final_output,
                WorkflowEntity.public,
                WorkflowEntity.enable
            ).\
                filter(WorkflowEntity.id == workflow_id).\
                all()

            result_dict = [
                {
                    'workflow_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'username': row[3],
                    'repo_uri': row[4],
                    'version': row[5],
                    'documentation_uri': row[6],
                    'inputs': json.loads(row[7]),
                    'parameters': json.loads(row[8]),
                    'final_output': json.loads(row[9]),
                    'public': row[10],
                    'enable': row[11],
                    'steps': {}
                } for row in result
            ]

        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        # should have just one record
        if not result_dict:
            return {}

        result_dict = result_dict[0]

        # get steps
        steps = self.get_step_defs_by_workflow_id(workflow_id)
        if not steps:
            Log.an().error(
                'cannot get step definitions for workflow: workflow_id=%s',
                workflow_id
            )
            return False

        result_dict['steps'] = steps

        return result_dict


    def get_app_defs_by_workflow_id(self, workflow_id):
        """
        Get normalized app definitions.

        Args:
            workflow_id: workflow ID of apps to return.

        Returns:
            On success: dict of app dicts.
            On failure: False.

        """
        try:
            result = self._session.query(
                AppEntity.id,
                AppEntity.name,
                AppEntity.description,
                AppEntity.repo_uri,
                AppEntity.version,
                AppEntity.public,
                AppEntity.username,
                AppEntity.inputs,
                AppEntity.parameters,
                AppEntity.definition
            ).\
                filter(StepEntity.workflow_id == workflow_id).\
                filter(StepEntity.app_id == AppEntity.id).\
                all()

            result_dict = {
                row[1]: {
                    'app_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'repo_uri': row[3],
                    'version': row[4],
                    'public': row[5],
                    'username': row[6],
                    'inputs': json.loads(row[7]),
                    'parameters': json.loads(row[8]),
                    'definition': json.loads(row[9])
                } for row in result
            }

        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    #### Workflow Entity ####


    def get_workflows(self):
        """
        Get all workflows from database.

        Args:
            None

        Returns:
            List of workflow dicts.

        """
        try:
            result = self._session.query(WorkflowEntity).all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_workflow_by_name(self, name):
        """
        Get workflow record matching name.

        Args:
            name: workflow name.

        Returns:
            Dict of workflow record.

        """
        try:
            result = self._session.query(WorkflowEntity).\
                filter(WorkflowEntity.name == name).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_workflow_by_id(self, workflow_id):
        """
        Get workflow record matching ID.

        Args:
            workflow_id: workflow id.

        Returns:
            Dict of workflow record.

        """
        try:
            result = self._session.query(WorkflowEntity).\
                filter(WorkflowEntity.id == workflow_id).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_workflow(self, data):
        """
        Add workflow record to database.

        Args:
            data: dict of workflow record.

        Returns:
            On success: new workflow id.
            On failure: False.

        """
        workflow_id = str(uuid.uuid4()).replace('-', '')
        try:
            self._session.add(WorkflowEntity(
                id=workflow_id,
                name=data['name'],
                description=data['description'],
                username=data['username'],
                repo_uri=data['repo_uri'],
                version=data['version'],
                documentation_uri=data['documentation_uri'],
                inputs=data['inputs'],
                parameters=data['parameters'],
                final_output=data['final_output'],
                public=data['public'],
                enable=data['enable'],
                created=None,
                modified=None
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return workflow_id


    def update_workflow(self, workflow_id, data):
        """
        Update workflow matching ID.

        Args:
            workflow_id: ID of workflow to update.
            data: dict of new workflow record.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(WorkflowEntity).\
                filter(WorkflowEntity.id == workflow_id).\
                update(data)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_workflow_by_id(self, workflow_id):
        """
        Delete workflow record matching ID.

        Also delete all database records pointing to this workflow ID
        (including jobs, steps, depends, and job_steps).

        Args:
            workflow_id: ID of workflow to delete.

        Returns:
            On success: True.
            On failure: False.

        """
        if not self.delete_job_step_by_workflow_id(workflow_id):
            return False

        if not self.delete_depend_by_workflow_id(workflow_id):
            return False

        if not self.delete_step_by_workflow_id(workflow_id):
            return False

        if not self.delete_job_by_workflow_id(workflow_id):
            return False

        try:
            self._session.query(WorkflowEntity).\
                filter(WorkflowEntity.id == workflow_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_workflow_by_name(self, name):
        """
        Delete workflow matching name.

        This method fails if more than one workflow matches.

        Args:
            name: workflow name.

        Returns:
            On success: True.
            On failure: False.

        """
        workflow = self.get_workflow_by_name(name)
        if workflow is False:
            Log.an().error('cannot get workflow by name: %s', name)
            return False

        if not workflow:
            Log.an().error('workflow "%s" not found', name)
            return False

        if len(workflow) > 1:
            Log.an().error(
                'non-unique workflow "%s", try delete by id instead', name
            )
            return False

        return self.delete_workflow_by_id(workflow[0]['id'])


    #### App Entity ####

    def get_apps(self):
        """
        Get all apps from database.

        Args:
            None

        Returns:
            On success: list of all app dicts.
            On failure: False.

        """
        try:
            result = self._session.query(AppEntity).all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_app_by_name(self, name):
        """
        Get app record matching name.

        Args:
            name: app name.

        Returns:
            On success: dict of app record.
            On failure: False.

        """
        try:
            result = self._session.query(AppEntity).\
                filter(AppEntity.name == name).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_app_by_id(self, app_id):
        """
        Get app record matching ID.

        Args:
            app_id: ID of app record.

        Returns:
            On success: dict of app record.
            On failure: False.

        """
        try:
            result = self._session.query(AppEntity).\
                filter(AppEntity.id == app_id).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_app(self, data):
        """
        Add app record to database.

        Args:
            data: dict of app record.

        Returns:
            On success: ID of new app record.
            On failure: False.

        """
        app_id = str(uuid.uuid4()).replace('-', '')
        try:
            self._session.add(AppEntity(
                id=app_id,
                name=data['name'],
                description=data['description'],
                repo_uri=data['repo_uri'],
                version=data['version'],
                username=data['username'],
                public=data['public'],
                definition=data['definition'],
                inputs=data['inputs'],
                parameters=data['parameters']
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return app_id


    def update_app(self, app_id, data):
        """
        Update app record matching ID.

        Args:
            app_id: ID of app to update.
            data: dict of new app record.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(AppEntity).\
                filter(AppEntity.id == app_id).\
                update(data)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_app_by_id(self, app_id):
        """
        Delete app matching ID.

        Args:
            app_id: ID of app to delete.

        Returns:
            On success: True.
            On failure: False.

        """
        # first check if app is linked to any steps
        try:
            count = self._session.query(StepEntity).\
                filter(StepEntity.app_id == app_id).\
                count()
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        if count > 0:
            Log.an().error('app with id "%s" still used by steps', app_id)
            return False

        # delete app
        try:
            self._session.query(AppEntity).\
                filter(AppEntity.id == app_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_app_by_name(self, name):
        """
        Delete app matching name. Fails if more than one app matches.

        Args:
            name: name of app to delete.

        Returns:
            On success: result of delete_app_by_id for matching app.
            On failure: False.

        """
        app = self.get_app_by_name(name)
        if app is False:
            Log.an().error('cannot get app by name: %s', name)
            return False

        if not app:
            Log.an().error('app "%s" not found', name)
            return False

        if len(app) > 1:
            Log.an().error(
                'non-unique app "%s", try deleting by id instead', name
            )
            return False

        return self.delete_app_by_id(app[0]['id'])


    #### StepDependency Entity ####

    def get_depend_by_child_id(self, child_id):
        """
        Get dependent entities in current session by using child ID.

        Args:
            child_id: id of a step dependency entity.

        Returns:
            On success: a dictionary of all dependent entities.
            On failure: False.

        """
        try:
            result = self._session.query(StepDependencyEntity).\
                filter(StepDependencyEntity.child_id == child_id).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_depend(self, data):
        """
        Add dependency to current session.

        Args:
            data: a dictionary with "child_id" and "parent_id" as keys.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.add(StepDependencyEntity(
                child_id=data['child_id'],
                parent_id=data['parent_id']
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_depend_by_workflow_id(self, workflow_id):
        """
        Delete StepDependencyEntity in current session by workflow_id.

        Args:
            workflow_id: The the id of the step entity object.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            # use of a sub-query instead of join for delete is required
            # for sqlite
            sub_query = self._session.query(StepEntity.id).\
                filter(StepEntity.workflow_id == workflow_id)
            self._session.query(StepDependencyEntity).\
                filter(StepDependencyEntity.child_id.in_(sub_query)).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    #### Step Entity ####

    def get_step_by_workflow_id(self, workflow_id):
        """
        Get Step Entity object in current session by using workflow_id.

        Args:
            workflow_id: the id of the StepEntity object.

        Returns:
            On success: result in dictionary.
            On failure: False.

        """
        try:
            result = self._session.query(StepEntity).\
                filter(StepEntity.workflow_id == workflow_id).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_step_dependent_names(self, step_id):
        """
        Get names of all steps (parents) on which this step (child) depends.

        Args:
            step_id: id of the child step.

        Returns:
            On success: dict of all parent steps.
            On failure: False.

        """
        try:
            result = self._session.query(StepEntity.name).\
                filter(StepDependencyEntity.child_id == step_id).\
                filter(StepDependencyEntity.parent_id == StepEntity.id).\
                all()

            result_dict = [
                {'name': row[0]} for row in result
            ]
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_step(self, data):
        """
        Add a step Entity to the current session.

        Args:
            data: a dictionary with the current keys:
                  ['workflow_id', 'app_id', 'name', 'number',
                  'letter', 'map_uri', 'map_regex','template',
                  'exec_context', 'exec_method']

        Returns:
            On success: step id of the added StepEntity object.
            On failure: Flase

        """
        step_id = str(uuid.uuid4()).replace('-', '')
        try:
            self._session.add(StepEntity(
                id=step_id,
                workflow_id=data['workflow_id'],
                app_id=data['app_id'],
                name=data['name'],
                number=data['number'],
                letter=data['letter'],
                map_uri=data['map_uri'],
                map_regex=data['map_regex'],
                template=data['template'],
                exec_context=data['exec_context'],
                exec_method=data['exec_method']
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return step_id


    def update_step(self, step_id, data):
        """
        Update a Step Entity object with a data dictionary.

        Args:
            step_id: ID of the Step Entity to work on.
            data: a data dictionary to update the Step Entity.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(StepEntity).\
                filter(StepEntity.id == step_id).\
                update(data)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_step_by_workflow_id(self, workflow_id):
        """
        Delete steps for workflow.

        Args:
            workflow_id: ID of workflow for which steps should be deleted.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(StepEntity).\
                filter(StepEntity.workflow_id == workflow_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    #### Job Entity ####

    def get_job_by_id(self, job_id):
        """
        Get a Job Entity object by id.

        Args:
            job_id: id of the Job Entity.

        Returns:
            On success: a dictionary containing the job entity.
            On failure: False.

        """
        try:
            result = self._session.query(JobEntity).\
                filter(JobEntity.id == job_id).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_pending_jobs(self):
        """
        Find pending jobs in current session.

        Args:
            None

        Returns:
            On success: A dictionary of JobEntity objects ordered by queued
                time in ascend order.
            On failure: False.

        """
        try:
            result = self._session.query(JobEntity).\
                filter(JobEntity.status == 'PENDING').\
                order_by(asc(JobEntity.queued)).\
                all()
            result_dict = self.result_dict(result)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def get_job_by_username_status(self, username, status):
        """
        Get Job Entity by user name and status.

        Args:
            username: user name.
            status: status of the job.

        Returns:
            On success: a dictionary of job entities.
            On failure: False.

        """
        def merge_dicts(dict_a, dict_b):
            """
            Merge two dictionaries (for Python versions 3.4 or lower).

            Args:
                dict_a: First dictionary.
                dict_b: Second dictionary.

            Returns:
                On success: return a new dict merging the two dicts.
                On failure: False.

            """
            dict_c = dict_a.copy()
            dict_c.update(dict_b)
            return dict_c

        try:
            query = self._session.query(
                JobEntity, WorkflowEntity.name
            )

            if username != '':
                query = query.filter(JobEntity.username == username)

            if status != '':
                query = query.filter(JobEntity.status == status)

            result = query.filter(JobEntity.workflow_id == WorkflowEntity.id).\
                order_by(desc(JobEntity.status)).\
                all()

            # convert result tuple to dict
            result_dict = [
                merge_dicts(
                    row[0].__dict__,
                    {'workflow_name': row[1]}
                ) for row in result
            ]
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_job(self, data):
        """
        Add job to current session.

        Args:
            data: a dictionary with the following keys:
                  ['workflow_id', 'name', 'username', 'work_uri', 'no_output_hash',
                  'inputs', 'parameters', 'output_uri','final_output',
                  'exec_context', 'exec_method']
        Returns:
            On success: id of the added job.
            On failure: False.

        """
        job_id = str(uuid.uuid4()).replace('-', '')
        try:
            self._session.add(JobEntity(
                id=job_id,
                workflow_id=data['workflow_id'],
                name=data['name'],
                username=data['username'],
                work_uri=data['work_uri'],
                no_output_hash=data['no_output_hash'],
                inputs=data['inputs'],
                parameters=data['parameters'],
                output_uri=data['output_uri'],
                final_output=data['final_output'],
                exec_context=data['exec_context'],
                exec_method=data['exec_method'],
                notifications=data['notifications']
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return job_id


    def update_job_status(self, job_id, status, msg):
        """
        Update job status in current session.

        Args:
            job_id: id string of the Job Entity
            status: string of the status
            msg: mesage of the status update.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobEntity).\
                filter(JobEntity.id == job_id).\
                update(
                    {
                        'status': status,
                        'msg': case(
                            [(JobEntity.msg == '', msg)],
                            else_=JobEntity.msg+'|'+msg
                        )
                    },
                    synchronize_session=False
                )
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def set_job_started(self, job_id):
        """
        Set a job to started state with time.

        Args:
            job_id: id string of the JobEntity.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobEntity).\
                filter(JobEntity.id == job_id).\
                update({'started': datetime.datetime.now()})
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def set_job_finished(self, job_id):
        """
        Set a job to finished status with time.

        Args:
            job_id: ID string of the JobEntity.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobEntity).\
                filter(JobEntity.id == job_id).\
                update({'finished': datetime.datetime.now()})
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_job_by_id(self, job_id):
        """
        Delete a job of a particular job ID.

        Args:
            job_id: ID string of the JobEntity.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobEntity).\
                filter(JobEntity.id == job_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_job_by_workflow_id(self, workflow_id):
        """
        Delete a job of a particular workflow ID.

        Args:
            job_id: ID string of the workflow.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobEntity).\
                filter(JobEntity.workflow_id == workflow_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    #### JobStep Entity ####

    def get_job_step_dependent_status(self, job_id, step_id):
        """
        Get job step dependent status with job id and step ID.

        Args:
            job_id: job id string of the JobStepEntity.
            step_id: setp id string of the JobStepEntity.

        Returns:
            On success: a dictionary of job step dependency.
            On failure: False.

        """
        try:
            result = self._session.query(
                StepDependencyEntity.parent_id,
                JobStepEntity.status
            ).\
                filter(StepDependencyEntity.child_id == step_id).\
                filter(StepDependencyEntity.parent_id == StepEntity.id).\
                filter(StepEntity.id == JobStepEntity.step_id).\
                filter(JobStepEntity.job_id == job_id).\
                all()

            result_dict = [
                {
                    'parent_id': row[0],
                    'status': row[1]
                } for row in result
            ]
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return result_dict


    def add_job_step(self, data):
        """
        Add a job step to the current session.

        Args:
            data: a dictionary with the following keys: ['step_id, 'job_id'].

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.add(JobStepEntity(
                step_id=data['step_id'],
                job_id=data['job_id'],
                detail='{}',
            ))
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def update_job_step_status(self, step_id, job_id, status, detail, msg):
        """
        Update job step status in current session.

        Args:
            step_id: step id string of the JobStepEntity.
            job_id: job id string of the JobStepEntity.
            status: status string of the JobStepEntity.
            detail: string with detailed description.
            msg: a string for message.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobStepEntity).\
                filter(JobStepEntity.step_id == step_id).\
                filter(JobStepEntity.job_id == job_id).\
                update(
                    {
                        'status': status,
                        'detail': detail,
                        'msg': case(
                            [(JobStepEntity.msg == '', msg)],
                            else_=JobStepEntity.msg+'|'+msg
                        )
                    },
                    synchronize_session=False
                )
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_job_step_by_workflow_id(self, workflow_id):
        """
        Delete JobStepEntity by workflow id.

        Args:
            workflow_id: the id string of the JobStepEntity workflow.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            # use of a sub-query instead of join for delete is required
            # for sqlite
            sub_query = self._session.query(JobEntity.id).\
                filter(JobEntity.workflow_id == workflow_id)
            self._session.query(JobStepEntity).\
                filter(JobStepEntity.job_id.in_(sub_query)).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    def delete_job_step_by_job_id(self, job_id):
        """
        Delete a JobStepEntity by job id.

        Args:
            job_id: the job id string of JobStepEntity.

        Returns:
            On success: True.
            On failure: False.

        """
        try:
            self._session.query(JobStepEntity).\
                filter(JobStepEntity.job_id == job_id).\
                delete(synchronize_session=False)
        except SQLAlchemyError as err:
            Log.an().error('sql exception [%s]', str(err))
            return False

        return True


    #### Meta-Methods for Importing Definitions from Dicts ####

    def import_definition(self, def_path):
        """
        Import geneflow definition, including apps, workflows, and jobs.

        Args:
            def_path: path to geneflow definition.

        Returns:
            On success: Dict mapping names to IDs:
                {
                    'apps': {'app1': 'id', 'app2': 'id', ...},
                    'workflows': {'workflow1': 'id', 'workflow2': 'id', ...},
                    'jobs': {'job1': 'id', 'job2', 'id', ...}
                }
            On failure: False.

        """
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition: %s', def_path)
            return False

        app_name2id = self.import_apps_from_dict(
            gf_def.apps(), validate=False
        )

        yaml_dir = os.path.dirname(def_path)

        workflow_name2id = self.import_workflows_from_dict(
            gf_def.workflows(), validate=False, base_path=yaml_dir
        )
        job_name2id = self.import_jobs_from_dict(
            gf_def.jobs(), validate=False
        )

        return {
            'apps': app_name2id,
            'workflows': workflow_name2id,
            'jobs': job_name2id
        }


    # Apps

    def import_apps_from_dict(self, apps_dict, validate=True):
        """
        Import app definitions from a dict into DB.

        Optionally validate the dict before importing.

        Args:
            apps_dict: array of dict app definitions.
            validate: if True, validate the dict with the Definition class.

        Returns:
            Dict of app names and IDs. Example with "app1" and "app2"
            successfully importing, and "app2" failing:

            {
                "app1": "app1-id",
                "app2": "app2-id"
            }

        """
        app_name2id = {}

        for app in iter(apps_dict.values()):

            valid_def = {}
            if validate:
                valid_def = Definition.validate_app(app)
                if valid_def is False:
                    Log.an().error('invalid app:\n%s', yaml.dump(app))
                    return False

            else:
                valid_def = app

            if valid_def['name'] in app_name2id:
                Log.an().error('duplicate app name: %s', valid_def['name'])
                return False

            app_id = self.add_app({
                'name'          : valid_def['name'],
                'description'   : valid_def['description'],
                'repo_uri'      : valid_def['repo_uri'],
                'version'       : valid_def['version'],
                'username'      : valid_def['username'],
                'public'        : valid_def['public'],
                'definition'    : json.dumps(valid_def['definition']),
                'inputs'        : json.dumps(valid_def['inputs']),
                'parameters'    : json.dumps(valid_def['parameters'])
            })
            if not app_id:
                Log.an().error(
                    'cannot add app "%s" to data source', app['name']
                )
                return False

            app_name2id[valid_def['name']] = app_id

        return app_name2id


    def import_apps_from_def(self, def_path):
        """
        Import multiple app definitions from a single yaml file.

        Args:
            def_path: app definition path.

        Returns:
            Result of self.import_apps_from_dict if successful. False if
            invalid geneflow definition.

        """
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition')
            return False

        if not gf_def.apps():
            Log.a().warning('no apps in geneflow definition')

        return self.import_apps_from_dict(gf_def.apps(), validate=False)


    def delete_apps_by_def(self, def_path):
        """
        Delete multiple apps by IDs or names given by definition.

        Args:
            def_path: path to app definitions.

        Returns:
            On success: True.
            On failure: False.

        """
        # load apps from yaml
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition')
            return False

        # delete by id or name
        for app in iter(gf_def.apps().values()):
            if app['app_id']:
                if not self.delete_app_by_id(app['id']):
                    Log.an().error(
                        'cannot delete app from data source: app_id=%s',
                        app['id']
                    )
                    return False

            else: # use app name
                if not self.delete_app_by_name(app['name']):
                    Log.an().error(
                        'cannot delete app from data source: app_name=%s',
                        app['name']
                    )
                    return False

        return True


    def update_app_from_dict(self, app_dict, app_id=None, validate=True):
        """
        Update single app in the database from dict.

        Args:
            app_id: ID of app to update.
            app_dict: dict of new app.
            validate: validate dict or not?

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = {}
        if validate:
            valid_def = Definition.validate_app(app_dict)
            if valid_def is False:
                Log.an().error('invalid app:\n%s', yaml.dump(app_dict))
                return False

        else:
            valid_def = app_dict

        # insert app_id into dict if provided
        if app_id:
            valid_def['app_id'] = app_id

        if not self.update_app(
                valid_def['app_id'],
                {
                    'name'          : valid_def['name'],
                    'description'   : valid_def['description'],
                    'repo_uri'      : valid_def['repo_uri'],
                    'version'       : valid_def['version'],
                    'username'      : valid_def['username'],
                    'public'        : valid_def['public'],
                    'definition'    : json.dumps(valid_def['definition']),
                    'inputs'        : json.dumps(valid_def['inputs']),
                    'parameters'    : json.dumps(valid_def['parameters'])
                }
        ):
            Log.an().error(
                'error updating app: app_id=%s', valid_def['app_id']
            )
            return False

        return True


    def update_app_from_def(self, def_path, app_id=None):
        """
        Update single app in the database from definition file.

        Args:
            def_path: path to app definition file.
            app_id: ID of app to update. If provided, it's inserted into the
                app dict.

        Returns:
            On success: True.
            On failure: False.

        """
        # load app from yaml
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition')
            return False

        if not gf_def.apps():
            Log.an().error('no apps in geneflow definition')
            return False

        # insert app_id into first definition if provided
        if app_id:
            next(iter(gf_def.apps().values()))['app_id'] = app_id

        # can only update one at a time, so take first in list
        return self.update_app_from_dict(
            next(iter(gf_def.apps().values())), validate=False
        )


    # Workflows

    def add_linked_apps(self, workflow_dict, base_path):
        """
        Add apps referenced relatively from workflow defincition.

        Update workflow_dict to include new app IDs.

        Args:
            workflow_dict: Dict of workflow with relative apps references.

        Returns:
            On success: True.
            On failure: False.

        """
        app_dict = {}
        steps = workflow_dict['steps']
        for step in steps.values():
            if step.get('app'):

                app_id = app_dict.get(step['app'])
                if not app_id:
                    # app not yet loaded

                    # import app definition
                    if not os.path.isabs(step['app']):
                        app_path = os.path.join(base_path, step['app'])
                    else:
                        app_path = step['app']

                    apps = self.import_apps_from_def(app_path)
                    if not apps:
                        Log.an().error(
                            'cannot import app: %s', app_path
                        )
                        return False

                    # put ID of first item in dict
                    app_id = next(iter(apps.values()))
                    app_dict[step['app']] = app_id

                # update app_id of workflow
                step['app_id'] = app_id

        return True


    def synchronize_workflow_with_db(self, workflow_dict, workflow_id=None):
        """
        Verify that workflow steps/apps match database.

        Make sure workflow steps and apps in dict match steps defined in
        database for workflow_id. Also, update steps to include app_id and
        step_id.

        Args:
            workflow_dict: Dict of workflow to validate.
            workflow_id: ID of workflow to validate. If provided, inserted into
                workflow_dict.

        Returns:
            On success: True.
            On failure: False.

        """
        if workflow_id:
            workflow_dict['workflow_id'] = workflow_id

        step_map_db = {}
        if workflow_dict['workflow_id']:
            # get list of step names from DB and map to ids
            steps = self.get_step_by_workflow_id(workflow_dict['workflow_id'])
            if steps is False:
                Log.an().error(
                    'cannot get step by workflow id: workflow_id=%s',
                    workflow_dict['workflow_id']
                )
                return False

            step_map_db = {}
            for step in steps:
                step_map_db[step['name']] = step['id']

            # make sure number of steps in dict matches number in DB
            if len(workflow_dict['steps']) != len(step_map_db):
                Log.an().error('cannot change number of steps in workflow')
                return False

        # verify that apps are valid
        for step_name, step in workflow_dict['steps'].items():

            # verify step names if workflow_id provided
            if workflow_dict['workflow_id']:
                if step_name not in step_map_db:
                    Log.an().error(
                        'must use the same step names when updating a workflow'
                    )
                    return False

            # verify if app exists
            app = None
            app_key = ''
            if step['app_id']:
                # if app_id is defined, get corresponding app from DB
                app_key = step['app_id']
                app = self.get_app_by_id(app_key)

            else:
                # otherwise use app name to lookup app
                app_key = step['app_name']
                app = self.get_app_by_name(app_key)

            if app is False:
                Log.an().error(
                    'cannot get app by name or id: app_key=%s', app_key
                )
                return False

            if not app:
                # no app found by that name/id
                Log.an().error('invalid app: app_key=%s', app_key)
                return False

            # update app_id and step_id
            step['app_id'] = app[0]['id']
            # update step_id if workflow_id provided
            if workflow_dict['workflow_id']:
                step['step_id'] = step_map_db[step_name]

        return True


    def import_workflow_steps_from_dict(self, workflow_dict, workflow_id=None):
        """
        Add workflow steps to DB from workflow dict.

        Assume that the workflow_dict has already been validated. Does not add
        dependency records.

        Args:
            workflow_dict: dict of workflow that contains steps.
            workflow_id: database id of workflow. if provided, overrides any
                workflow_id in workflow_dict. if no id is provided as a
                parameter or in the dict, an error is returned.

        Returns:
            On success: dict of step IDs.
            On failure: False.

        """
        if workflow_id:
            workflow_dict['workflow_id'] = workflow_id

        if not workflow_dict['workflow_id']:
            Log.an().error('workflow_id required for importing steps')
            return False

        step_name2id = {}

        for step_name, step in workflow_dict['steps'].items():
            step_id = self.add_step({
                'workflow_id': workflow_dict['workflow_id'],
                'app_id': step['app_id'],
                'name': step_name,
                'number': step['number'],
                'letter': step['letter'],
                'map_uri': step['map']['uri'],
                'map_regex': step['map']['regex'],
                'template': json.dumps(step['template']),
                'exec_context': step['execution']['context'],
                'exec_method': step['execution']['method']
            })
            if not step_id:
                Log.an().error('cannot add workflow step: %s', step_name)
                return False

            # add new step id to dict
            step['step_id'] = step_id
            # update step name to id mapping
            step_name2id[step_name] = step_id

        return step_name2id


    def update_workflow_steps_from_dict(self, workflow_dict, workflow_id=None):
        """
        Update workflow steps in DB from workflow dict.

        Assume that the workflow_dict has already been validated. Does not
        update dependency records.

        Args:
            workflow_dict: dict of workflow that contains steps.
            workflow_id: database id of workflow. if provided, overrides any
                workflow_id in workflow_dict. if no id is provided as a
                parameter or in the dict, an error is returned.

        Returns:
            On success: dict of step IDs.
            On failure: False.

        """
        if workflow_id:
            workflow_dict['workflow_id'] = workflow_id

        if not workflow_dict['workflow_id']:
            Log.an().error('workflow_id required for updating steps')
            return False

        step_name2id = {}

        for step in workflow_dict['steps']:
            if not self.update_step(
                    step['step_id'],
                    {
                        'workflow_id': workflow_dict['workflow_id'],
                        'app_id': step['app_id'],
                        'name': step['name'],
                        'number': step['number'],
                        'letter': step['letter'],
                        'map_uri': step['map']['uri'],
                        'map_regex': step['map']['regex'],
                        'template': json.dumps(step['template']),
                        'exec_context': step['execution']['context'],
                        'exec_method': step['execution']['method']
                    }
            ):
                Log.an().error(
                    'cannot update step in data source: %s', step['name']
                )
                return False

            # update step name to id mapping
            step_name2id[step['name']] = step['step_id']

        return step_name2id


    def import_step_depends_from_dict(self, workflow_dict, step_name2id):
        """
        Add step dependencies to DB from workflow dict.

        Args:
            workflow_dict: dict of workflow that contains steps.
            step_name2id: dict that maps step names to ids.

        Returns:
            On success: True.
            On failure: False.

        """
        for step in workflow_dict['steps'].values():
            depend_list = step['depend']
            if not depend_list:
                depend_list = ['root']
            for depend in depend_list:
                parent_id = depend if depend == 'root' else step_name2id[depend]
                if not self.add_depend({
                        'child_id': step['step_id'],
                        'parent_id': parent_id
                }):
                    Log.an().error(
                        'cannot add step dependency (parent->step): %s->%s',
                        depend, step['name']
                    )
                    return False

        return True


    def import_workflows_from_dict(
            self, workflows_dict, validate=True, base_path=''
        ):
        """
        Import workflow definitions from a dict.

        Args:
            workflows_dict: array of workflow dicts.
            validate: if true, validate dict before import.

        Returns:
            On success: dict mapping workflow names to new IDs.
            On failure: False.

        """
        workflow_name2id = {}
        for workflow in iter(workflows_dict.values()):

            valid_def = {}
            if validate:
                valid_def = Definition.validate_workflow(workflow)
                if valid_def is False:
                    Log.an().error('invalid workflow:\n%s', yaml.dump(workflow))
                    return False

            else:
                valid_def = workflow

            if not self.add_linked_apps(valid_def, base_path):
                Log.an().error(
                    'cannot add linked apps for workflow: workflow_name=%s',
                    valid_def['name']
                )
                return False

            if not self.synchronize_workflow_with_db(valid_def):
                Log.an().error(
                    'cannot synchronize workflow with data source: workflow_name=%s',
                    valid_def['name']
                )
                return False

            # insert workflow record
            workflow_id = self.add_workflow({
                'name'              : valid_def['name'],
                'description'       : valid_def['description'],
                'username'          : valid_def['username'],
                'inputs'            : json.dumps(valid_def['inputs']),
                'repo_uri'          : valid_def['repo_uri'],
                'documentation_uri' : valid_def['documentation_uri'],
                'parameters'        : json.dumps(valid_def['parameters']),
                'final_output'      : json.dumps(valid_def['final_output']),
                'public'            : valid_def['public'],
                'enable'            : valid_def['enable'],
                'version'           : valid_def['version']
            })
            if not workflow_id:
                Log.an().error(
                    'cannot add workflow to data source: workflow_name=%s',
                    valid_def['name']
                )
                return False

            workflow_name2id[valid_def['name']] = workflow_id
            valid_def['workflow_id'] = workflow_id

            # insert steps, create map of steps
            step_name2id = self.import_workflow_steps_from_dict(valid_def)
            if not step_name2id:
                Log.an().error(
                    'cannot add workflow steps to database: workflow_name=%s',
                    valid_def['name']
                )
                return False

            # insert dependency records
            if not self.import_step_depends_from_dict(valid_def, step_name2id):
                Log.an().error(
                    'cannot add workflow step dependencies: workflow_name=%s',
                    valid_def['name']
                )
                return False

        return workflow_name2id


    def import_workflows_from_def(self, def_path):
        """
        Import multiple workflow definitions from a single yaml file.

        Args:
            def_path: workflow definition path.

        Returns:
            Result of self.import_workflows_from_dict if successful. False if
            invalid geneflow definition.

        """
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition: %s', def_path)
            return False

        if not gf_def.workflows():
            Log.an().warning('no workflows in geneflow definition')

        yaml_dir = os.path.dirname(def_path)

        return self.import_workflows_from_dict(
            gf_def.workflows(), validate=False, base_path=yaml_dir
        )


    def delete_workflows_by_def(self, def_path):
        """
        Delete multiple workflows by ID or name given by definition.

        Args:
            def_path: path to workflow definitions.

        Returns:
            On success: True.
            On failure: False.

        """
        # load workflows from yaml
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition: %s', def_path)
            return False

        # delete by id or name
        for workflow in iter(gf_def.workflows().values()):
            if workflow['workflow_id']:
                if not self.delete_workflow_by_id(workflow['id']):
                    Log.an().error(
                        'cannot delete workflow by id: workflow_id=%s',
                        workflow['id']
                    )
                    return False

            else: # use app name
                if not self.delete_workflow_by_name(workflow['name']):
                    Log.an().error(
                        'cannot delete workflow by name: workflow_name=%s',
                        workflow['name']
                    )
                    return False

        return True


    def update_workflow_from_dict(
            self,
            workflow_dict,
            workflow_id=None,
            validate=True
    ):
        """
        Update single workflow in the database from dict.

        Args:
            workflow_id: database ID of workflow to  update.
            workflow_dict: dict of new workflow.
            validate: validate workflow or not?

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = {}
        if validate:
            valid_def = Definition.validate_workflow(workflow_dict)
            if valid_def is False:
                Log.an().error(
                    'invalid workflow:\n%s', yaml.dump(workflow_dict)
                )
                return False

        else:
            valid_def = workflow_dict

        # insert workflow_id into dict if provided
        if workflow_id:
            valid_def['workflow_id'] = workflow_id

        # make sure steps of workflow are valid, update app IDs
        if not self.synchronize_workflow_with_db(valid_def):
            Log.an().error(
                'cannot synchronize workflow with data source: workflow_name=%s',
                valid_def['name']
            )
            return False

        # update workflow record
        if not self.update_workflow(
                valid_def['workflow_id'],
                {
                    'name':              valid_def['name'],
                    'description':       valid_def['description'],
                    'username':          valid_def['username'],
                    'repo_uri':          valid_def['repo_uri'],
                    'documentation_uri': valid_def['documentation_uri'],
                    'inputs':            json.dumps(valid_def['inputs']),
                    'parameters':        json.dumps(valid_def['parameters']),
                    'final_output':      json.dumps(valid_def['final_output']),
                    'public':            valid_def['public'],
                    'enable':            valid_def['enable'],
                    'version':           valid_def['version']
                }
        ):
            Log.an().error(
                'cannot update workflow: workflow_id=%s',
                valid_def['workflow_id']
            )
            return False

        # update steps, create map of steps
        step_name2id = self.update_workflow_steps_from_dict(valid_def)
        if not step_name2id:
            Log.an().error(
                'cannot update workflow steps: workflow_name=%s',
                valid_def['name']
            )
            return False

        # delete dependencies
        if not self.delete_depend_by_workflow_id(valid_def['workflow_id']):
            Log.an().error(
                'cannot delete step dependencies for workflow: workflow_id=%s',
                valid_def['workflow_id']
            )
            return False

        # insert dependency records
        if not self.import_step_depends_from_dict(valid_def, step_name2id):
            Log.an().error(
                'cannot import step dependencies for workflow: workflow_id=%s',
                valid_def['workflow_id']
            )
            return False

        return True


    def update_workflow_from_def(self, def_path, workflow_id=None):
        """
        Update single workflow in the database from definition file.

        Args:
            def_path: path to workflow definition file.
            workflow_id: ID of workflow to update. If provided, it's inserted
                into the workflow dict.

        Returns:
            On success: True.
            On failure: False.

        """
        # load workflow from yaml
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition: %s', def_path)
            return False

        if not gf_def.workflows():
            Log.an().error('no workflows in geneflow definition')
            return False

        # insert workflow_id into first definition if provided
        if workflow_id:
            next(iter(gf_def.workflows().values()))['workflow_id']\
                = workflow_id

        # can only update one at a time, so take first in list
        return self.update_workflow_from_dict(
            next(iter(gf_def.workflows().values())), validate=False
        )


    # Jobs


    def synchronize_job_with_db(self, job_dict):
        """
        Populate job dict with workflow name given a correct workflow_id.

        Args:
            job_dict: Dict of job to synchronize.

        Returns:
            On success: True.
            On failure: False.

        """
        if not job_dict['workflow_id']:
            # get workflow ID by workflow name
            workflow = self.get_workflow_by_name(job_dict['workflow_name'])
            if workflow is False:
                Log.an().error(
                    'cannot get workflow by name: workflow_name=%s',
                    job_dict['workflow_name']
                )
                return False

            if not workflow:
                Log.an().error(
                    'no workflow named %s', job_dict['workflow_name']
                )
                return False

            # use ID of the first match
            job_dict['workflow_id'] = workflow[0]['id']

        return True


    def import_jobs_from_dict(self, jobs_dict, validate=True):
        """
        Import job definitions from dict.

        Args:
            jobs_dict: array of job dicts.
            validate: if true, validate dict before import.

        Returns:
            On success: dict mapping job names to new IDs.
            On failure: False.

        """
        job_name2id = {}
        for job in iter(jobs_dict.values()):

            valid_def = {}
            if validate:
                valid_def = Definition.validate_job(job)
                if valid_def is False:
                    Log.an().error('invalid job:\n%s', yaml.dump(job))
                    return False

            else:
                valid_def = job

            if not self.synchronize_job_with_db(valid_def):
                Log.an().error(
                    'cannot synchronize job with data source: job_name=%s',
                    valid_def['name']
                )
                return False

            # insert job record
            job_id = self.add_job({
                'workflow_id'   : valid_def['workflow_id'],
                'name'          : valid_def['name'],
                'username'      : valid_def['username'],
                'work_uri'      : json.dumps(valid_def['work_uri']),
                'no_output_hash': valid_def['no_output_hash'],
                'inputs'        : json.dumps(valid_def['inputs']),
                'parameters'    : json.dumps(valid_def['parameters']),
                'output_uri'    : valid_def['output_uri'],
                'final_output'  : json.dumps(valid_def['final_output']),
                'exec_context'  : json.dumps(valid_def['execution']['context']),
                'exec_method'   : json.dumps(valid_def['execution']['method']),
                'notifications' : json.dumps(valid_def['notifications'])
            })
            if not job_id:
                Log.an().error(
                    'cannot add job to data source: job_name=%s',
                    valid_def['name']
                )
                return False

            job_name2id[valid_def['name']] = job_id
            valid_def['job_id'] = job_id

            # insert job step records
            steps = self.get_step_by_workflow_id(valid_def['workflow_id'])
            if not steps:
                Log.an().error(
                    'cannot get steps for workflow: workflow_id=%s',
                    valid_def['workflow_id']
                )
                return False

            for step in steps:
                if not self.add_job_step({
                        'job_id': job_id,
                        'step_id': step['id']
                }):
                    Log.an().error(
                        'cannot add job step: job_id=%s, step_name=%s',
                        job_id, step['name']
                    )
                    return False

        return job_name2id


    def import_jobs_from_def(self, def_path):
        """
        Import multiple job definitions from a single yaml file.

        Args:
            def_path: job definition path.

        Returns:
            Result of self.import_jobs_from_dict if successful. False if
            invalid geneflow definition.

        """
        gf_def = Definition()
        if not gf_def.load(def_path):
            Log.an().error('invalid geneflow definition: %s', def_path)
            return False

        if not gf_def.jobs():
            Log.a().warning('no jobs in geneflow definition')

        return self.import_jobs_from_dict(gf_def.jobs(), validate=False)
