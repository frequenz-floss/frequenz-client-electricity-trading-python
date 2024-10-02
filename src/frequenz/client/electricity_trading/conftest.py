# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Validate docstring code examples.

Code examples are often wrapped in triple backticks (```) within docstrings.
This plugin extracts these code examples and validates them using pylint.
"""

from frequenz.repo.config.pytest import examples
from sybil import Sybil

args = examples.get_sybil_arguments()
# Pop "excludes" which was added upstream to work around a sybil bug
# with __init__.py files
args.pop("excludes", None)

pytest_collect_file = Sybil(**args).pytest()
