.. app-exec-conditional

Conditional Execution in Apps
=============================

This tutorial extends the previously created "Hello World" workflow and app to demonstrate conditional execution in apps. The "Piped Execution in Apps" tutorial must be completed, and its resulting "Hello World!" workflow should be committed to a Git repo prior to beginning this tutorial.

Modify the "Hello World!" App
-----------------------------

Clone the previous "Hello World!" app from the Git repo (be sure to replace the Git repo URL with the appropriate URL for your app):

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

Change the ``description`` field to indicate a change in the app; leave the ``repo_uri`` field as is (e.g., with [USER] replaced with your username, and github.com replaced with the appropriate Git service); update the ``version`` field to ``0.4``:

.. code-block:: yaml

    # Basic app information

    # name: standard GeneFlow app name
    name: hello-world-gf
    # description: short description for the app
    description: Updated hello world GeneFlow app demonstrating conditional execution
    # repo_uri: link to the app's git repo
    repo_uri: https://github.com/[USER]/hello-world-gf.git
    # version: must be incremented every time this file, or any file in the app
    # project is modified
    version: '0.4'

Update App Parameters
~~~~~~~~~~~~~~~~~~~~~

Add a string parameter named ``mode`` to the app to control the app's execution. If this parameter is set to ``basic``, then the app will simply output ``Hello World!`` to a file. However, if this parameter is set to any other value, the app will execute as defined in the previous tutorial, i.e., it will use pipes to count the number of words in the input file. Leave the ``output`` parameter as is.

.. code-block:: yaml

    parameters:
      mode:
        label: Mode
        description: Execution mode
        type: string
        required: false
        default: basic
        test_value: basic
      output: 
        label: Output Text File
        description: Output text file
        type: File
        required: true
        test_value: output.txt

Update App Execution Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the app execution commands in the ``exec_methods`` section so that it checks the ``mode`` parameter and executes commands accordingly:

.. code-block:: yaml

    exec_methods:
    - name: environment
      if:
      - in_path: cat
      - in_path: wc
      - in_path: echo
      exec:
      - if:
        - str_equal: ['${MODE}', 'basic']
        run: echo 'Hello World!'
        stdout: ${OUTPUT_FULL}
        else:
        - pipe:
          - run: cat ${FILE_FULL}
          - run: wc -w
            stdout: ${OUTPUT_FULL}

The modified ``exec_methods`` block first checks if three command-line utilities are available in the system path: ``echo``, ``cat`` (which prints the contents of a file) and ``wc`` (which counts the number of words). If two or more items are defined in the ``if`` block, they are treated as an ``AND`` conditional, so ``echo``, ``cat``, and ``wc`` must all be available in the system path in order for the ``environment`` execution method to run. The ``if`` block checks the value of the ``mode`` parameter. If ``mode`` is set to ``basic``, the app echos ``Hello World!`` to the output file, as in the original version of the "Hello World!" app. However, if the ``mode`` parameter is set to anything else, the app executes the piped command as defined in the previous ""Piped Execution in Apps" tutorial. 

Re-"Make" the App
~~~~~~~~~~~~~~~~~

Now that the ``config.yaml`` file has been updated with the new conditional execution block and a new parameter has been added, rebuild the app with the following commands:

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


