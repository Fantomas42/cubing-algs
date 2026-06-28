"""Type definitions for the cubing-algs library."""
import re
from typing import Literal

# Facelet, Mask and DisplayCode
type Facelet = Literal['U', 'R', 'F', 'D', 'L', 'B']
type Mask = Literal['0', '1']
type DisplayCode = Literal['0', '1', '2', '3', '4']

# Piece type for corners and edges
type PieceType = Literal['corner', 'edge']

# Facelet piece type
type FaceletPieceType = Literal[
    'corner',
    'edge', 'midge', 'wing',
    'center', 'fixed_center',
    't_center', 'x_center',
    'oblique_center',
]


# Corner types (8 corners, orientations 0-2)
type CornerIndex = Literal[0, 1, 2, 3, 4, 5, 6, 7]
type CornerOrientationValue = Literal[0, 1, 2]
type CornerPermutation = list[int]
type CornerOrientation = list[int]

# Edge types (12 edges, orientations 0-1)
type EdgeIndex = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
type EdgeOrientationValue = Literal[0, 1]
type EdgePermutation = list[int]
type EdgeOrientation = list[int]

# Face/spatial orientation (6 faces)
type FaceIndex = Literal[0, 1, 2, 3, 4, 5]
type SpatialOrientation = list[int]

# Cubie arrays - permutation and orientation
type Permutation = list[int]
type Orientation = list[int]

# Cube facelets
type CubeFacelets = str[Facelet]
type FaceFacelets = str[Facelet]

# Cube orientation (1 or 2 characters)
type CubeOrientation = str[Facelet]

# Binary mask (string of '0' and '1')
type POVMask = str[Mask]
type CubeMask = str[Mask]
type FaceMask = str[Mask]

# Display mask
type POVDisplayMask = str[DisplayCode]
type CubeDisplayMask = str[DisplayCode]

# Cube cubies tuple (cp, co, ep, eo) - without spatial orientation
type CubeCubies = tuple[
    CornerPermutation, CornerOrientation,
    EdgePermutation, EdgeOrientation,
]

# Cube cubies tuple (cp, co, ep, eo, so) - with spatial orientation
type CubeCubiesOriented = tuple[
    CornerPermutation, CornerOrientation,
    EdgePermutation, EdgeOrientation,
    SpatialOrientation,
]

# Regex pattern type
type RegexPattern = re.Pattern[str]
