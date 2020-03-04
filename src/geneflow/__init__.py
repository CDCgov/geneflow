"""
GeneFlow package initialization.

GeneFlow (GF) is a light-weight platform-agnostic workflow engine written in
Python that lays the foundation for robust bioinformatics workflow development.

"""

from pathlib import Path

# GeneFlow module path
GF_PACKAGE_PATH = Path.resolve(Path(__file__)).parents[0]

# version info
__version_info__ = ('1', '13', '3')
__version__ = '.'.join(__version_info__)
