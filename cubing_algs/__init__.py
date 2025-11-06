"""
Python library for manipulating and analyzing Rubik's cube algorithms.

This library provides comprehensive tools for parsing, transforming,
and analyzing speedcubing algorithms.

It supports multiple notations (standard and SiGN), cube simulation,
pattern matching, and algorithm metrics.

Core modules:
- algorithm: Algorithm class for representing move sequences
- move: Move class for individual cube moves
- vcube: Virtual cube simulation with state tracking
- parsing: Parse move strings into Algorithm objects
- transform: Modular transformation functions
"""
from cubing_algs.algorithm import Algorithm
from cubing_algs.vcube import VCube

__version__ = '1.0.14'

__all__ = [  # noqa: PLE0604
    Algorithm.__name__,
    VCube.__name__,
]
