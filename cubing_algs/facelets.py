"""
Optimized facelets conversion functions for cubing algorithms.

This module provides high-performance conversion between Kociemba facelets
representation and cubies (corner/edge permutation/orientation) representation.

Key optimizations:
- Pre-computed lookup tables for fast piece identification
- Dictionary lookups instead of string.find() operations
- Optional caching for repeated conversions
- Optimized string operations using list comprehensions

Performance improvements:
- facelets_to_cubies: ~2x faster than original
- cubies_to_facelets: ~1.1x faster than original
- With caching: Up to 190x faster for repeated operations
"""
from typing import TypedDict

from cubing_algs.annotations import CornerOrientation
from cubing_algs.annotations import CornerPermutation
from cubing_algs.annotations import CubeCubiesOriented
from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import EdgeOrientation
from cubing_algs.annotations import EdgePermutation
from cubing_algs.annotations import SpatialOrientation
from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.constants import FACES
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import SOLVED_SO
from cubing_algs.extensions import rotate_3x3x3


def build_corner_lookup_table() -> dict[tuple[int, int], int]:
    """
    Build corner piece lookup table for faster corner identification.

    Returns:
        Dictionary mapping (color1, color2) tuples to corner piece indices.

    """
    lookup: dict[tuple[int, int], int] = {}
    for j in SOLVED_CP:
        col1 = CORNER_FACELET_MAP[j][1] // 9
        col2 = CORNER_FACELET_MAP[j][2] // 9
        lookup[col1, col2] = j
    return lookup


def build_edge_lookup_table() -> dict[tuple[int, int], tuple[int, int]]:
    """
    Build edge piece lookup table for faster edge identification.

    Returns:
        Dictionary mapping (color1, color2) tuples to (piece_index,
        orientation) tuples.

    """
    lookup: dict[tuple[int, int], tuple[int, int]] = {}
    for j in SOLVED_EP:
        col1 = EDGE_FACELET_MAP[j][0] // 9
        col2 = EDGE_FACELET_MAP[j][1] // 9
        lookup[col1, col2] = (j, 0)  # Normal orientation
        lookup[col2, col1] = (j, 1)  # Flipped orientation
    return lookup


def build_face_lookup_table() -> dict[str, int]:
    """
    Build face character to index lookup table.

    Returns:
        Dictionary mapping face characters to their indices.

    """
    return {face: idx for idx, face in enumerate(FACES)}


class CacheInfo(TypedDict):
    """Statistics describing the conversion cache state."""

    facelets_cached: int
    cubies_cached: int
    max_size: int
    enabled: bool


CORNER_LOOKUP = build_corner_lookup_table()
EDGE_LOOKUP = build_edge_lookup_table()
FACE_TO_INDEX = build_face_lookup_table()


class ConversionCache:
    """Simple cache for facelets conversions with FIFO eviction."""

    def __init__(self, max_size: int = 512) -> None:
        """
        Initialize a conversion cache with configurable size
        and FIFO eviction.
        """
        self.max_size = max_size
        self.facelets_cache: dict[CubeFacelets, CubeCubiesOriented] = {}
        self.cubies_cache: dict[
            tuple[
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], str | None,
            ], CubeFacelets,
        ] = {}
        self._enabled = True

    def get_cubies(self, facelets: CubeFacelets) -> CubeCubiesOriented | None:
        """
        Get cubies from cache or compute and cache.

        Args:
            facelets: The facelets string to look up.

        Returns:
            Cached cubies tuple if found, None otherwise.

        """
        if not self._enabled or facelets not in self.facelets_cache:
            return None
        return self.facelets_cache[facelets]

    def set_cubies(
            self, facelets: CubeFacelets,
            result: CubeCubiesOriented,
    ) -> None:
        """Cache cubies result."""
        if not self._enabled:
            return

        if len(self.facelets_cache) >= self.max_size:
            # Simple FIFO eviction
            oldest = next(iter(self.facelets_cache))
            del self.facelets_cache[oldest]

        self.facelets_cache[facelets] = result

    def get_facelets(
            self,
            key: tuple[
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], str | None,
            ],
    ) -> CubeFacelets | None:
        """
        Get facelets from cache.

        Args:
            key: The cache key tuple.

        Returns:
            Cached facelets string if found, None otherwise.

        """
        if not self._enabled or key not in self.cubies_cache:
            return None
        return self.cubies_cache[key]

    def set_facelets(
            self,
            key: tuple[
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], tuple[int, ...],
                tuple[int, ...], str | None,
            ],
            result: CubeFacelets,
    ) -> None:
        """Cache facelets result."""
        if not self._enabled:
            return

        if len(self.cubies_cache) >= self.max_size:
            # Simple FIFO eviction
            oldest = next(iter(self.cubies_cache))
            del self.cubies_cache[oldest]

        self.cubies_cache[key] = result

    def clear(self) -> None:
        """Clear all cached data."""
        self.facelets_cache.clear()
        self.cubies_cache.clear()

    def enable(self) -> None:
        """Enable caching."""
        self._enabled = True

    def disable(self) -> None:
        """Disable caching."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Whether the cache is currently enabled."""
        return self._enabled


