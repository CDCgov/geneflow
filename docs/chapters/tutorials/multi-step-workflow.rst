.. multi-step-workflow

Multi-Step Workflow
===================

This tutorial extends the previously created "Hello World" workflow by adding a second step. The "Conditional Execution in Apps" tutorial must be completed, and its resulting "Hello World!" workflow chould be committed to a Git repo prior to beginning this tutorial. 

We will modify the workflow by adding a second step that's executed before the current "Hello World!" app. The new app will take an input file, duplicate its contents, and save these contents to a separate output file. 

Create the "Duplicate" App
--------------------------

The "Duplicate" app takes an input file and prints the contents of the file to another file twice, separated by a single newline. In Bash, this can be achieved with a command similar to the following: ``awk '{print}' file.txt file.txt > ./output.txt``. Thus, we will use a similar command when we define the execution section of the "Duplicate" app.

Clone the GeneFlow App Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, create a new app using the GeneFlow app template:

.. code-block:: text

    cd ~/geneflow_work
    git clone https://gitlab.com/geneflow/apps/app-template.git duplicate-gf

``duplicate-gf`` is the name of the app. 

Define App Metadata
~~~~~~~~~~~~~~~~~~~

Next, edit the metadata section of the app ``config.yaml`` file:

.. code-block:: text

    cd ~/geneflow_work/duplicate-gf
    vi ./config.yaml

The metadata section should look like the following:

.. code-block:: text

    name: duplicate-gf
    description: Geneflow app that duplicates contents of text file
    repo_uri: https://github.com/[USER]/duplicate-gf.git 
    version: '0.1'

Define App Inputs and Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define App Execution Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"Make" the App
~~~~~~~~~~~~~~

Test the App
~~~~~~~~~~~~

Create App README
~~~~~~~~~~~~~~~~~

Commit and Tag the App
~~~~~~~~~~~~~~~~~~~~~~

Modify the "Hello World!" Workflow
----------------------------------

Add "Duplicate" to App Repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update Workflow Metadata
~~~~~~~~~~~~~~~~~~~~~~~~

Add "Duplicate" Step
~~~~~~~~~~~~~~~~~~~~

Update Workflow README
~~~~~~~~~~~~~~~~~~~~~~

Commit and Tag the New Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install and Test the Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Summary
-------



