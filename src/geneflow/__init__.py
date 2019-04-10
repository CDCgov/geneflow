"""
GeneFlow package initialization.

GeneFlow (GF) is a light-weight platform-agnostic workflow engine written in
Python that lays the foundation for robust bioinformatics workflow development.

"""

from pathlib import Path

# GeneFlow module path
GF_PACKAGE_PATH = Path.resolve(Path(__file__)).parents[0]
