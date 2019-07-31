.. app-exec-pipe

Piped Execution in Apps
=======================

This tutorial extends the previously created "Hello World" workflow and app to demonstrate the use of Bash pipes. The "Basic Workflow and App Inputs" tutorial must be completed, and its resulting "Hello World!" workflow should be committed to a Git repo prior to beginning this tutorial. 

Modify the "Hello World!" App
-----------------------------

Clone the previous "Hello World!" app from the Git repo (be sure to replace Git repo URL with the appropriate URL for your app):

.. code-block:: text

    cd ~/geneflow_work
    git clone https://github.com/[USER]/hello-world-gf.git

Note: if the ``hello-world-gf`` directory still exists with the contents of the previous app tutorial, do a ``git pull`` instead:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    git pull

Update App Metadata
~~~~~~~~~~~~~~~~~~~

Update the app metadata to reflect the new functionality:

.. code-block:: text

    vi ./config.yaml

Change the ``description`` field to indicate a change in the app; leave the ``repo_uri`` field as is (e.g., with [USER] replaced with your username, and github.com replaced with the appropriate Git service); update the ``version`` field to ``0.3``:

.. code-block:: yaml

    # Basic app information

    # name: standard GeneFlow app name
    name: hello-world-gf
    # description: short description for the app
    description: Updated hello world GeneFlow app demonstrating pipes
    # repo_uri: link to the app's git repo
    repo_uri: https://github.com/[USER]/hello-world-gf.git
    # version: must be incremented every time this file, or any file in the app
    # project is modified
    version: '0.3'

Update App Execution Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the app execution commands in the ``exec_methods`` section as follows:

.. code-block:: yaml

    exec_methods:
    - name: environment
      if:
      - in_path: cat
      - in_path: wc
      exec:
      - pipe:
        - run: cat ${FILE_FULL}
        - run: wc -w
          stdout: ${OUTPUT_FULL}

The modified ``exec_methods`` block first checks if two command-line utilities are available in the system path: ``cat`` (which prints the contents of a file) and ``wc`` (which counts the number of words). If two or more items are defined in the ``if`` block, they are treated as an ``AND`` conditional, so both ``cat`` and ``wc`` must be available in the system path in order for the ``environment`` execution method to run. The ``pipe`` section includes a list of execution blocks. Each execution block is piped into the subsequent execution block, and the final block pipes its output to the item defined by the ``stdout`` field. Thus, the ``pipe`` section translates to the following Bash code:

.. code-block:: text

    cat ${FILE_FULL} | wc -w > ${OUTPUT_FULL}

This command prints the contents of ``${FILE_FULL}``, pipes the result to ``wc``, the word count utility, then outputs the word count result to ``${OUTPUT_FULL}``. 

Re-"Make" the App
~~~~~~~~~~~~~~~~~

Now that the ``config.yaml`` file has been updated with the new piped execution block, rebuild the app with the following commands:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    geneflow make-app .

This should re-generate the ``app.yaml.j2``, ``agave-app-def.json.j2``, ``hello-world-gf.sh``, and ``test.sh`` scripts. 

Make sure the app wrapper script and test script are executable:

.. code-block:: text

    chmod +x ./assets/hello-world-gf.sh
    chmod +x ./test/test.sh

Test the App
~~~~~~~~~~~~

Run the ``test.sh`` script to test the app. Note: this test uses the same test input file added in the previous tutorial:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf/test
    ./test.sh

You should see output similar to the following:

.. code-block:: text

    CMD=/home/[USER]/geneflow_work/hello-world-gf/test/../assets/hello-world-gf.sh --file="/home/[USER]/geneflow_work/hello-world-gf/test/data/file.txt" --output="output.txt" --exec_method="auto"
    File: /home/[USER]/geneflow_work/hello-world-gf/test/data/file.txt
    Output: output.txt
    Execution Method: auto
    Detected Execution Method: environment
    CMD=cat /home/[USER]/geneflow_work/hello-world-gf/test/data/file.txt |wc -w  >"/scicomp/home/ktr2/geneflow_work/hello-world-gf/test/output.txt"
    Exit code: 0
    Exit code: 0

