"""
Transformation functions for modifying Rubik's cube algorithms.

This package provides modular transformation functions that can be applied
to Algorithm objects to modify their structure, optimize their efficiency,
or convert between different notations and representations.

All transform functions follow the pattern:
    transform_function(algorithm: Algorithm) -> Algorithm

Transform functions can be chained using the Algorithm.transform() method:
    algorithm.transform(mirror_moves, compress_moves, optimize_moves)
"""
