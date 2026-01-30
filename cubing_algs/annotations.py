"""Type definitions for the cubing-algs library."""
import re
from typing import Literal

# Piece type for corners and edges
type PieceType = Literal['corner', 'edge']

# Corner types (8 corners, orientations 0-2)
type CornerIndex = Literal[0, 1, 2, 3, 4, 5, 6, 7]
type CornerOrientationValue = Literal[0, 1, 2]
type CornerPermutation = list[CornerIndex]
type CornerOrientation = list[CornerOrientationValue]

# Edge types (12 edges, orientations 0-1)
type EdgeIndex = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
type EdgeOrientationValue = Literal[0, 1]
type EdgePermutation = list[EdgeIndex]
type EdgeOrientation = list[EdgeOrientationValue]

# Face/spatial orientation (6 faces)
type FaceIndex = Literal[0, 1, 2, 3, 4, 5]
type SpatialOrientation = list[FaceIndex]

# Cubie arrays - permutation and orientation
type Permutation = list[int]
type Orientation = list[int]

# Cube facelets
type CubeFacelets = str

# Cube cubies tuple (cp, co, ep, eo) - without spatial orientation
type CubeCubies = tuple[
    Permutation, Orientation,
    Permutation, Orientation,
]

# Cube cubies tuple (cp, co, ep, eo, so) - with spatial orientation
type CubeCubiesOriented = tuple[
    Permutation, Orientation,
    Permutation, Orientation,
    Orientation,
]

# Regex pattern type
type RegexPattern = re.Pattern[str]
