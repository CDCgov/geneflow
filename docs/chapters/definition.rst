.. definition

GeneFlow Definition Language
============================

A GeneFlow definition consists of five components: metadata, steps, apps, inputs, and parameters. The metadata, steps, inputs, and parameters components are all defined in the workflow YAML file. The apps components are defined in a separate YAML file and describe individual applications. The apps are then referenced as part of the steps components of the workflow YAML file. Chaining of workflow steps is facilitated by a dynamic templating system that allows inputs and outputs to be generically parameterized, avoiding hard coding of these values.

The following is an example GeneFlow definition for a two-step workflow.

.. code-block:: yaml

    %YAML 1.1
    ---
    gfVersion: v1.0
    class: workflow

    # metadata
    name: BWA Workflow
    description: Sequence alignment with BWA
    documentation_uri: agave://cobra-default-public-storage/workflows/bwa/bwa_0.3_20180919.pdf
    repo_uri: https://git.biotech.cdc.gov/geneflow-workflows/bwa-gf.git
    version: '0.3'

    final_output:
    - align

    # inputs
    inputs:
      files:
        label: Input Directory
        description: Input directory containing FASTQ files
        type: Directory
        default: /input/files
        enable: true
        visible: true
     reference:
        label: Reference Sequence FASTA
        description: Reference sequence FASTA file
        type: File
        default: /input/reference.fa
        enable: true
        visible: true

    # parameters
    parameters: 
      threads:
        label: CPU Threads
        description: Number of CPU threads for alignment
        type: int
        default: 2
        enable: false
        visible: true

    # steps
    steps:
      index:
        app: apps/bwa-index-0.7.17-gf-0.2/app.yaml
        depend: []
        template:
          reference: '{workflow->reference}'
          output: reference

      align:
        app: apps/bwa-mem-0.7.17-gf-0.3/app.yaml
        depend: [ "index" ]
        map:
          uri: '{workflow->files}'
          regex: '(.*)_(R|)1(.*)\.((fastq|fq)(|\.gz))$'
        template:
          input: '{workflow->files}/{1}_{2}1{3}.{4}'
          pair: '{workflow->files}/{1}_{2}2{3}.{4}'
          reference: '{index->output}/reference'
          threads: '{workflow->threads}'
          output: '{1}.sam'
    ...

The above definition references two apps. The "index" step references the "bwa-index" app because the value of its "app" field is a relative link to the app definition: "apps/bwa-index-0.7.17-gf-0.2/app.yaml". Similarly, the "align" step references the "bwa-mem" app because the value of its "app" field is a relative link to the app definition: "apps/bwa-mem-0.7.17-gf-0.3/app.yaml".  As an example, the definition for the "bwa-mem" app is listed below. Note that the "name" field of the app definition is "bwa-mem-0.7.17-gf": 

.. code-block:: yaml

    %YAML 1.1
    ---
    gfVersion: v1.0
    class: app

    name: bwa-mem-0.7.17-gf
    description: BWA Mem Alignment
    repo_uri: https://git.biotech.cdc.gov/geneflow-apps/bwa-mem-0.7.17-gf.git
    version: '0.3'
    inputs:
      input:
        label: Sequence FastQ File
        description: sequence fastq file
        type: File
        default: input1.fastq.gz
      pair:
        label: Paired-End Sequence FastQ File
        description: Paired-end sequence fastq file
        type: File
        default: input2.fastq.gz
      reference:
        label: Reference Index
        description: Reference index directory
        type: Directory
        default: /reference/dir
    parameters:
      threads:
        label: CPU Threads
        description: Number of CPU threads used for alignment
        type: int
        default: 2
      output: 
        label: Output SAM File
        description: Output SAM file
        type: File
        default: output.sam
    definition:
      agave:
        agave_app_id: public-bwa-mem-0.7.17-gf-0.2u5
      local:
        script: bwa-mem-0.7.17-gf.sh
    ...

Each definition component is described in further detail in the following sections.

Metadata
--------

The metadata section contains general workflow descriptors as well as information for versioning, accessibility, and documentation. Metadata fields include name, description, author, version, documentation_uri, repo_uri, and final_output. Fields are described in detail below:

- name: A short string that represents the name of the workflow.
- description: A longer string, up to several sentences, that describes the workflow.
- username: Username of the workflow's creator or primary author.
- version: String representing the current or latest version number of the workflow.
- documentation_uri: A link (i.e., http:// URIs) to extended workflow documentation. This field can be an http or agave URI. 
- repo_uri: A link to the workflow's source control repository. 
- final_output: This field enables fine-tuning of data movement after workflow execution completes. It consists of a list of workflow steps specifying which output files should be moved to the final workflow output location.

The following is an example of a workflow metadata definition:

.. code-block:: yaml

    name: BWA Workflow
    description: Sequence alignment with BWA
    documentation_uri: agave://cobra-default-public-storage/workflows/bwa/bwa_0.3_20180919.pdf
    repo_uri: https://git.biotech.cdc.gov/geneflow-workflows/bwa-gf.git
    version: '0.3'
    username: user
    final_output:
    - align

Inputs
------

Inputs are references, or links, to files that are "staged" or copied to the workflow execution system. For local workflows, input files must be available on the local file system of the execution system. These files are staged to the workflow execution directory using basic copy operations (e.g., Linux "cp").

Each input is defined as a distinct key-value section in the YAML definition, with the name of the input being the key. Each input must also be defined with the following properties:

- label: a short description of the input, which can be used as the label when rendering a workflow input form. 
- description: a longer description of the input.
- type: can be "File", "Directory" or "Any"
- default: default value of the input, if no other value is provided.
- enable: used for rendering a workflow input form. If set to true, the input can be edited. If set to false, the input cannot be edited and the default value is used.
- visible: used for rendering a workflow input form. If set to true, the input is displayed (and editable if "enable" is also set to true). If set to false, the input is not displayed and the default value is used.

The following is an example of a workflow input definition with two inputs, "files" and "reference":

.. code-block:: yaml

    inputs:
      files:
        label: Input Directory
        description: Input directory containing FASTQ files
        type: Directory
        default: /input/files
        enable: true
        visible: true
      reference:
        label: Reference Sequence FASTA
        description: Reference sequence FASTA file
        type: File
        default: /input/reference.fa
        enable: true
        visible: true

Parameters
----------

Parameters are similar to inputs, but are inline data (either strings or numbers) rather than references to files or directories. The parameter "type" property can be set to: string, int, float, double, long, or Any. 

The following is an example of a workflow parameter definition with one parameter, "threads":

.. code-block:: yaml

    parameters: 
      threads:
        label: CPU Threads
        description: Number of CPU threads for alignment
        type: int
        default: 2
        enable: false
        visible: true

Steps
-----

The steps section describes all workflow steps and their order of execution. Each step of a workflow references a single analytical or computational task called an "application" or "app". For example, the "app" of the "align" step in the example definition references the "bwa-mem" app with a relative path of "apps/bwa-mem-0.7.17-gf-0.2/app.yaml". Apps are described in more detail in the "Apps" section.

The order of step execution is determined by the "depend" list defined for each step. In the example definition, the "index" step executes first because it has no dependencies on other steps (i.e., "depend" is an empty list). "align" executes only after "index" completes because it depends on the "index" step (i.e., "depend" explicitly contains "index").

The "template" section lists inputs and parameters that are passed to the referenced app. Templates are described in more detail in the section "Dynamic Templating". 

The "map" section of each app is optional and, if included, enables the Map-Reduce functionality of GeneFlow. This feature is described in more detail in the section "Map Reduce".

.. code-block:: yaml

    steps:
      index:
        app: apps/bwa-index-0.7.17-gf-0.2/app.yaml
        depend: []
        template:
          reference: '{workflow->reference}'
          output: reference

      align:
        app: apps/bwa-mem-0.7.17-gf-0.3/app.yaml
        depend: [ "index" ]
        map:
          uri: '{workflow->files}'
          regex: '(.*)_(R|)1(.*)\.((fastq|fq)(|\.gz))$'
        template:
          input: '{workflow->files}/{1}_{2}1{3}.{4}'
          pair: '{workflow->files}/{1}_{2}2{3}.{4}'
          reference: '{index->output}/reference'
          threads: '{workflow->threads}'
          output: '{1}.sam'
    ...

.. _definition-apps:

Apps
----

Apps referenced by workflow steps are defined independently of workflows, enabling modularity and reusability. An app can be referenced by multiple workflows or referenced multiple times within a single workflow. Bioinformatics workflows that effectively leverage this feature of GeneFlow naturally avoid the pitfall of monolithic code by inherently modularizing each logical bioinformatics operation as a reusable app. In this way, a GeneFlow workflow definition describes how these independent bioinformatics apps are orchestrated to achieve a complex multi-step bioinformatics goal. 

A single app can be referenced by a step using a relative or absolute link. However, relative links are preferred to facilitate workflow portability. For example, the "app" field within a step definition can point to an app definition YAML file as follows:

.. code-block:: yaml

    steps:
      index:
        app: apps/bwa-index-0.7.17-gf-0.2/app.yaml
        depend: []
        template:
          reference: '{workflow->reference}'
          output: reference

With the above definition, GeneFlow will accordingly look for the app.yaml file in the "apps" directory of the workflow package. 

Like workflows, app definitions include metadata, inputs, and parameters sections, but also include a "definition" section. App metadata is similar to workflow metadata and includes the following fields:

- name: A short string that represents the name of the app. 
- description: A longer string, up to several sentences, that describes the app.
- repo_uri: A link to the app's source control repository.
- version: String representing the current or latest version number of the app.

App "inputs" and "parameters" sections are also similar to that of workflows, but do not include the "enable" and "visible" fields. Values for inputs and parameters specified in apps are defaults and only used if their values are not provided in the workflow step definition. Default values may be useful for ensuring that app inputs or parameters are valid even when these values are omitted in the workflow definition; or may be useful for providing baseline test data for the app. 

The app "definition" section can contain multiple sub-sections, depending on which execution contexts are supported. As an example, the app definition section below illustrates how the "bwa-mem" app (referenced by the "align" step in the Workflow definition example) supports both "local" and "agave" execution contexts. The "local" execution context is associated with the "local" section, which contains a single "script" field. The "script" field is the name of the bash script to be executed when the app executes. Similarly, the "agave" execution context is associated with the "agave" section, which contains a single "agave_app_id" field. This field is the name of the registered Agave app that is executed with the app executes. 

.. code-block:: yaml

    definition:
      agave:
        agave_app_id: public-bwa-mem-0.7.17-gf-0.2u5
      local:
        script: bwa-mem-0.7.17-gf.sh

Dynamic Templating
------------------

Workflow step templates are required subsections of step definitions that (1) enable dynamic data references from inputs and parameters to steps and apps; (2) facilitate "chaining" of apps within a workflow by moving data between steps; and (3) help avoid tight coupling of steps to local file systems. 

Step templates comprise the core inputs, parameters, and outputs of an individual app. Template values are strings that are dynamically substituted with workflow-level inputs or parameters. For example, in the example workflow definition (the "steps" section shown below), the "index" step’s templates section contains a "reference" item. The string value of this template item, "{workflow->reference}", refers to the "reference" workflow-level input. Upon execution, the value of the "reference" input is passed into the "index" step’s app (i.e., "bwa-index") as the variable "reference". Similarly, "{workflow->files}" is dynamically substituted by the value of the workflow-level "file" input.  In this way, templates allow workflow-level inputs and parameters to be passed into the apps referenced by steps.
 
Dynamic templating also facilitates referencing of data between workflow steps, or "chaining" of apps. The output of a step can be passed as the input to a subsequent step. For example, in the example workflow definition, the output of the "index" step is passed as the input of the "align" step via the "{index->output}" string in the "align" step’s "reference" template. 

"{index->output}" is actually replaced with the base output directory of the "index" step. However, because the index step creates a single folder within that output directory called "reference", the "align" step is able to find the reference generated in the "index" step.  

Note that the value of the reference parameter passed to the "align" step template is "{index->output}/reference". This is because "{index->output}" is actually replaced with the base output directory of the "index" step. Furthermore, the index step creates a single folder within that output directory called "reference", and the contents of this reference folder are the expected input for the "align" step "reference" input. 

.. code-block:: yaml

    steps:
      index:
        app: apps/bwa-index-0.7.17-gf-0.2/app.yaml
        depend: []
        template:
          reference: '{workflow->reference}'
          output: reference

      align:
        app: apps/bwa-mem-0.7.17-gf-0.3/app.yaml
        depend: [ "index" ]
        map:
          uri: '{workflow->files}'
          regex: '(.*)_(R|)1(.*)\.((fastq|fq)(|\.gz))$'
        template:
          input: '{workflow->files}/{1}_{2}1{3}.{4}'
          pair: '{workflow->files}/{1}_{2}2{3}.{4}'
          reference: '{index->output}/reference'
          threads: '{workflow->threads}'
          output: '{1}.sam'

By defining data references with dynamic templates rather than with file system paths or URIs, GeneFlow decouples steps from infrastructure-specific file systems. Dynamic templating allows the GeneFlow engine, depending on the workflow type or execution environment, to automatically determine file system paths for staging input data and writing output data. 

Map Reduce
----------

The GeneFlow definition language supports a "Map-Reduce"-like functionality that allows item-wise parallel processing of directory contents. The optional "map" section of a step definition includes "uri" and "regex" fields. The "uri" field indicates the directory or location that contains a collection of items (either files or other folders) for processing. This field can also be templated, i.e., populated with a dynamic reference to an input, parameter, or output of a previous step. In the following step definition, the "uri" field is populated with the "files" workflow input. 

.. code-block:: yaml

    steps:
      ...
      align:
        app: apps/bwa-mem-0.7.17-gf-0.3/app.yaml
        depend: [ "index" ]
        map:
          uri: '{workflow->files}'
          regex: '(.*)_(R|)1(.*)\.((fastq|fq)(|\.gz))$'
        template:
          input: '{workflow->files}/{1}_{2}1{3}.{4}'
          pair: '{workflow->files}/{1}_{2}2{3}.{4}'
          reference: '{index->output}/reference'
          threads: '{workflow->threads}'
          output: '{1}.sam'

When a workflow step is defined with Map-Reduce, the step iterates through all contents of the "uri" and executes a single app for each item. All app instances for a step are the same, and is defined by the step's "app" field. 

The "regex" field allows filtering of "uri" contents using regular expressions and even allows extraction of regular expression groups in order to populate the template of each app instance. Thus, GeneFlow's "Map-Reduce" may be more aptly called "Map-Filter-Reduce". 

Consider the following contents of a URI passed to the "uri" field:

.. code-block:: yaml

    - sample-a_R1_001.fastq.gz
    - sample-a_R2_001.fastq.gz
    - sample-b_R1_001.fq.gz
    - sample-b_R2_001.fq.gz 

The regex of ``(.*)_(R|)1(.*)\.((fastq|fq)(|\.gz))$`` would match to two items: ``sample-a_R1_001.fastq.gz`` and ``sample-b_R1_001.fq.gz``. In the first match, the following groups would be extracted:

.. code-block:: yaml

    1: sample-a
    2: R
    3: _001
    4: fastq.gz

The template items ``{1}``, ``{2}``, ``{3}``, and ``{4}`` correspond to these groups, and would be substituted for the app instance. This would result in populated template items of:

.. code-block::  yaml

    input: '{workflow->files}/sample-a_R1_001.fastq.gz'
    pair: '{workflow->files}/sample-a_R2_001.fastq.gz'
    reference: '{index->output}/reference'
    threads: '{workflow->threads}'
    output: 'sample-a.sam'

In the second match, the following groups would be extracted:

.. code-block:: yaml

    1: sample-b
    2: R
    3: _001
    4: fq.gz

And the substituted template values for the second match would be:

.. code-block::  yaml

    input: '{workflow->files}/sample-b_R1_001.fq.gz'
    pair: '{workflow->files}/sample-b_R2_001.fq.gz'
    reference: '{index->output}/reference'
    threads: '{workflow->threads}'
    output: 'sample-b.sam'

Thus, GeneFlow identifies two pairs of FASTQ files and accordingly executes an app instance for each pair. The output directory of this step would contain an output file for each app instance. In this case, the files would be ``sample-a.sam`` and ``sample-b.sam``. 

GeneFlow implements a "Reduce" operation simply by passing an input directory to a step that does not have a "map" section. In this case, the contents of the directory are not filtered and all items are passed to a single app instance, which would be expected to perform some type of summarization operation. For example, such an app could merge multiple SAM files, or perform a multi-sample GATK variant calling analysis. 


