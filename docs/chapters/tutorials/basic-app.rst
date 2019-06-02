.. basic-app

Basic App: Hello World
======================

In this tutorial, you'll create a basic GeneFlow app that prints "Hello World!" to a text file. This tutorial provides a high-level overview of the components of the app configuration file (config.yaml). However, not all of these components are required to create a functional "Hello World!" app. 

Configure the Environment
-------------------------

Load or Install GeneFlow
~~~~~~~~~~~~~~~~~~~~~~~~

First, configure our environment by loading or installing GeneFlow. If you're using a system administered by someone else (e.g., a CDC system), GeneFlow may already be installed. 

To check if GeneFlow is available, use the following command:

.. code-block:: text

    geneflow --help

If it's available, you'll get a message similar to the following:

.. code-block:: text

    usage: geneflow [-h] [--log_level LOG_LEVEL] [--log_file LOG_FILE]
                    {add-apps,add-workflows,help,init-db,install-workflow,make-app,migrate-db,run,run-pending}
                    ...

    GeneFlow CLI

    positional arguments:
      {add-apps,add-workflows,help,init-db,install-workflow,make-app,migrate-db,run,run-pending}
                            Functions
        add-apps            add apps to database
        add-workflows       add workflows to database
        help                GeneFlow workflow help
        init-db             initialize database
        install-workflow    install workflow
        make-app            make app from templates
        migrate-db          migrate database
        run                 run a GeneFlow workflow
        run-pending         run pending workflow jobs

    optional arguments:
      -h, --help            show this help message and exit
      --log_level LOG_LEVEL
                            logging level
      --log_file LOG_FILE   log file

However, if it's not installed, you'll get a message like this:

.. code-block:: text

    -bash: geneflow: command not found

If this happens, try loading the GeneFlow module:

.. code-block:: text

    module load geneflow/latest
    geneflow --help

If GeneFlow is still not available, you'll need to install it. The recommended method for installation is in a Python virtual environment, as described here: :ref:`Install GeneFlow using a Python Virtual Environment <install-geneflow-venv>`.

After installation in a Python virtual environment, you can load GeneFlow using the following commands:

.. code-block:: text

    cd ~/geneflow_work
    source gfpy/bin/activate

Clone the GeneFlow App Template
-------------------------------

Create the "geneflow_work" directory in your home directory if doesn't already exist. This will be the location for all tutorial-related workflows, apps, and data:

.. code-block:: text

    mkdir -p ~/geneflow_work
    cd ~/geneflow_work

GeneFlow's public Apps and Workflows repository is located here: https://gitlab.com/geneflow/. In addition to public apps and workflows, this repository contains app and workflow templates. When creating new GeneFlow apps or workflows, we recommended to start with the app or workflow template rather than start from scratch. Clone the app template with the following command:

.. code-block:: text

    git clone https://gitlab.com/geneflow/apps/app-template.git hello-world-gf

This command downloads the app template into the "hello-world-gf" directory. "hello-world-gf" also happens to be the name of the app you're creating in this tutorial.

The GeneFlow app template contains a simple, but fully functional application. View the contents of the app template using the following commands:

.. code-block:: text

    cd hello-world-gf
    tree .

You should see the following output:

.. code-block:: text

    .
    ├── assets
    │   └── README.rst
    ├── build
    │   └── README.rst
    ├── config.yaml
    ├── docs
    │   └── README.rst
    ├── README.rst
    └── test
        ├── data
        │   └── file.txt
        └── README.rst

    5 directories, 7 files

You only need to update the "config.yaml" file to create the "Hello World" app. The "config.yaml" file is the main app configuration file, which defines the inputs, parameters, and execution commands of the app.

It's good practice to also update the main "README.rst" file to document the app. 

Configure the App
-----------------

Proceed with configuring the app by editing the "config.yaml" file. This file currently contains the configuration of a fully functional app, so you'll be simplifying some of the sections to create the "hello-world" app. Open the "config.yaml" file using your favorite text editor (vi and nano examples shown):

.. code-block:: text

    vi ./config.yaml

or:

.. code-block:: text

    nano ./config.yaml

The "config.yaml" file contains four main sections: Metadata, Inputs and Parameters, Execution Methods, and Assets. Edit each of these sections to create the "hello-world" app.

Metadata
~~~~~~~~

The app metadata section contains the following basic information:

name:
  Name of the GeneFlow app. We recommend to include version information if your app is wrapping a specific binary, container, or script. The app name should also include a "gf" suffix. For example, if the app is meant to wrap the "mem" function in BWA version 0.7.17, the app name should be "bwa-mem-0.7.17-gf". For this example, we'll use "hello-world-gf" without a version number because the app does not wrap a specific binary, container, or script. 

