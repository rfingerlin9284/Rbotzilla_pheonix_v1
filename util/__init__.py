"""Utility package for RICK — ensures proper package import resolution for tests.

This file makes the `util` directory a proper Python package, fixing import
errors when tests or other modules use `import util` paths.
"""

__all__ = []
