.. background

Background and Introduction
===========================

GeneFlow is a light-weight workflow engine for scientific computing that includes a standard definition language and a workflow execution engine. GeneFlow's definition language is configuration-based, uses a standard and easy-to-read YAML text format, and does not require any knowledge of scripting or programming, reducing the barriers to entry for non-computational scientists. The language allows scientists to specify metadata (e.g., workflow descriptors), inputs, parameters, and analytical steps for each workflow. 

A GeneFlow workflow can contain multiple steps, with each step referring to a single analytical task, which we call an application, or "app". Although apps can be defined to execute native tasks (i.e., Linux shell commands), GeneFlow supports and encourages the use of containers for apps. GeneFlow apps can be containerized using either Docker or Singularity and these containers are executed by the app's entry script. 

The GeneFlow definition is explicit, requiring users to declare specific app version numbers, dependencies between steps, and default input or parameter values, facilitating provenance and reducing ambiguity in scientific data analysis.

GeneFlow is part of a larger, standard toolchain that enables transparent resource access for end users and facilitates scientific collaboration. The GeneFlow framework was designed with a number of key features in mind: resulting workflows are 1) scientifically applicable, 2) portable, 3) shareable, 4) reproducible, 5) accessible, and are 6) developed using best practices:

1. Scientifically Applicable: The GeneFlow definition language employs a simple, yet flexible text-based YAML format that can capture any scientific workflow representable as a directed acyclic graph. Thus, GeneFlow is scientifically applicable to a wide range of workflows.

2. Portable: GeneFlow workflows are portable in that end users can execute their workflows in a wide range of computing environments including on a laptop (e.g.., in the field), in a centralized High Performance Computing (HPC) system, or in a cloud environment. GeneFlow achieves this by enabling the packaging of workflow apps using standard container technologies such as docker or singularity. GeneFlow is also extendable to support customized URIs, allowing easier integration of data management capabilities for both local or remote (e.g., cloud based object stores) data and analysis results.

3. Shareable: The text-based GeneFlow definition language facilitates easy sharing of workflows via standard source-control repositories such as GitHub or GitLab. Moreover, because the workflow definition specifies all required inputs (i.e., data resources) and parameters, GeneFlow greatly facilitates publishing workflows as graphical web-based applications. 

4. Reproducible: The ability to containerize a workflow's apps, coupled with GeneFlow's enforcement of documenting information such as app versions and workflow parameters improves workflow reproducibility by promoting numerical equivalence of results regardless of the execution environment. 

5. Accessible: GeneFlow's configuration based approach to defining a workflow is easier to understand than workflow definitions based on scripting languages, and does not require any programming background. Thus, GeneFlow workflows are more accessible to users with less computational experience. While creation of new GeneFlow apps requires some scripting experience, creation of workflows that re-use existing apps can be achieved by less experienced users by simply specifying the apps in the workflow definition. GeneFlow then automatically pulls and installs these apps in the computing environment.  

6. Promotes Best Practices: GeneFlow enables rapid development of new workflows through the reuse of existing workflow components. The fundamental building blocks of GeneFlow are individual applications or apps. An app typically defines one bioinformatics tool, such as a sequence aligner. GeneFlow workflows can point to any app stored in a Git repository. Moreover, these apps can be containerized and stored in repositories such as DockerHub. These capabilities and features of GeneFlow allow the end user to focus on the flow of data analysis and the outcomes rather than the underlying complexities associated with wrapping third party applications in their workflows. 