description:
  A title or short description of the app. For this example, use "Simple hello world GeneFlow app".

repo_uri:
  The full URL of the app's source repository. This information is not available yet, so leave it blank for now.

version:
  A string value that represents the app's version. For this example, use "0.1". We recommend to start with "0.1" for new apps and increment the number when changes are made to the app. 

In the "config.yaml" file, modify the "Metadata" section so that it looks like the following:

.. code-block:: yaml

    # name: standard GeneFlow app name
    name: hello-world-gf
    # description: short description for the app
    description: Simple hello world GeneFlow app
    # repo_uri: link to the app's git repo
    repo_uri:
    # version: must be incremented every time this file, or any file in the app
    # project is modified
    version: '0.1'

Inputs and Parameters
~~~~~~~~~~~~~~~~~~~~~

Each app input and parameter item is defined in a subsection with several properties. At least one input and one parameter is requred for each app. The "output" parameter is required, and must be manually included in the config file.

The example "Hello World" app doesn't need any inputs. However, because at least one input is required, define a "dummy", or un-used, input called "file". Modify the "Inputs and Parameters" section of the "config.yaml" file so that it looks like the following:

.. code-block:: yaml

    inputs:
      file:
        label: Dummy Input File
        description: Dummy input file
        type: File
        required: false

    parameters:
      output:
        label: Output Text File
        description: Output text file
        type: File
        required: true
        test_value: output.txt

For a more detailed explanation of each input or parameter property, see :ref:`App Inputs and Parameters <apps-inputs-parameters>`.

Execution Methods
~~~~~~~~~~~~~~~~~

The "Execution Methods" section of the app configuration file defines what your app actually does when executed. Apps can be defined with multiple execution methods. The specific method executed upon app invocation is either auto-detected or specified on the command line. Execution method names are customizable and the choice of a name should depend on your execution system. For example, if your app dependencies are installed globally in your execution system, you should define an "environment" execution method (indicating that dependencies are available in the environment). If your app dependencies are containerized with Singularity, you should define a "singularity" execution method. For a more detailed explanation of the app "Execution Methods" section, see :ref:`App Execution Methods <app-execution-methods>`.

The "Execution Methods" section contains four sub-sections: "default_exec_method", "pre_exec", "exec_methods", and "post_exec". Edit the "config.yaml" file so that each corresponding sub-section looks like the following. 

The "default_exec_method" sub-section is a single string value. Set this to "auto", indicating that the execution method should be auto-detected. Alternatively, you can set it to one of the execution methods defined in the "exec_methods" sub-section, e.g., "environment". 

.. code-block:: yaml

    default_exec_method: auto

The "pre_exec" sub-section defines any commands that should be executed prior to commands in the main "exec_methods" sub-section. These usually include commands for directory or file preparation that are common for all execution methods, e.g., creating an output directory. For this tutorial, no "pre_exec" commands are required, so leave it blank:

.. code-block:: yaml

    pre_exec:

The "Hello World" app simply prints "Hello World!" to a text file using the standard Linux "echo" command. Thus, define a single execution method in the "exec_methods" sub-section called "environment", which indicates that the needed commands or tools are already available in Linux. Update the "exec_methods" sub-section so that it looks like the following:

.. code-block:: yaml

    exec_methods:
    - name: environment
      if:
      - in_path: 'echo'
      exec:
      - run: echo 'Hello World!'
        stdout: ${OUTPUT_FULL}

The "if" statement is used for auto-detecting the execution method. If multiple execution methods are specified, the first execution method with an "if" statement that evaluates to "True" will be selected for execution. In this example, the statement ``in_path: 'echo'`` within the "if" statement means that the "environment" execution method will be selected if the "echo" command is available in the environment path. The "exec" statement contains a list of commands to be executed for the "environment" execution method. The "environment" execution method contains only a single command that echos the "Hello World!" text to an output file. Here, ${OUTPUT_FULL} is the full path of the file specified by the "output" parameter.

The "post_exec" sub-section defines any commands that should be executed after commands in the main "exec_methods" sub-section. These usually include commands for cleaning up any temporary files created during app execution. For this tutorial, no clean-up commands are necessary, so leave it blank:

.. code-block:: yaml

    post_exec:

Assets
~~~~~~

The "assets" section of the "config.yaml" file specifies additional scripts, binaries, or containers that need to be cloned from a git repo, copied from another location, and/or built during app installation. In this example, the app is fully contained within the "Execution Methods" section, so no additional assets are required. Specify this in the assets section as follows:

.. code-block:: yaml

    default_asset: none

    assets:
      none: []

"Make" the App
--------------

Now that the app has been configured, generate the app wrapper script, the test script, and various definition files using the following commands:

First, make sure you're still in the app directory:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf

Then run the GeneFlow "make-app" command:

