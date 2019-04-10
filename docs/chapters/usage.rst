.. usage

GeneFlow Usage
==============

GeneFlow Command-Line Options
-----------------------------

All GeneFlow command line options can be viewed with the following:

.. code-block:: bash

    geneflow --help

Resulting in the following output:

.. code-block:: none

    usage: geneflow [-h] [--log_level LOG_LEVEL] [--log_file LOG_FILE]
                    {add-apps,add-workflows,help,init-db,install-workflow,migrate-db,run,run-pending}
                    ...

    GeneFlow CLI

    positional arguments:
      {add-apps,add-workflows,help,init-db,install-workflow,migrate-db,run,run-pending}
                            Functions
        add-apps            add apps to database
        add-workflows       add workflows to database
        help                GeneFlow workflow help
        init-db             initialize database
        install-workflow    install workflow
        migrate-db          migrate database
        run                 run a GeneFlow workflow
        run-pending         run pending workflow jobs

    optional arguments:
      -h, --help            show this help message and exit
      --log_level LOG_LEVEL
                            logging level
      --log_file LOG_FILE   log file


Each GeneFlow sub-command is detailed below.

Command-Line "add-apps"
~~~~~~~~~~~~~~~~~~~~~~~

The "add-apps" sub-command is a utility for adding GeneFlow apps directly to the GeneFlow relational database and is recommended for use by advanced users only. View further details for this sub-command with the following:

.. code-block:: bash

    geneflow add-apps --help

Resulting in the following output:

.. code-block:: none

    usage: geneflow add-apps [-h] -c CONFIG_FILE -e ENVIRONMENT app_yaml

    positional arguments:
      app_yaml              geneflow definition yaml with apps

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config_file CONFIG_FILE
                            geneflow config file path
      -e ENVIRONMENT, --environment ENVIRONMENT
                            environment

The "app_yaml" argument is a path to a YAML file with an app definition. See :ref:`definition-apps` for more details. The config file contains configuration paramters for GeneFlow execution, see :ref:`usage-config` for more details. The environment parameter refers to a specific section of the GeneFlow config file. 

Command-Line "add-workflows"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "add-workflows" sub-command is a utility for adding GeneFlow workflows directly to the GeneFlow relational database and is recommended for use by advanced users only. View further details for this sub-command with the following:

.. code-block:: bash

    geneflow add-workflows --help

Resulting in the following output:

.. code-block:: none

    usage: geneflow add-workflows [-h] -c CONFIG_FILE -e ENVIRONMENT workflow_yaml

    positional arguments:
      workflow_yaml         geneflow definition yaml with workflows

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config_file CONFIG_FILE
                            geneflow config file path
      -e ENVIRONMENT, --environment ENVIRONMENT
                            environment

The "workflow_yaml" argument is a path to a YAML file with a workflow definition. See :ref:`definition` for more details. The config file contains configuration parameters for GeneFlow execution, see :ref:`usage-config` for more details. The environment parameter refers to a specific section of the GeneFlow config file.

.. _usage-config:

GeneFlow Config File
--------------------

Config file.

Run Pre-Installed Workflows in the CDC Environment
--------------------------------------------------

The CDC SciComp environment contains a number of preinstalled GeneFlow workflows that can be run using GeneFlow's command-line interface. These workflows are installed in the directory ``/apps/geneflow/workflows``. 

Loading the GeneFlow module sets the ``GENEFLOW_PATH`` environment variable, which points to the pre-installed workflow directory. Check the path using the following:

.. code-block:: bash

    echo $GENEFLOW_PATH

You should see:

.. code-block:: none

    /apps/geneflow/workflows

This environment variable can be customized to point to a different location, if desired. To view the list of all workflows available in this shared location, use the following command:

.. code-block:: bash

    tree -L 2 $GENEFLOW_PATH

Which should result in a listing such as:

.. code-block:: none

    /apps/geneflow/workflows
    ├── bwa
    │   └── 0.1
    ├── bwa-basic
    │   ├── 0.1
    │   └── 0.3
    ├── bwa-samtools
    │   └── 0.1
    ├── fastqc
    │   └── 0.1
    ├── legionella-prs
    │   └── 0.4.1
    ├── legionella-species-id
    │   └── 0.2.1
    └── mars
        └── 0.1

These workflows may be accessed simply by referring to the workflow's name and version number, for example:

.. code-block:: bash

    geneflow help bwa-basic/0.3

This command displays the required inputs and parameters for the ``bwa-basic/0.3`` workflow:

.. code-block:: none

    2018-12-19 12:30:11 INFO [help.py:78:help_func()] workflow definition found: /apps/geneflow/workflows/bwa-basic/0.3/workflow/workflow.yaml

    GeneFlow: BWA Basic Workflow

    Basic Sequence alignment with BWA

    Inputs:
            --file: Input File: Input FASTQ file
                    type: File, default: /input/file.fastq
            --reference: Reference Sequence FASTA: Reference sequence FASTA file
                    type: File, default: /input/reference.fa

    Parameters:
            --threads: CPU Threads: Number of CPU threads for alignment
                    type: int, default: 2

