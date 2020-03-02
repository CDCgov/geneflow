# GeneFlow

Version: 1.13.3

GeneFlow (GF) is a light-weight platform-agnostic workflow engine for scientific computing.

## Requirements

At a minimum, GeneFlow requires a Linux environment with Python 3. The Python pip installer for GeneFlow handles all python dependencies.

Agave is optional.  [Agave](https://tacc-cloud.readthedocs.io/projects/agave/en/latest/index.html) is a Science as a Service platform developed by the Texas Advanced Computing Center (TACC).  It provides fine-grained access to storage, authentication, data manipulation, and compute infrastructure and allows you to bring together public, private, and shared high performance computing (HPC), high throughput computing (HTC), Cloud, and Big Data resources under a single, web-friendly REST API.

## Quick Start

Users with access to the CDC SciComp environment may use the pre-installed GeneFlow and Agave to get started: [Quick Start for CDC Users](#use-geneflow-in-the-cdc-scicomp-environment).

External users, or CDC users who need a more customized installation, may refer to the general installation instructions which can be found in the [Additional Documentation](#additional-documentation).

### Use GeneFlow in the CDC SciComp Environment

1. Load the GeneFlow module in the CDC SciComp environment (from either Biolinux or Aspen):

    ```
    module load geneflow/latest
    ```

2. Test the installation by running the GeneFlow CLI:

    ```
    geneflow --help
    ```

### Install GeneFlow in a Python Virtual Environment

If you need to install GeneFlow, it is recommended to use a Python3 virtual environment. However, if you have root access and want to install GeneFlow system-wide, you may skip the virtual environment step.

1.  Create and activate a Python3 virtual environment:

    ```
    python3 -m venv gfpy
    source gfpy/bin/activate
    ```

2.  Clone the GeneFlow source repository:

    ```
    git clone https://github.com/CDCgov/geneflow
    ```

3.  Install GeneFlow:

    ```
    pip3 install ./geneflow
    ```

4.  Test the installation by running the GeneFlow CLI:

    ```
    geneflow --help
    ```

## Additional Documentation

Additional documentation can be found [here](https://geneflow.gitlab.io/). Alternatively, it can be found in the docs folder of this source repository (or by following this link: [Additional Documentation](docs/index.rst)). You can view the index.rst text file, or you can generate the html and pdf documentation with the following commands:

```
cd ~/geneflow_work
git clone https://github.com/CDCgov/geneflow
cd geneflow/docs
make html
make latexpdf
```

The output html and pdf files should appear in the `_build/html` or `_build/latex` folders. Note that you may need to install some dependencies prior to building the documentation. For example, for Ubuntu systems, run:

```
pip install sphinx
sudo apt install latexmk texlive texlive-science texlive-formats-extra
```

Note that sphinx may be installed within a Python virtual environment.

## Development Team and Support

GeneFlow was developed by the GDIT Scientific Computing and Bioinformatics Support (SCBS) team for the Office of Advanced Molecular Detection (OAMD) at the CDC.

For technical support, please contact oamdsupport@cdc.gov.
  
## Public Domain

This repository constitutes a work of the United States Government and is not
subject to domestic copyright protection under 17 USC § 105. This repository is in
the public domain within the United States, and copyright and related rights in
the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this repository will be released under the CC0 dedication. By
submitting a pull request you are agreeing to comply with this waiver of
copyright interest.

## License

The repository utilizes code licensed under the terms of the Apache Software
License and therefore is licensed under ASL v2 or later.

This source code in this repository is free: you can redistribute it and/or modify it under
the terms of the Apache Software License version 2, or (at your option) any
later version.

This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the Apache Software License for more details.

You should have received a copy of the Apache Software License along with this
program. If not, see http://www.apache.org/licenses/LICENSE-2.0.html

The source code forked from other open source projects will inherit its license.

## Privacy

This repository contains only non-sensitive, publicly available data and
information. All material and community participation is covered by the
Surveillance Platform [Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md)
and [Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
For more information about CDC's privacy policy, please visit [http://www.cdc.gov/privacy.html](http://www.cdc.gov/privacy.html).

## Contributing

Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo)
and submitting a pull request. (If you are new to GitHub, you might start with a
[basic tutorial](https://help.github.com/articles/set-up-git).) By contributing
to this project, you grant a world-wide, royalty-free, perpetual, irrevocable,
non-exclusive, transferable license to all users under the terms of the
[Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or
later.

All comments, messages, pull requests, and other submissions received through
CDC including this GitHub page are subject to the [Presidential Records Act](http://www.archives.gov/about/laws/presidential-records.html)
and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

## Records

This repository is not a source of government records, but is a copy to increase
collaboration and collaborative potential. All government records will be
published through the [CDC web site](http://www.cdc.gov).

## Notices

Please refer to [CDC's Template Repository](https://github.com/CDCgov/template)
for more information about [contributing to this repository](https://github.com/CDCgov/template/blob/master/CONTRIBUTING.md),
[public domain notices and disclaimers](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md),
and [code of conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).