.. code-block:: text

    geneflow make-app .

You should see output similar to the following:

.. code-block:: text

    2019-05-31 00:21:43 INFO [app_installer.py:267:make_def()] compiling /home/[user]/geneflow_work/hello-world-gf/app.yaml.j2
    2019-05-31 00:21:43 INFO [app_installer.py:293:make_agave()] compiling /home/[user]/geneflow_work/hello-world-gf/agave-app-def.json.j2
    2019-05-31 00:21:43 INFO [app_installer.py:325:make_wrapper()] compiling /home/[user]/geneflow_work/hello-world-gf/assets/hello-world-gf.sh
    2019-05-31 00:21:43 INFO [app_installer.py:357:make_test()] compiling /home/[user]/geneflow_work/hello-world-gf/test/test.sh

Finally, make the app wrapper script executable:

.. code-block:: text

    chmod +x ./assets/hello-world-gf.sh

Test the App
------------

The GeneFlow "make-app" command generates a "test.sh" script inside the "test" folder. If your app requires test data, that data can be placed inside the "test" folder, ideally within a sub-folder called "data". In this example, no test data is required.

To test the app, run the following commands:

.. code-block:: text

    cd test
    sh ./test.sh

You should see output similar to the following:

.. code-block:: text

    CMD=/home/[user]/geneflow_work/hello-world-gf/test/../assets/hello-world-gf.sh --output="output.txt" --exec_method="auto"
    File:
    Output: output.txt
    Execution Method: auto
    Detected Execution Method: environment
    CMD=echo 'Hello World!'  >"/home/[user]/geneflow_work/hello-world-gf/test/output.txt"
    Exit code: 0
    Exit code: 0

The "output.txt" file should also have been created in the test directory with the text "Hello World!". View it with:

.. code-block:: text

    cat ./output.txt

And you should see this output:

.. code-block:: text

    Hello World!

Update the App README
---------------------

It's best practice to update the app README file to include the app name, a short description, and descriptions for each input and parameter. Edit the README.rst file in the main app directory:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    vi ./README.rst

Modify the file so it looks like the following:

.. code-block:: text

    Hello World! Basic GeneFlow App
    ===============================

    Version: 0.1

    This is a basic GeneFlow app.

    Inputs
    ------

    1. file: Dummy input file, use any small file. 

    Parameters
    ----------

    1. output: Output text file where "Hello World!" will be printed.

Save the file and exit the editor.

Commit the App to a Git Repo
----------------------------

Finally, commit the app to a git repo so that it can be used in a GeneFlow workflow. First, if you don't already have one, create an account in either GitHub, GitLab, BitBucket, or your company/organization's git repository. Delete the output file that was created while testing the app, since this output file is not part of the main app definition:

.. code-block:: text

    cd ~/geneflow_work/hello-world-gf
    rm ./test/output.txt

Add and commit all changes to the local git repo, and tag the app version: 

.. code-block:: text

    git add -A
    git commit -m "initial version of the hello world app"
    git tag 0.1

Push to the remote repo using the following commands, depending on where your repository is located.

GitHub
~~~~~~

If your repository is in GitHub, you must first create the repo on the GitHub.com site. Once created, it will likely be located at a URL similar to ``https://github.com/[user]/hello-world-gf.git``, where ``[user]`` should be replaced with your GitHub username or group. Push your code to GitHub using the following commands:

.. code-block:: text

    git remote set-url origin https://github.com/[user]/hello-world-gf.git
    git push --tags origin master

Be sure to replace ``[user]`` with your GitHub username or group. 

GitLab
~~~~~~

If your repository is in GitLab, you don't need to create the repo on the GitLab.com site. You can skip directly to pushing your code to the git URL, which will be similar to ``https://gitlab.com/[user]/hello-world-gf.git``, where ``[user]`` should be replaced with your GitLab username or group:

.. code-block:: text

    git remote set-url origin https://gitlab.com/[user]/hello-world-gf.git
    git push --tags origin master

Be sure to replace ``[user]`` with your GitLab username or group. 

Organization GitLab
~~~~~~~~~~~~~~~~~~~

If you have a company or organization GitLab server, your git repo hostname will likely be different. For example, it could be hosted at ``https://git.biotech.cdc.gov/[user]/hello-world-gf.git``, where ``[user]`` should be replaced with your username or group:

.. code-block:: text

    git remote set-url origin https://git.biotech.cdc.gov/[user]/hello-world-gf.git
    git push --tags origin master

Be sure to replace ``[user]`` with your organization's GitLab username or group. 

Summary
-------

Congratulations! You created a basic GeneFlow app, tested it using the auto-generated test script, and committed it to a git repo. In the next tutorial, you'll create a one-step GeneFlow workflow that uses this "Hello-World" app. 