Similarly, the workflow can be run using a command as follows. Here, the inputs are assigned using publicly available test data. However, these input values may be substituted with other appropriate data.  

.. code-block:: bash

    geneflow run bwa-basic/0.3 -d name="Test BWA Basic" -d output_uri=output -d inputs.file=/apps/geneflow/training/geneflow_intro/polio-sample.fastq -d inputs.reference=/apps/geneflow/training/geneflow_intro/poliovirus_strain_Sabin1.fasta

This run command produces the output similar to the following. Note that, since the parameter ``output_uri`` is set to ``output``, the workflow's output will be placed in a folder in the current directory called ``output``. This parameter may be replaced by any relative or absolute path. 

.. code-block:: none

    2018-12-19 12:48:50 INFO [run.py:122:run()] workflow definition found: /apps/geneflow/workflows/bwa-basic/0.3/workflow/workflow.yaml
    2018-12-19 12:48:51 INFO [run.py:164:run()] workflow loaded: BWA Basic Workflow -> 0731b0de8c8f4622ab99d9d21ad2e303
    2018-12-19 12:48:51 INFO [common.py:25:run_workflow()] job loaded: Test BWA Basic -> 09443efaca61473db4e6492b723df153
    2018-12-19 12:48:51 INFO [common.py:33:run_workflow()] running workflow:
    Job: Test BWA Basic (09443efaca61473db4e6492b723df153)
        Workflow: BWA Basic Workflow
            Description: Basic Sequence alignment with BWA
        Inputs:
            file: /apps/geneflow/training/geneflow_intro/polio-sample.fastq
            reference: /apps/geneflow/training/geneflow_intro/poliovirus_strain_Sabin1.fasta
        Parameters:
            threads: 2
        Work URIs:
            local: local:/scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa
        Output URI: local:/scicomp/home/[USER]/geneflow_work/output/test-bwa-basic-09443efa
    2018-12-19 12:48:51 INFO [workflow.py:610:run()] [input.reference]: staging input
    2018-12-19 12:48:51 INFO [workflow.py:623:run()] [step.index]: iterating map uri
    2018-12-19 12:48:51 INFO [workflow.py:630:run()] [step.index]: running
    Reference: /apps/geneflow/training/geneflow_intro/poliovirus_strain_Sabin1.fasta
    Output: /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/index/reference
    Execution Method: auto
    Detected Execution Method: cdc-shared-singularity
    CMD=mkdir -p /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/index/reference
    CMD=singularity run  -B /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/index:/data1 -B /apps/geneflow/training/geneflow_intro:/data2 /apps/standalone/singularity/bwa/bwa-0.7.17-biocontainers.simg bwa index  -p /data1/reference/reference.fa /data2/poliovirus_strain_Sabin1.fasta > log.stdout 2> log.stderr
    Exit code: 0
    2018-12-19 12:48:55 INFO [workflow.py:641:run()] [step.index]: all jobs complete
    2018-12-19 12:48:55 INFO [workflow.py:650:run()] [step.index]: cleaning
    2018-12-19 12:48:56 INFO [workflow.py:657:run()] [step.index]: staging output
    2018-12-19 12:48:56 INFO [workflow.py:668:run()] [step.index]: complete
    2018-12-19 12:48:56 INFO [workflow.py:610:run()] [input.file]: staging input
    2018-12-19 12:48:56 INFO [workflow.py:623:run()] [step.align]: iterating map uri
    2018-12-19 12:48:56 INFO [workflow.py:630:run()] [step.align]: running
    Input: /apps/geneflow/training/geneflow_intro/polio-sample.fastq
    Pair:
    Reference: /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/index/reference
    Threads: 2
    Output: /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/align/output.sam
    Execution Method: auto
    CMD=BWT_FILE=reference.fa.bwt
    CMD=BWT_PREFIX="reference.fa"
    Detected Execution Method: cdc-shared-singularity
    CMD=singularity run  -B /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/index:/data2 -B /apps/geneflow/training/geneflow_intro:/data3 /apps/standalone/singularity/bwa/bwa-0.7.17-biocontainers.simg bwa mem  -t 2 /data2/reference/reference.fa /data3/polio-sample.fastq > /scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa/align/output.sam 2> log.stderr
    Exit code: 0
    2018-12-19 12:49:00 INFO [workflow.py:641:run()] [step.align]: all jobs complete
    2018-12-19 12:49:00 INFO [workflow.py:650:run()] [step.align]: cleaning
    2018-12-19 12:49:00 INFO [workflow.py:657:run()] [step.align]: staging output
    2018-12-19 12:49:00 INFO [workflow.py:668:run()] [step.align]: complete
    2018-12-19 12:49:00 INFO [common.py:39:run_workflow()] workflow complete:
    Job: Test BWA Basic (09443efaca61473db4e6492b723df153)
        Workflow: BWA Basic Workflow
            Description: Basic Sequence alignment with BWA
        Inputs:
            file: /apps/geneflow/training/geneflow_intro/polio-sample.fastq
            reference: /apps/geneflow/training/geneflow_intro/poliovirus_strain_Sabin1.fasta
        Parameters:
            threads: 2
        Work URIs:
            local: local:/scicomp/home/[USER]/.geneflow/work/test-bwa-basic-09443efa
        Output URI: local:/scicomp/home/[USER]/geneflow_work/output/test-bwa-basic-09443efa