The ``output.txt`` file should have been created in the test directory with the text ``4``, which is the number of words in the test file (which has contents ``Hello World File Contents!``. View it with:

.. code-block:: text

    cat ./output.txt

And you should see the number of words in the test file:

.. code-block:: text

    4

Update the App README
~~~~~~~~~~~~~~~~~~~~~

Update the app ``README.rst`` file to reflect changes to the app:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    vi ./README.rst

Modify the file so it looks like the following:

.. code-block:: text

    Hello World! Updated GeneFlow App
    =================================

    Version: 0.3

    This is a basic GeneFlow app with an input that demonstrates pipes.

    Inputs
    ------

    1. file: Input text file.

    Parameters
    ----------

    1. output: Output text file where the number of words in the input text file will be printed.

Commit and Tag the New App
~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, commit the updated app to the Git repo and update its tag to reflect the new version number:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    git add -u
    git commit -m "update hello world app with pipes"
    git tag 0.3
    git push --tags origin master

Modify the "Hello World!" Workflow
----------------------------------

Now that the app has been updated, we can update the "Hello World!" workflow to use the new app.

Checkout the previous "Hello World!" workflow:

.. code-block:: text

    cd ~/geneflow_work
    git clone https://github.com/[USER]/hello-world-workflow-gf.git

Note: if the ``hello-world-workflow-gf`` directory still exists with the contents of the previous workflow tutorial, do a ``git pull`` instead:

.. code-block:: text

    cd ~/geneflow_work/hello-world-workflow-gf
    git pull

Update the App Repo
~~~~~~~~~~~~~~~~~~~

Update the ``apps-repo.yaml`` file so that the ``hello-world`` app item points to the latest "Hello World!" app repo. Open the file with:

.. code-block:: text

    cd ~/geneflow_work/hello-world-workflow-gf/workflow
    vi ./apps-repo.yaml

And modify the file so that it contains a single app item similar to:

.. code-block:: text

    - name: hello-world
      repo: https://github.com/[USER]/hello-world-gf.git
      tag: '0.3'
      folder: hello-world-gf-0.3
      asset: none

Be sure to replace the ``repo`` field with the appropriate Git url, and update ``tag`` and ``folder`` to reflect the ``0.2`` version of the app we just committed. 

Save and close the ``apps-repo.yaml`` file.

Update Workflow Metadata
~~~~~~~~~~~~~~~~~~~~~~~~

Update the workflow metadata by incrementing the version number to ``0.3``:

.. code-block:: text

    vi ./workflow.yaml

The metadata section should have the line:

.. code-block:: yaml

    version: '0.3'

Update the Workflow README
~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the ``README.rst`` file to reflect the new functionality:

.. code-block:: text

    cd ~/geneflow_work/hello-world-workflow-gf
    vi ./README.rst

Modify the file so it looks like the following:

.. code-block:: text

    Hello World! One-Step GeneFlow Workflow
    =======================================

    Version: 0.3

    This is a basic one-step GeneFlow workflow that demonstrates piping.

    Inputs
    ------

    1. file: Input text file.

    Parameters
    ----------

    None

Commit and Tag the New Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commit the new version of the workflow to the Git repo:

.. code-block:: text

    cd ~/geneflow_work/hello-world-workflow-gf
    git add -u
    git commit -m "updated hello world workflow"
    git tag 0.3
    git push --tags origin master

Install and Test the Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that the workflow has been updated and committed to a Git repo, we can install and test it:

.. code-block:: text

    cd ~/geneflow_work
    geneflow install-workflow -g https://github.com/[USER]/hello-world-workflow-gf.git -c --make_apps ./test-workflow-0.3

This command installs the updated "Hello World!" one-step workflow, and its updated "Hello World!" app into the directory ``test-workflow-0.3``. Remember to replace the Git URL with the URL to which you committed the workflow.

Test the workflow to validate its functionality:

.. code-block:: text

    geneflow run -d output_uri=output -d inputs.file=./test-workflow-0.3/data/test.txt ./test-workflow-0.3

This command runs the workflow in the ``test-workflow-0.3`` directory using the test data and copies the output to the ``output`` directory.

Once complete, you should see a file called ``output.txt`` with contents of ``4``: 

.. code-block:: text

    cat ./output/geneflow-job-[JOB ID]/hello/output.txt

Be sure to replace ``[JOB ID]`` with the ID of the GeneFlow job. The job ID is a randomly generated string and ensures that workflow jobs do not overwrite existing job output. You should see the following text in the ``output.txt`` file:

.. code-block:: text

    4

Summary
-------

Congratulations! You updated the one-step GeneFlow workflow so that it demonstrates piping the app. The next tutorial will expand on this workflow by introducing conditional execution in apps. 

