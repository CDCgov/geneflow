# Changelog


## 2019/09/11 - v1.11.0: minor enhancement release

1. Update agavepy module names for Python 3.7 compatibilty

2. Add "Executing Containers in Apps" tutorial to documentation.

3. Add "Build a Container for an App" tutorial to documentation.


## 2019/08/28 - v1.10.0: minor enhancement release

1. Add "Multi-Step Worflow" tutorial to documentation.

2. Simplify logging format and information for non-debug level logging.

3. Include workflow and app version and repo info in job logs.


## 2019/08/15 - v1.9.1: bug fix release

1. Fix bug: ensure that URL values passed to URL quote function are strings


## 2019/08/14 - v1.9.0: minor enhancement release

1. Add "Conditional Execution in Apps" tutorial to documentation.

2. Add --force option to overwrite existing workflow directory when installing from a Git repo.


## 2019/07/31 - v1.8.0: minor enhancement release

1. Fix bug: input files or directories with spaces should be handled correctly. 

2. Add "Piped Execution in Apps" tutorial to documentation.


## 2019/07/17 - v1.7.0: minor enhancement release

1. Add "Basic Workflow and App Inputs" tutorial to documentation.


## 2019/07/03 - v1.6.0: minor enhancement release

1. Set the default Singularity command to "-s exec" and allow custom commands for both Singularity and Docker


## 2019/06/19 - v1.5.0: minor enhancement release

1. Add "One-Step Workflow: Hello World" tutorial to documentation.

2. Fix bug: disallow GeneFlow from installing with Python >=3.7 until all dependencies have been validated for compatibility.


## 2019/06/05 - v1.4.0: minor enhancement release

1. Add "Basic App: Hello World" tutorial to documentation.

2. Fix bug: "Any" datatypes for inputs or parameters should be processed similar to "File" or "Directory" datatypes.

3. Add ability to store app log files in consistent and structured location: "_log" folder.


## 2019/05/08 - v1.3.0: minor enhancement release

1. Fix security vulnerability: pyyaml>=4.2b1

2. Fix security vulnerability: Jinja2>=2.10.1

3. Fix security vulnerability: SQLAlchemy>=1.3.0

4. Add "multi" exec feature to app config, allowing multiple execution items in a single block.

5. Add "else" conditional to exec blocks.

6. Add "str_contain" and "not_str_contain" tests to conditional blocks in app config.


## 2019/03/27 - v1.2.5: minor bug fix release

1. Fix bug: shell invoke method not catching non-zero exit codes.

2. Fix bug: workflow string parameters that contain whitespace are truncated


## 2019/03/13 - v1.2.4: minor bug fix release

1. Fix bug: step, input, and parameter dependencies in app templates not checked for validity when creating DAG.

2. Fix bug: invalid input URIs not correctly handled when using CLI. 


## 2019/02/27 - v1.2.3: minor bug fix release

1. Fix Agave import checks so that the agave module is not required for local execution.

2. Fix conditional 'if' block bug in app script jinja2 template. Require all items to be lists rather than dicts to allow repeated use of conditional keys.

3. Fix error message logging to database so that messages are more descriptive.


## 2019/01/30 - v1.2.2: minor bug fix release

1. Fix agave file list limit bug. Set limit to 1000000.


## 2019/01/16 - v1.2.1: documentation update and minor bug fix release

1. Fix agave def template issue: JSON dict comma for default values.

2. Fix wrapper script template issues: move SCRIPT_DIR definition to top of script.

3. Add script_default field to app config.yaml file.

4. Update installation documentation to include Sphinx and Ubuntu dependencies. 

5. Add app creation documentation.


## 2018/12/05 - v1.2.0: feature enhancment release

1. Add ability to generate app definitions from Jinja templates. Apps can now be fully defined with a single config.yaml file.

2. Add "make-app" sub-command for app development.

3. Add recursive directory creation for work and output URIs.

4. Update documentation to include more detailed information about workflow definition and command-line usage.


## 2018/09/12 - v1.1.0: minor feature and maintenance release

1. Error messages and formatting improved to be more descriptive and sensible to users.

2. Fixed bug: Error messages from step classes not logged to database.

3. Fixed bug: GeneFlow attempts to connect to Agave even when running a non-Agave workflow.

4. Fixed bug: GeneFlow unable to clone repos from CDC GitLab due to self-signed cert.


## 2018/08/28 - v1.0.0: production release of GeneFlow version 1

1. Add 'enable' boolean field to workflow table.

2. Change URI check messages to "INFO" rather than "ERROR".

3. Add "requests" library to setup.py.

4. Fix bug: default template values ignored if not string type.


## 2018/08/15 - v1.0.0-beta.2: workflow definition update, add install-workflow and help sub-commands

1. Refactor workflow definition for inputs and parameters.

2. Modularize CLI sub-commands.

3. Add install-workflow sub-command that replaces bash scripts.

4. Add WorkflowInstaller class.

5. Add async notifications to job definition and workflow class functionality.

6. Add optional functionality to accept job parameters on CLI instead of in job file.

7. Add support for GENEFLOW_PATH environment variable.

8. Add help sub-command.


## 2018/07/18 - v1.0.0-beta.1: workflow definition update, and app store functionality

1. Remove "type" from workflow and app definitions.

2. Add support for multiple execution contexts in app definitions.

3. Add "execution" section to job definition for specifying execution context and method.

4. Add 25 apps to the app store.

5. Add Agave app publication functionality to CLI.

6. Add database migration functionality to CLI.

7. Add CLI functionality to run pending jobs in DB.

8. Re-enable job-step logging to DB.

9. Add support for relative app links to workflow definition.


## 2018/05/30 - v1.0.0-alpha.4: code cleanup, minor feature testing, and app development

1. Enable multi-process execution of jobs from CLI

2. Pylint and Pydocstyle code cleanup

3. Add app and workflow methods to geneflow CLI entrypoint

4. Remove hardcoded SGE "queue" from Agave job templates


## 2018/04/26 - v1.0.0-alpha.3: graph data structure and refactoring

1. Refactor to use graph data structure

2. Integrate existing non-object-oriented functions into new or existing classes

3. Add automated tests with "behave"

4. Improve code styling and docstrings with "pylint" and "pydocstyle"


## 2018/03/15 - v1.0.0-alpha.2: initial agave-support release

1. Enable Agave functionality

2. Package project for PIP installation

3. Update documentation


## 2018/03/01 - v1.0.0-alpha.1: initial release


