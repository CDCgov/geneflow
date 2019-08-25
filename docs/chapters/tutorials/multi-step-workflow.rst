.. multi-step-workflow

Multi-Step Workflow
===================

This tutorial extends the previously created "Hello World" workflow by adding a second step. The second step executes the wc command and returns a text file with the word count, line count, and byte count of the file created by the "Hello World" app.

You can either start from your previous "Hello World" workflow or the GeneFlow workflow template using one of the following commands 

.. code-block:: text

    git clone https://github.com/[USER]/hello-world-workflow-gf.git hello-world-2step-workflow-gf

Or

.. code-block:: text

    git clone https://gitlab.com/geneflow/workflows/workflow-template.git hello-world-2step-workflow-gf

The "wc" app
------------

The wc app has been created `already <https://gitlab.com/geneflow/apps/wc-gf.git>`_. The app essentially executes the following command: ``wc input.file > output.file`` You can clone the git repository, and look over the app, and run the test script to get a better understanding of how it works.

First, we tell the workflow to install and use the existing "wc" app by updating the ``apps-repo.yaml`` file.  

.. code-block:: text

    vi ./hello-world-2step-workflow-gf/workflow/apps-repo.yaml

Update the entries to include both the "hello-world" and "wc" apps. We will use the first version (0.1) of the "Hello World" app. You can use the app provided or substitute the name and version of your "Hello World" app.

.. code-block:: yaml

    apps:
    - name: hello-world-gf
      repo: https://gitlab.com/geneflow/apps/hello-world-gf.git
      tag: '0.1'
      folder: hello-world-gf-0.1
      asset: none

    - name: wc-gf
      repo: https://gitlab.com/geneflow/apps/wc-gf.git
      tag: '0.1'
      folder: wc-gf-0.1
      asset: none


Hello World output is the wc input
----------------------------------

The most important parts multi-step workflows are the inputs and outputs of the apps, as the output of one app will usually be the input of another app.

wc app input and output
~~~~~~~~~~~~~~~~~~~~~~~

Let's look at the input and output section of the "wc" app at
`https://gitlab.com/geneflow/apps/wc-gf/blob/master/config.yaml <https://gitlab.com/geneflow/apps/wc-gf/blob/master/config.yaml>`_.

.. code-block:: yaml

    inputs:
      file:
        label: Input File
        description: Input file
        type: File
        required: true
        test_value: ${SCRIPT_DIR}/data/file.txt

    parameters:
      output: 
        label: Output File
        description: Output file
        type: File
        required: true
        test_value: output.txt 

We see that the "wc" app takes a file as the input in the "file" field. In our workflow, we will use the output file of the "Hello World" app as the input to the "wc" app. 

Update the workflow.yaml file
-----------------------------

Update the appropriate sections of the workflow.yaml file as follows: 

.. code-block:: text

    vi ./hello-world-2step-workflow-gf/workflow/workflow.yaml

Metadata
~~~~~~~~

Update the metadata section with the new information for the package. Add ``- wc`` to ``final_output`` for the output of the wc step to be included in the final output. 

.. code-block:: yaml

    # metadata
    name: hello-world-2step-workflow-gf
    description: Hello World two-step workflow
    documentation_uri:
    repo_uri: 'https://github.com/jiangweiyao/hello-world-2step-workflow-gf.git'
    version: '0.1'
    username: USER

    final_output:
    - hello
    - wc

Steps
~~~~~

Add the wc app as the second step. Set the ``app:`` value to the location specified in the ``apps-repo.yaml`` file. The ``depend:`` value specifies the steps that must complete before the current step runs. Set the "wc" step to depend on the "hello" step since the output of the "hello-world" app is the input to the "wc" app. Set the ``file:`` option of "wc" to '{hello->output}/helloworld.txt' specifying the "helloworld.txt" file produced in the "hello" step as the input to "wc". Finally, set the ``output:`` option under the "wc" step as the name of the output file. 

.. code-block:: yaml

    # steps
    steps:
      hello:
        app: apps/hello-world-gf-0.1/app.yaml
        depend: []
        template:
          file: '{workflow->file}'
          output: helloworld.txt

      wc:
        app: apps/wc-gf-0.1/app.yaml
        depend: [ "hello" ]
        template:
          file: '{hello->output}/helloworld.txt'
          output: wc.txt

Update Workflow README
~~~~~~~~~~~~~~~~~~~~~~

Update the README.rst to include the relevant information 

Commit and Tag the New Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll use GitHub as an example, but the commands are similar for other repositories. If you cloned the workflow from an existing repository, delete the .git folder to create a new repository.

.. code-block:: text

    cd hello-world-2step-workflow-gf
    rm -rf .git

Create a new repository on GitHub named "hello-world-2step-workflow-gf". Push the code to GitHub using the following commands:

.. code-block:: text

    git init
    git add .
    git commit -m "1st commit"
    git tag 0.1
    git remote add origin https://github.com/[name]/hello-world-2step-workflow-gf.git
    git push -u origin master
    git push origin 0.1

Be sure to replace ``[name]`` with your GitHub username. 

Install and Test the Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that the workflow has been committed to a Git repo, it can be installed anywhere:

.. code-block:: text

    geneflow install-workflow -g https://github.com/[name]/hello-world-2step-workflow-gf.git -c --make_apps ./hello-world-2step

Make a dummy file named "test.txt":

.. code-block:: text

    touch test.txt

Finally, test the workflow to validate its functionality:

.. code-block:: text

    geneflow run -d output_uri=output -d inputs.file=test.txt ./hello-world-2step

This command runs the workflow in the "hello-world-2step" directory using the test data and copies the output to the "output" directory. The output of the two steps are placed in separate folders. 

.. code-block:: text

    tree ./geneflow_output/geneflow-job-[JOB ID]

You should see the following file structure:

.. code-block:: text

    geneflow-job-50dd420d
    ├── hello
    │   └── helloworld.txt
    └── wc
        └── wc.txt

Summary
-------

Congratulations! You created a two-step workflow that uses the output of one app as the input of the second app. 

