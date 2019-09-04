.. app-exec-container

Executing Containers in Apps
============================

This tutorial demonstrates how to create a GeneFlow app using a Singularity container. This tutorial also shows how to pipe two singularity commands together, which is a useful way to build more complex apps that run multiple commands from multiple images in a single app. Singularity (and container technologies in general) is a way for the user to have full control of their environment. A container (rather than the operating system) contains all the software dependencies required for the app, which allows improved reproducibility. For more information on Singularity, check out the documentation at: https://sylabs.io/docs/

Clone the GeneFlow App Template
-------------------------------

Start by cloning the App Template. 

.. code-block:: text

    git clone https://gitlab.com/geneflow/apps/app-template.git singularity-gf

This command downloads the app template into the "singularity-gf" directory. "singularity-gf" is also the name of the app you're creating in this tutorial.

Configure the App
-----------------

Configure the app by editing the "config.yaml" file. Feel free to use your favorite editor. The example here will use vi.

.. code-block:: text

    vi ./singularity-gf/config.yaml

Metadata
~~~~~~~~

Start by changing the Metadata fields to be specific for your app. I include the information for my app here. Change it to be specific for your field.

.. code-block:: text
   
    # name: standard GeneFlow app name
    name: singularity-gf
    # description: short description for the app
    description: execute docker image godlovedc/lolcow using geneflow app and singularity
    # repo_uri: link to the app's git repo
    repo_uri: https://gitlab.com/geneflow/apps/singularity-gf.git
    # version: must be incremented every time this file, or any file in the app
    # project is modified
    version: '0.1'

Inputs and Parameters
---------------------

We will keep the convention for inputs and parameters the same as the "hello world" app. The input will be a dummy file. The output will be a text file. 

.. code-block:: text

    inputs:
      file:
        label: Input File
        description: Input file
        type: File
        required: false
    
    parameters:
      output:
        label: Output File
        description: Output file
        type: File
        required: true
        test_value: output.txt

App Execution Methods
---------------------

We will keep the following fields unmodified because we want to use auto method detection and have no pre-execution commands:

.. code-block:: text

    default_exec_method: auto
    pre_exec:

We will modify the ``exec_methods:`` field significantly. The ultimate command we want to execute is 

.. code-block:: text

    singularity -s exec docker://godlovedc/lolcow fortune | singularity -s exec docker://godlovedc/lolcow cowsay

This command calls singularity to execute the "fortune" command from the "docker://godlovedc/lolcow" container image. The results of this command is piped into the "cowsay" command also executed from the "docker://godlovedc/lolcow" container image. The output is the text file specified from the parameters section. 

First, we change the "name" field of the "exec_method" to ``singularity``. The "if" statement checks if singularity is installed in the environment. If it is not, you need to install it for the app to work. We add the ``- pipe:`` line under ``exec:`` because we want to pipe the commands into each other. 

Below the ``- pipe:`` line are the yaml blocks specifying the two singularity commands we want to execute. Remember that the first command is ``singularity -s exec docker://godlovedc/lolcow fortune``. The ``'singularity'`` goes with the "- type:" field. The ``'-s exec'`` goes with the "options" field. Note that ``'-s exec'`` is actually the default option for singularity in GeneFlow, so this line is unnecessary here, but included to show how to modify this portion of the command. The "image" field defines the image we are using. In this case, we pull from dockerhub at ``'docker://godlovedc/lolcow'``. The "run" field defines the command we want run from the container, in this case ``fortune``. 

Because we are using the same image, the second block keeps the same fields except the following. The "run" field contains ``cowsay`` command. Next, we add the ``stdout: ${OUTPUT_FULL}`` line at the end of the block to specify that the output of the command is piped into the file defined in the parameters section.  

.. code-block:: text

    exec_methods:
    - name: singularity
      if:
      - str_equal: ['${SINGULARITY}', 'yes']
      exec:
      - pipe:
        - type: 'singularity'
          options: '-s exec'
          image: 'docker://godlovedc/lolcow'
          run: 'fortune'
        - type: 'singularity'
          options: '-s exec'
          image: 'docker://godlovedc/lolcow'
          run: 'cowsay'
          stdout: ${OUTPUT_FULL}


We also leave the ``post_exec:`` field empty because we have no post execution commands.

"Make" the App
--------------

Make this app like how you made the "hello world" app. 

.. code-block:: text

    cd singularity-gf
    geneflow make-app .

Next, make the app wrapper script executable:

.. code-block:: text

    chmod +x ./assets/singularity-gf.sh

Test the App
------------

The GeneFlow "make-app" command generates a "test.sh" script inside the "test" folder. If your app requires test data, that data can be placed inside the "test" folder, ideally within a sub-folder called "data". In this example, no test data is required.

To test the app, run the following commands:

.. code-block:: text

    cd test
    sh ./test.sh

The command should generate a file called "output.txt" after it finishes. Because we are pulling container images and running them on demand, this might take several minutes to finish.

Use the ``cat`` command to view the output of the file:

.. code-block:: text

    cat output.txt

You should see a cow saying a random statement like below. The statement was generated from the ``fortune`` command, while the cow and text box is generated from the ``cowsay`` command. 

..
    
   _________________________________________
  / Your reasoning powers are good, and you \
  \ are a fairly good planner.              /
   -----------------------------------------
          \   ^__^
           \  (oo)\_______
              (__)\       )\/\
                  ||----w |
                  ||     ||

Update your README.rst
----------------------

As usual, update your README file so others (and you later in time) can find out what the app does.

.. code-block:: text

    cd ..
    vi README.rst

Fill in the pertinent information:

.. code-block:: text

    singularity-gf
    =====
    
    Version: 0.1
    
    This is a GeneFlow app demonstrating how to execute and pipe singularity containers.
    
    Inputs
    ------
    
    1. file: dummy input file.
    
    Parameters
    ----------
    
    1. output: name of output file.

Upload your app
---------------

Upload the app to your favorite repo service. Create a new project called "singularity-gf". Commit and upload using the following commands, except change the url to your revelant repo service and name.

.. code-block:: text

    rm -rf .git
    git init
    git add .
    git commit -m "1st commit build"
    git tag 0.1
    git remote add origin https://gitlab.com/[YOUR NAME]/singularity-gf.git
    git push -u origin master
    git push origin 0.1

Summary
-------

Congratulations! You have created a GeneFlow app that uses singularity and pipes commands, tested it using the auto-generated test script, and committed it to a git repo. 
