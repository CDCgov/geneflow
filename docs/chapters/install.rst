.. install_geneflow

Install GeneFlow
================

GeneFlow can be installed and run in any Linux environment, and is pre-installed in the CDC environment. 

Requirements
------------

At a minimum, GeneFlow requires a Linux environment with Python 3. The Python pip installer for GeneFlow handles all python dependencies.

Agave is optionally required if you want to run workflows in Agave (see https://agaveapi.co).

Install Dependencies in Ubuntu/Debian Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install system-level dependencies in Ubuntu with the following commands:

    .. code-block:: bash

        sudo apt install python3 python3-dev git gcc

Install Dependencies in CentOS/RHEL Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install system-level dependencies in CentOS with the following commands:

    .. code-block:: bash

       sudo yum install python36 python36-devel git gcc

Python Modules
~~~~~~~~~~~~~~

You may also need the following Python modules:

    .. code-block:: bash

        pip install setuptools wheel

Prepare the CDC Environment to run GeneFlow
-------------------------------------------

To use the pre-installed GeneFlow in the CDC environment, use the following instructions to prepare the environment and load the module.

Prepare the CDC Environment and Load the GeneFlow Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the following steps to setup your CDC Linux environment to run GeneFlow. GeneFlow can be run from Biolinux or from any CDC Linux system that has access to the "modules" environment. 

1. In your home directory, create a working directory.

    .. code-block:: bash

        mkdir ~/geneflow_work

2. Although GeneFlow output can be directed to any folder, create an output folder to help organize workflow outputs:

    .. code-block:: bash

        mkdir ~/geneflow_work/output

3. Load the GeneFlow module. Note that older versions of GeneFlow can also be loaded by replacing "latest" with the desired version number:

    .. code-block:: bash

        module load geneflow/latest

Prepare Agave in the CDC Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to run workflows in Agave, you will need to initialize your CDC Agave environment.

Follow these instructions to prepare your Agave environment. Note that these instructions only need to be performed once.

1. Load the Agave CLI tools:

    .. code-block:: bash

        module load cobra-cli/0.1

2. Initialize your client:

    .. code-block:: bash

        cobra-init

    ``cobra-init`` will prompt you for your username and password.

3. Create an execution system:

    .. code-block:: bash

        cobra-systems-create

    Note the name of the new execution system, which will be formatted as ``cobra-hpc-aspen-[USER]-[DATE]``.

    Create GeneFlow output and work directories in your Agave home:

    .. code-block:: bash

        files-mkdir -N geneflow-output /[USER]
        files-mkdir -N geneflow-work /[USER]

4. Prepare the Agave configuration file:

    Create a new file with agave environment parameters:

    .. code-block:: bash

        cd ~/geneflow_work
        vi ./agave-params.yaml

    Add the following to the file:

    .. code-block:: yaml

       %YAML 1.1
       ---
       agave:
         # prefix for app name. For user apps, use your username.
         # For public apps, use 'public'.
         appsPrefix: [USER]

         # must have publish rights to the execution system
         executionSystem: cobra-hpc-aspen-[USER]-[DATE]

         # location of your agave home directory
         deploymentSystem: cobra-default-public-storage

         # Apps directory where app assets will be uploaded
         # This must be an absolute path
         appsDir: /[USER]/apps-gf

         # location of workflow test data, absolute path
         testDataDir: /[USER]/testdata-gf


    Replace ``[USER]`` with your Agave username.

    ``executionSystem`` should be the same system created in step 3 (e.g., ``cobra-hpc-aspen-[USER]-[DATE]``, replace ``[USER]`` and ``[DATE]``). To see a list of execution systems to which you have access, use:

    .. code-block:: bash

        systems-list -E

    ``deploymentSystem`` should be left at the default value.

Install GeneFlow in a General Linux Environment
-----------------------------------------------

Use the following instructions to install GeneFlow in a general Linux environment. 

Install GeneFlow using a Python Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GeneFlow can be installed and run in any general Linux environment. Use the following instructions to install geneflow and prepare the environment for running workflows. 

1. Create a working directory in a Linux environment. The remainder of these instructions will assume that the working directory is in ``~/geneflow_work``. If you customize this, be sure to adjust the commands in the instructions accordingly.

    .. code-block:: bash

        mkdir ~/geneflow_work

2. Setup a Python 3 virtual environment and install dependencies with pip3. The virtual environment is optional if you have sudo access and wish to install GeneFlow and dependencies system-wide. The python3 executable must be available in your path.

    Create and activate the Python 3 virtual environment:

    .. code-block:: bash

        cd ~/geneflow_work
        python3 -m venv gfpy
        source gfpy/bin/activate

    You should now see a modified prompt prefixed with "(gfpy)".

3. Clone the GeneFlow source code and install it:

    .. code-block:: bash

        git clone --config http.sslVerify=false https://git.biotech.cdc.gov/scbs/geneflow.git
        pip3 install ./geneflow

Prepare Agave in a General Linux Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to run workflows in Agave, you will need access to an Agave tenant. Follow the instructions at https://agaveapi.co to setup Agave with a client, storage system, and execution system. Alternatively, talk to your system administrator about setting up an Agave tenant.

1. Create an Agave token using the Agave CLI (https://bitbucket.org/tacc-cic/cli):

    .. code-block:: bash

        auth-tokens-create -u [USER]

2. Create GeneFlow output and work directories in your Agave home:

    .. code-block:: bash

        files-mkdir -N geneflow-output /[USER]
        files-mkdir -N geneflow-work /[USER]

    Note that, depending on your Agave default storage system, your home directory may be in a different place (e.g., /home/[USER]). Check with your Agave administrator if you are unsure.

3. Install the Agave Python wrapper:

    .. code-block:: bash

        pip3 install agavepy

4. Prepare the Agave configuration file:

    Create a new file with Agave environment parameters:

    .. code-block:: bash

        cd ~/geneflow_work
        vi ./agave-params.yaml

    Add the following to the file:

    .. code-block:: yaml

        %YAML 1.1
        ---
        agave:
          # prefix for app name. For user apps, use your username.
          # For public apps, use 'public'.
          appsPrefix: [USER]

          # must have publish rights to the execution system
          executionSystem: [execution-system]

          # location of your agave home directory
          deploymentSystem: [default-public-storage]

          # Apps directory where app assets will be uploaded.
          # This must be an absolute path.
          appsDir: /[USER]/apps-gf

          # location of workflow test data, absolute path.
          testDataDir: /[USER]/testdata-gf

    Replace ``[USER]`` with your Agave username.

    Replace ``[execution-system]`` with an Agave execution system for which you have "OWNER" access.

    Replace ``[deployment-system]`` with an Agave storage system that contains your home directory.

    For public apps, ``appsDir`` and ``testDataDir`` can be set to a global or shared location instead of a user home directory.

 
