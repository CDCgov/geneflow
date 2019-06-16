.. one-step-workflow

One-Step Workflow: Hello World
==============================

Now that you've created an app in the previous tutorial, you can create your first GeneFlow workflow. This workflow flow will be a simple one-step workflow that runs the "Hello World" app. 

Clone the GeneFlow Workflow Template
------------------------------------

Enter the previously created "geneflow_work" directory:

.. code-block:: text

    cd ~/geneflow_work

Then make sure GeneFlow is still available in your environment either by loading the Python virtual environment, or loading the module.

Clone the workflow template from GeneFlow public workflows repository:

.. code-block:: text

    git clone https://gitlab.com/geneflow/workflows/workflow-template.git hello-world-workflow-gf

This command downloads the workflow template into the "hello-world-workflow-gf" directory, which also happens to be the name of the workflow you're creating in this tutorial. View the contents of the app template using the "tree" command:

.. code-block:: text

    cd hello-world-workflow-gf
    tree .

You should see the workflow template directory structure:

.. code-block:: text

    .
    ├── data
    │   └── README.rst
    ├── docs
    │   └── README.rst
    ├── README.rst
    └── workflow
        ├── apps-repo.yaml
        └── workflow.yaml

    3 directories, 5 files



Configure the Apps Repo
-----------------------

The first file 

Configure the Workflow
----------------------

Metadata
~~~~~~~~

Inputs and Parameters
~~~~~~~~~~~~~~~~~~~~~

Steps
~~~~~

Commit the Workflow to a Git Repo
---------------------------------

Install the Workflow from a Git Repo
------------------------------------

Test the Workflow
-----------------

Recommended Revision Process
----------------------------