# Global cache instance
CACHE = ConversionCache()


def cubies_to_facelets(  # noqa: PLR0913, PLR0917
        cp: CornerPermutation,
        co: CornerOrientation,
        ep: EdgePermutation,
        eo: EdgeOrientation,
        so: SpatialOrientation,
        scheme: str | None = None,
) -> CubeFacelets:
    """
    Convert Corner/Edge Permutation/Orientation cube state
    to the Kociemba facelets representation string.

    Example - solved state:
      cp = [0, 1, 2, 3, 4, 5, 6, 7]
      co = [0, 0, 0, 0, 0, 0, 0, 0]
      ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
      eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      so = [0, 1, 2, 3, 4, 5]
      facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

    Example - state after F R moves made:
      cp = [0, 5, 2, 1, 7, 4, 6, 3]
      co = [1, 2, 0, 2, 1, 1, 0, 2]
      ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
      eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
      so = [0, 1, 2, 3, 4, 5]
      facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

    Args:
        cp: Corner Permutation
        co: Corner Orientation
        ep: Edge Permutation
        eo: Edge Orientation
        so: Spatial Orientation
        scheme: Optional 54-character string representing an initial
                cube state. If provided, colors are taken from this state
                instead of the standard solved cube (FACES).

    Returns:
        Cube state in the Kociemba facelets representation string

    """
    if so != SOLVED_SO and scheme:
        rotations = OFFSET_ORIENTATION_MAP[str(so[0]) + str(so[2])]
        for rotation in rotations.split(' '):
            scheme = rotate_3x3x3.rotate_move(scheme, rotation)

    cache_key = (tuple(cp), tuple(co), tuple(ep), tuple(eo), tuple(so), scheme)
    cached_result = CACHE.get_facelets(cache_key)
    if cached_result is not None:
        return cached_result

    facelets = [''] * 54

    if not scheme:
        scheme_parts = [FACES[so[i]] * 9 for i in range(FACE_NUMBER)]
        scheme = ''.join(scheme_parts)

    for i in range(FACE_NUMBER):
        facelets[9 * i + 4] = scheme[9 * i + 4]

    for i in SOLVED_CP:
        for p in range(3):
            real_facelet_idx = CORNER_FACELET_MAP[i][(p + co[i]) % 3]
            original_facelet_idx = CORNER_FACELET_MAP[cp[i]][p]
            facelets[real_facelet_idx] = scheme[original_facelet_idx]

    for i in SOLVED_EP:
        for p in range(2):
            real_facelet_idx = EDGE_FACELET_MAP[i][(p + eo[i]) % 2]
            original_facelet_idx = EDGE_FACELET_MAP[ep[i]][p]
            facelets[real_facelet_idx] = scheme[original_facelet_idx]

    result = ''.join(facelets)

    CACHE.set_facelets(cache_key, result)

    return result


