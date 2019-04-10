"""Module containing common functions for CLI sub-commands."""


from geneflow.log import Log
from geneflow.workflow import Workflow


def run_workflow(job, config, log_level):
    """
    Run a GeneFlow workflow.

    Args:
        job: job dict describing run.
        config: GeneFlow configuration dict.
        log_level: logging level for this run.

    Returns:
        On success: Workflow job dict.
        On failure: False.

    """
    if job['log']:
        # reconfig log location for this run
        Log.config(log_level, job['log'])
    Log.some().info('job loaded: %s -> %s', job['name'], job['id'])

    # run job
    workflow = Workflow(job['id'], config)
    if not workflow.initialize():
        Log.an().error('workflow initialization failed: job_id=%s', job['id'])
        return False

    Log.some().info('running workflow:\n%s', str(workflow))

    if not workflow.run():
        Log.an().error('workflow run failed: job_id=%s', job['id'])
        return False

    Log.some().info('workflow complete:\n%s', str(workflow))

    return workflow.get_job()
