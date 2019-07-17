.. basic-input

Basic Workflow and App Inputs
=============================

This tutorial extends the previously created "Hello World" workflow and app to process a single input file. The "One-Step Workflow: Hello World" tutorial must be completed, and its resulting "Hello World!" workflow should be committed to a Git repo prior to beginning this 

Modify the "Hello World!" App
-----------------------------

Checkout the previous "Hello World!" app:

.. code-block:: text

    cd ~/geneflow_work
    git clone https://github.com/[user]/hello-world-gf.git

Note: if the "hello-world-gf" directory still exists with the contents of the previous app tutorial, do a "git pull" instead:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    git pull

Define an App Input
~~~~~~~~~~~~~~~~~~~

Update the app metadata to reflect the new functionality. 


.. code-block:: text

    vi ./config.yaml

Change the ``description`` field to indicate a change in the app; add a ``repo_uri`` field (with [user] replaced with your username, and github.com replaced with the appropriate Git service); update the ``version`` field to '0.2':

.. code-block:: yaml

    # Basic app information

    # name: standard GeneFlow app name
    name: hello-world-gf
    # description: short description for the app
    description: Updated hello world GeneFlow app
    # repo_uri: link to the app's git repo
    repo_uri: https://github.com/[user]/hello-world-gf.git
    # version: must be incremented every time this file, or any file in the app
    # project is modified
    version: '0.2'

Next, update the ``file`` input in the ``inputs`` section of the ``config.yaml`` file. Change the ``label`` and ``description`` of the ``file`` input to "Input text file". Change the ``required`` field to 'true' and add a ``test_value`` field with value ``${SCRIPT_DIR}/data/file.txt``. The ``test_value`` field is only used when running the app's test script. We will define the ``/data/file.txt`` file in the next section. ``${SCRIPT_DIR}`` in the context of the test script is the directory in which the test script is located. The updated ``inputs`` section of the ``config.yaml`` file should look like:

.. code-block:: yaml

    inputs:
      file:
        label: Input Text File
        description: Input text file
        type: File
        required: true
        test_value: ${SCRIPT_DIR}/data/file.txt

Finally, change the execution commands of the app in the ``exec_methods`` section. 

.. code-block:: yaml

    exec_methods:
    - name: environment
      if:
      - in_path: 'cat'
      exec:
      - run: cat ${FILE_FULL}
        stdout: ${OUTPUT_FULL}

The modified execution block first checks if the 'cat' command is available (it should be available in all standard Linux systems). It then runs the 'cat' command to print the contents of the file passed as the ``file`` input. ``${FILE_FULL}`` is a bash variable that is automatically defined for the ``file`` input, and represents the full path of the ``file`` input. 

Save and close the ``config.yaml`` file.

Add a Test File to the App
~~~~~~~~~~~~~~~~~~~~~~~~~~

Previously, we added a file called ``file.txt`` to the test folder. Modify this file so that it contains the string "Hello World File Contents!":

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf/test/data
    vi ./file.txt

Make sure the file has the contents:

.. code-block:: text

    Hello World File Contents!

Save and close the ``file.txt`` file.

Re-"Make" the App
~~~~~~~~~~~~~~~~~

Now that the ``config.yaml`` file has been updated and the test file defined. Rebuild the app with the following commands:

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

Run the ``test.sh`` script to test the app:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf/test
    ./test.sh

You should see output similar to the following:

.. code-block:: text

    CMD=/home/[user]/geneflow_work/hello-world-gf/test/../assets/hello-world-gf.sh --file="/home/[user]/geneflow_work/hello-world-gf/test/data/file.txt" --output="output.txt" --exec_method="auto"
    File: /home/[user]/geneflow_work/hello-world-gf/test/data/file.txt
    Output: output.txt
    Execution Method: auto
    Detected Execution Method: environment
    CMD=cat /home/[user]/geneflow_work/hello-world-gf/test/data/file.txt  >"/home/[user]/geneflow_work/hello-world-gf/test/output.txt"
    Exit code: 0
    Exit code: 0

The ``output.txt`` file should have been created in the test directory with the text "Hello World File Contents!". View it with:

.. code-block:: text

    cat ./output.txt

And you should see:

.. code-block:: text

    Hello World File Contents!

Update the App README
~~~~~~~~~~~~~~~~~~~~~

Update the app README.rst file to reflect changes to the app:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    vi ./README.rst

Modify the file so it looks like the following:

.. code-block:: text

    Hello World! Updated GeneFlow App
    =================================

    Version: 0.2

    This is a basic GeneFlow app with an input.

    Inputs
    ------

    1. file: Input text file.

    Parameters
    ----------

    1. output: Output text file where "Hello World File Contents!" will be printed.

Commit and Tag the New App
~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, commit the updated app to the Git repo and update its tag to reflect the new version number:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    git add -u
    git commit -m "update app input"
    git tag 0.2
    git push --tags origin master

Modify the "Hello World!" Workflow
----------------------------------

Update the App Repo
~~~~~~~~~~~~~~~~~~~

Define a Workflow Input
~~~~~~~~~~~~~~~~~~~~~~~

Pass the Workflow Input to the App
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a Test File to the Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commit and Tag the New Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install and Test the Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


