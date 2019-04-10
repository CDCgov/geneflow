"""Install GeneFlow Workflow Engine."""
import os

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

BASE_DIR = os.path.dirname(__file__)
README = open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8').read()

VERSION = '1.2.5'

INSTALL_REQUIRES = [
    'PyYAML>=3.12',
    'PyMySQL>=0.8.0',
    'python-slugify>=1.2.5',
    'yoyo-migrations>=5.0.5',
    'regex>=2018.02.21,<2019.02.19',
    'sqlalchemy>=1.0.13',
    'pytest>=2.7.0',
    'cerberus==1.2',
    'networkx>=2.1',
    'behave>=1.2.6',
    'GitPython==2.1.11',
    'requests>=2.19.1',
    'Jinja2>=2.7'
]

PYTHON_REQUIRES = '>=3.5.*'

# test_suite = 'geneflow.test.test_all'

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)

setup(
    name='geneflow',
    version=VERSION,
    description="A light-weight platform-agnostic workflow engine for scientific computing.",
    long_description=README,
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: BSD',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    keywords='workflow agave bioinformatics',
    author='GeneFlow Development Team',
    author_email='oamdsupport@cdc.gov',
    url='https://git.biotech.cdc.gov/scbs/geneflow',
    license='BSD',
    packages=find_packages('src', exclude=["*.test"]),
    package_dir={'': 'src'},
    package_data={'': ['data/sql/geneflow.sql',
                       'data/sql/geneflow-sqlite.sql',
                       'data/migrations/20171005-01.py',
                       'data/migrations/20171029-01.py',
                       'data/migrations/20171105-01.py',
                       'data/migrations/20171113-01.py',
                       'data/migrations/20180122-01.py',
                       'data/migrations/20180713-01.py',
                       'data/migrations/20180727-01.py',
                       'data/migrations/20180821-01.py',
                       'data/migrations/20180907-01.py',
                       'data/templates/app.yaml.j2.j2',
                       'data/templates/agave-app-def.json.j2.j2',
                       'data/templates/wrapper-script.sh.j2',
                       'data/templates/test.sh.j2',
                       'data/templates/config.example.yaml']},
    include_package_data=True,
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    python_requires=PYTHON_REQUIRES,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand
        },
    entry_points={
        'console_scripts': [
            'geneflow = geneflow.__main__:main'
        ]
    }
)