Install and Run a GeneFlow Workflow from the Community Repo
-----------------------------------------------------------

GeneFlow workflows that have been committed to source code repositories such as GitHub or GitLab can be installed and run in any Linux environment. The ``install-workflow`` GeneFlow sub-command clones a workflow from a source code repository and installs it locally. For example (Note: This example pulls apps from the CDC GitLab repository):

.. code-block:: bash

    geneflow install-workflow ./bwa-basic-gf --make_apps -g https://git.biotech.cdc.gov/geneflow-workflows/bwa-basic-gf.git

This command clones the "BWA Basic" GeneFlow workflow into the local folder ./bwa-basic-gf. The ``--make_apps`` flag is optional and indicates that app templates should be compiled upon installation. The output of the ``install-workflow`` sub-command should be similar to the following:

.. code-block:: none

    2018-12-19 15:39:28 INFO [workflow_installer.py:299:install_apps()] app:
    {'asset': 'none',
     'folder': 'bwa-index-0.7.17-gf-0.4',
     'name': 'bwa-index',
     'repo': 'https://git.biotech.cdc.gov/geneflow-apps/bwa-index-0.7.17-gf.git',
     'tag': '0.4'}
    2018-12-19 15:39:29 INFO [app_installer.py:266:make_def()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-index-0.7.17-gf-0.4/app.yaml.j2
    2018-12-19 15:39:30 INFO [app_installer.py:292:make_agave()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-index-0.7.17-gf-0.4/agave-app-def.json.j2
    2018-12-19 15:39:30 INFO [app_installer.py:324:make_wrapper()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-index-0.7.17-gf-0.4/assets/bwa-index-0.7.17-gf.sh
    2018-12-19 15:39:30 INFO [app_installer.py:356:make_test()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-index-0.7.17-gf-0.4/test/test.sh
    2018-12-19 15:39:30 INFO [app_installer.py:559:install_assets()] installing app asset type: none
    2018-12-19 15:39:30 WARNING [app_installer.py:572:install_assets()] unconfigured asset type specified: none
    2018-12-19 15:39:30 INFO [workflow_installer.py:299:install_apps()] app:
    {'asset': 'none',
     'folder': 'bwa-mem-0.7.17-gf-0.4',
     'name': 'bwa-mem',
     'repo': 'https://git.biotech.cdc.gov/geneflow-apps/bwa-mem-0.7.17-gf.git',
     'tag': '0.4'}
    2018-12-19 15:39:31 INFO [app_installer.py:266:make_def()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-mem-0.7.17-gf-0.4/app.yaml.j2
    2018-12-19 15:39:31 INFO [app_installer.py:292:make_agave()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-mem-0.7.17-gf-0.4/agave-app-def.json.j2
    2018-12-19 15:39:31 INFO [app_installer.py:324:make_wrapper()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-mem-0.7.17-gf-0.4/assets/bwa-mem-0.7.17-gf.sh
    2018-12-19 15:39:31 INFO [app_installer.py:356:make_test()] compiling /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/apps/bwa-mem-0.7.17-gf-0.4/test/test.sh
    2018-12-19 15:39:31 INFO [app_installer.py:559:install_assets()] installing app asset type: none
    2018-12-19 15:39:31 WARNING [app_installer.py:572:install_assets()] unconfigured asset type specified: none


Following installation, input and parameter requirements for the workflow can be viewed with the GeneFlow ``help`` sub-command:

.. code-block:: bash

    geneflow help bwa-basic-gf

Which produces the following:

.. code-block:: none

    2018-12-19 16:01:19 INFO [help.py:78:help_func()] workflow definition found: /scicomp/home/[USER]/geneflow_work/bwa-basic-gf/workflow/workflow.yaml

    GeneFlow: BWA Basic Workflow

    Basic Sequence alignment with BWA

    Inputs:
            --file: Input File: Input FASTQ file
                    type: File, default: /input/file.fastq
            --reference: Reference Sequence FASTA: Reference sequence FASTA file
                    type: File, default: /input/reference.fa

    Parameters:
            --threads: CPU Threads: Number of CPU threads for alignment
                    type: int, default: 2