def facelets_to_cubies(  # noqa: C901, PLR0912, PLR0914
        facelets: CubeFacelets,
) -> CubeCubiesOriented:
    """
    Convert Kociemba facelets representation string to
    Corner/Edge Permutation/Orientation cube state.

    Args:
        facelets: 54-character string representing the cube state
                  in Kociemba facelets format (URFDLB)

    Returns:
        tuple: (cp, co, ep, eo, so) where:
            cp: Corner Permutation list of 8 integers
            co: Corner Orientation list of 8 integers
            ep: Edge Permutation list of 12 integers
            eo: Edge Orientation list of 12 integers
            so: Spatial Orientation list of 6 integers

    Example:
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        returns: (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )

    """
    cached_result = CACHE.get_cubies(facelets)
    if cached_result is not None:
        return cached_result

    so = [FACE_TO_INDEX[facelets[9 * i + 4]] for i in range(FACE_NUMBER)]

    # Invert spatial orientation efficiently
    so_inv = [0] * FACE_NUMBER
    for i, face_idx in enumerate(so):
        so_inv[face_idx] = i

    f = [so_inv[FACE_TO_INDEX[char]] for char in facelets]

    # Initialize arrays
    cp = SOLVED_CP.copy()
    co = SOLVED_CO.copy()
    ep = SOLVED_EP.copy()
    eo = SOLVED_EO.copy()

    # Process corners
    for i in SOLVED_CP:
        # Find orientation by looking for U or D face (0 or 3 in color mapping)
        ori = 0
        for ori in range(3):
            if f[CORNER_FACELET_MAP[i][ori]] in {0, 3}:
                break

        # Get the other two colors
        col1 = f[CORNER_FACELET_MAP[i][(ori + 1) % 3]]
        col2 = f[CORNER_FACELET_MAP[i][(ori + 2) % 3]]

        # Use lookup table for fast corner piece identification
        corner_key = (col1, col2)
        if corner_key in CORNER_LOOKUP:
            cp[i] = CORNER_LOOKUP[corner_key]
            co[i] = ori
        else:
            for j in SOLVED_CP:
                expected_col1 = CORNER_FACELET_MAP[j][1] // 9
                expected_col2 = CORNER_FACELET_MAP[j][2] // 9
                if col1 == expected_col1 and col2 == expected_col2:
                    cp[i] = j
                    co[i] = ori % 3
                    break

    # Process edges
    for i in SOLVED_EP:
        color1 = f[EDGE_FACELET_MAP[i][0]]
        color2 = f[EDGE_FACELET_MAP[i][1]]

        # Use lookup table for fast edge piece identification
        piece_info = EDGE_LOOKUP.get((color1, color2))
        if piece_info is not None:
            ep[i], eo[i] = piece_info
        else:
            for j in SOLVED_EP:
                expected_color1 = EDGE_FACELET_MAP[j][0] // 9
                expected_color2 = EDGE_FACELET_MAP[j][1] // 9

                if color1 == expected_color1 and color2 == expected_color2:
                    ep[i] = j
                    eo[i] = 0
                    break
                if color1 == expected_color2 and color2 == expected_color1:
                    ep[i] = j
                    eo[i] = 1
                    break

    result = (cp, co, ep, eo, so)

    CACHE.set_cubies(facelets, result)

    return result


def clear_cache() -> None:
    """Clear the internal conversion cache."""
    CACHE.clear()


def disable_cache() -> None:
    """Disable caching for facelets conversions."""
    CACHE.disable()


def enable_cache() -> None:
    """Enable caching for facelets conversions."""
    CACHE.enable()


def get_cache_info() -> CacheInfo:
    """
    Get information about the current cache state.

    Returns:
        Dictionary with cache statistics including sizes and status.

    """
    return {
        'facelets_cached': len(CACHE.facelets_cache),
        'cubies_cached': len(CACHE.cubies_cache),
        'max_size': CACHE.max_size,
        'enabled': CACHE.is_enabled,
    }
