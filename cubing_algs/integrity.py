"""
Cube state integrity validation for cubing algorithms.

This module provides comprehensive validation of Rubik's cube states
to ensure they represent valid, solvable cube configurations.
Checks include permutation validity, orientation constraints,
color combinations, and mathematical consistency.
"""
from cubing_algs.annotations import CornerOrientation
from cubing_algs.annotations import CornerPermutation
from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import CubeOrientation
from cubing_algs.annotations import EdgeOrientation
from cubing_algs.annotations import EdgePermutation
from cubing_algs.annotations import Orientation
from cubing_algs.annotations import Permutation
from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import CORNER_NUMBER
from cubing_algs.constants import CORNER_VALID_ORIENTATIONS
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import EDGE_NUMBER
from cubing_algs.constants import EDGE_VALID_ORIENTATIONS
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import ORIENTATIONS
from cubing_algs.exceptions import InvalidCubeStateError
from cubing_algs.exceptions import InvalidFaceError
from cubing_algs.facelets import facelets_to_cubies


def compute_parity(permutation: Permutation) -> int:
    """
    Compute the parity of a permutation using cycle detection.

    Parity is 0 for even permutations (even number of transpositions)
    and 1 for odd permutations (odd number of transpositions).

    This uses an O(n) cycle-based algorithm: a cycle of length k
    requires (k-1) transpositions, so cycles of even length contribute
    odd parity and cycles of odd length contribute even parity.

    Args:
        permutation: List where permutation[i] is the value at position i.

    Returns:
        0 for even parity, 1 for odd parity.

    """
    n = len(permutation)
    visited = [False] * n
    parity = 0

    for i in range(n):
        if visited[i] or permutation[i] == i:
            continue

        # Count cycle length
        cycle_len = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = permutation[j]
            cycle_len += 1

        # Cycle of length k contributes (k-1) swaps
        parity ^= (cycle_len - 1) % 2

    return parity


def find_permutation_cycles(permutation: Permutation) -> list[list[int]]:
    """
    Find cycles in a permutation.

    A cycle is a sequence of positions where each position maps to the next,
    forming a closed loop. For example, [1, 2, 0] contains the cycle [0, 1, 2]
    meaning position 0 goes to 1, 1 goes to 2, and 2 goes back to 0.

    Args:
        permutation: List where permutation[i] is the destination of position i.

    Returns:
        List of cycles, each cycle is a list of position indices.
        Fixed points (where permutation[i] == i) are not included.

    """
    visited = [False] * len(permutation)
    cycles = []

    for i in range(len(permutation)):
        if not visited[i] and permutation[i] != i:
            cycle = []
            current = i
            while not visited[current]:
                visited[current] = True
                cycle.append(current)
                current = permutation[current]
            if len(cycle) > 1:  # pragma: no branch
                cycles.append(cycle)

    return cycles


def is_valid_permutation(permutation: Permutation, expected_size: int) -> bool:
    """
    Check if a list is a valid permutation of 0 to expected_size-1.

    Args:
        permutation: List to validate.
        expected_size: Expected number of elements (must contain 0 to size-1).

    Returns:
        True if valid permutation, False otherwise.

    """
    return (
        len(permutation) == expected_size
        and set(permutation) == set(range(expected_size))
    )


def is_valid_orientation(
        orientation: Orientation,
        expected_size: int,
        valid_values: set[int],
) -> bool:
    """
    Check if orientation values are all within valid range.

    Args:
        orientation: List of orientation values to validate.
        expected_size: Expected number of elements.
        valid_values: Set of valid orientation values.

    Returns:
        True if all orientations are valid, False otherwise.

    """
    return (
        len(orientation) == expected_size
        and all(o in valid_values for o in orientation)
    )


class VCubeIntegrityChecker:
    """
    Check integrity of VCube.

    This is a mixin class that expects the following from subclasses:
    - size, face_size, face_number, _state attributes
    - face_center_colors property
    """

    size: int
    face_size: int
    face_number: int

    _state: CubeFacelets

    @property
    def face_center_colors(self) -> tuple[str, ...]:
        """
        Return the center facelet characters for each face.

        Must be implemented by subclass.
        """
        raise NotImplementedError

    @property
    def has_fixed_centers(self) -> bool:
        """
        Check if the cube has fixed centers.

        Must be implemented by subclass.
        """
        raise NotImplementedError

    def check_integrity(self) -> bool:
        """
        Perform comprehensive integrity checks on the cube state.

        Returns:
            True if all integrity checks pass.

        """
        self.check_length()

        color_counts: dict[str, int] = {}
        for i in self._state:
            color_counts.setdefault(i, 0)
            color_counts[i] += 1

        self.check_characters(color_counts)
        self.check_colors(color_counts)

        if self.has_fixed_centers:
            self.check_centers()

        if self.size != 3:
            return True

        cp, co, ep, eo, so = facelets_to_cubies(self._state)

        self.check_corner_permutations(cp)
        self.check_corner_orientations(co)
        self.check_corner_sum(co)
        self.check_corner_colors(cp, co)

        self.check_edge_permutations(ep)
        self.check_edge_orientations(eo)
        self.check_edge_sum(eo)
        self.check_edge_colors(ep, eo)

        self.check_permutation_parity(cp, ep)

        self.check_center_orientations(so)

        return True

    def check_length(self) -> None:
        """
        Validate that the state string has the correct number of characters.

        Raises:
            InvalidCubeStateError: If state string length is incorrect.

        """
        expected_length = self.face_number * self.face_size

        if len(self._state) != expected_length:
            msg = f'State string must be { expected_length } characters long'
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_characters(color_counts: dict[str, int]) -> None:
        """
        Validate that only valid face characters are used in the state.

        Raises:
            InvalidCubeStateError: If invalid characters are found in state.

        """
        if set(color_counts.keys()) - set(FACE_ORDER):
            msg = (
                'State string can only '
                f'contains { " ".join(FACE_ORDER) } characters'
            )
            raise InvalidCubeStateError(msg)

    def check_colors(self, color_counts: dict[str, int]) -> None:
        """
        Validate that each color appears exactly the expected number of times.

        Raises:
            InvalidCubeStateError: If color counts are incorrect.

        """
        if not all(count == self.face_size for count in color_counts.values()):
            msg = f'State string must have { self.face_size } of each color'
            raise InvalidCubeStateError(msg)

    def check_centers(self) -> None:
        """
        Validate that all face centers are unique and properly positioned.

        Raises:
            InvalidCubeStateError: If centers are not unique.

        """
        actual_centers = set(self.face_center_colors)

        if len(actual_centers) != self.face_number:
            msg = 'Face centers must be unique'
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_corner_permutations(cp: CornerPermutation) -> None:
        """
        Validate corner permutation contains exactly one of each corner piece.

        Raises:
            InvalidCubeStateError: If corner permutation is invalid.

        """
        if not is_valid_permutation(cp, CORNER_NUMBER):
            msg = (
                'Corner permutation must contain exactly '
                'one instance of each corner (0-7)'
            )
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_corner_orientations(co: CornerOrientation) -> None:
        """
        Validate corner orientations are all valid values (0, 1, or 2).

        Raises:
            InvalidCubeStateError: If corner orientations are invalid.

        """
        if not is_valid_orientation(
                co, CORNER_NUMBER, CORNER_VALID_ORIENTATIONS,
        ):
            msg = 'Corner orientation must be 0, 1, or 2 for each corner'
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_corner_sum(co: CornerOrientation) -> None:
        """
        Validate corner orientation sum is divisible by 3.

        Raises:
            InvalidCubeStateError: If corner orientation sum is invalid.

        """
        if sum(co) % 3:
            msg = 'Sum of corner orientations must be divisible by 3'
            raise InvalidCubeStateError(msg)

    def check_corner_colors(
            self,
            cp: CornerPermutation,
            co: CornerOrientation,
    ) -> None:
        """
        Validate corner pieces have valid color combinations.

        Raises:
            InvalidCubeStateError: If corner colors are invalid.

        """
        # co is unused here but kept for API consistency with the other
        # check_* methods and to validate its length against cp via zip.
        for i, (corner_pos, _corner_ori) in enumerate(zip(cp, co, strict=True)):
            corner_facelets = [
                self._state[facelet]
                for facelet in CORNER_FACELET_MAP[corner_pos]
            ]
            if len(set(corner_facelets)) != 3:
                msg = (
                    f'Corner { i } must have 3 different colors, '
                    f'got { corner_facelets }'
                )
                raise InvalidCubeStateError(msg)

            for j, color1 in enumerate(corner_facelets):
                for _, color2 in enumerate(corner_facelets[j + 1:], j + 1):
                    if (
                            color1 in OPPOSITE_FACES
                            and OPPOSITE_FACES[color1] == color2
                    ):
                        msg = (
                            f'Corner { i } cannot have opposite colors '
                            f'{ color1 } and { color2 }'
                        )
                        raise InvalidCubeStateError(msg)

    @staticmethod
    def check_edge_permutations(ep: EdgePermutation) -> None:
        """
        Validate edge permutation contains exactly one of each edge piece.

        Raises:
            InvalidCubeStateError: If edge permutation is invalid.

        """
        if not is_valid_permutation(ep, EDGE_NUMBER):
            msg = (
                'Edge permutation must contain exactly '
                'one instance of each edge (0-11)'
            )
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_edge_orientations(eo: EdgeOrientation) -> None:
        """
        Validate edge orientations are all valid values (0 or 1).

        Raises:
            InvalidCubeStateError: If edge orientations are invalid.

        """
        if not is_valid_orientation(eo, EDGE_NUMBER, EDGE_VALID_ORIENTATIONS):
            msg = 'Edge orientation must be 0 or 1 for each edge'
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_edge_sum(eo: EdgeOrientation) -> None:
        """
        Validate edge orientation sum is even.

        Raises:
            InvalidCubeStateError: If edge orientation sum is invalid.

        """
        if sum(eo) % 2:
            msg = 'Sum of edge orientations must be even'
            raise InvalidCubeStateError(msg)

    def check_edge_colors(
            self,
            ep: EdgePermutation,
            eo: EdgeOrientation,
    ) -> None:
        """
        Validate edge pieces have valid color combinations.

        Raises:
            InvalidCubeStateError: If edge colors are invalid.

        """
        # eo is unused here but kept for API consistency with the other
        # check_* methods and to validate its length against ep via zip.
        for i, (edge_pos, _edge_ori) in enumerate(zip(ep, eo, strict=True)):
            edge_facelets = [
                self._state[facelet]
                for facelet in EDGE_FACELET_MAP[edge_pos]
            ]
            if len(set(edge_facelets)) != 2:
                msg = (
                    f'Edge { i } must have 2 different colors, '
                    f'got { edge_facelets }'
                )
                raise InvalidCubeStateError(msg)

            color1, color2 = edge_facelets
            if color1 in OPPOSITE_FACES and OPPOSITE_FACES[color1] == color2:
                msg = (
                    f'Edge { i } cannot have opposite colors '
                    f'{ color1 } and { color2 }'
                )
                raise InvalidCubeStateError(msg)

    @staticmethod
    def check_permutation_parity(
            cp: CornerPermutation,
            ep: EdgePermutation,
    ) -> None:
        """
        Validate corner and edge permutation parities match.

        Raises:
            InvalidCubeStateError: If permutation parities do not match.

        """
        if compute_parity(cp) != compute_parity(ep):
            msg = 'Corner and edge permutation parities must be equal'
            raise InvalidCubeStateError(msg)

    def check_center_orientations(self, so: Orientation) -> None:
        """
        Validate center orientations are all valid values.

        Raises:
            InvalidCubeStateError: If center orientations are invalid.

        """
        valid_orientations = set(range(self.face_number))

        if len(so) != self.face_number or any(
                orientation not in valid_orientations
                for orientation in so
        ):
            msg = (
                'Center orientation must be between 0 and 5 '
                'for each center'
            )
            raise InvalidCubeStateError(msg)

    @staticmethod
    def check_face_orientations(faces: CubeOrientation) -> tuple[str, str]:
        """
        Validate and parses face orientation specification.

        Args:
            faces: Face orientation string (1-2 characters).

        Returns:
            Tuple of (top_face, front_face) or (top_face, '') if one face.

        Raises:
            InvalidFaceError: If face orientation specification is invalid.

        """
        if not faces:
            msg = 'Specify at least one face to orient'
            raise InvalidFaceError(msg)

        if len(faces) > 2:
            msg = f'Too many faces ({ len(faces) })'
            raise InvalidFaceError(msg)

        top_face = faces[0]
        front_face = (len(faces) > 1 and faces[1]) or ''

        if top_face not in OPPOSITE_FACES:
            msg = f'{ top_face } is an invalid face'
            raise InvalidFaceError(msg)

        if OPPOSITE_FACES[top_face] == front_face:
            msg = f'{ top_face } { front_face } are opposed faces'
            raise InvalidFaceError(msg)

        if front_face and front_face not in OPPOSITE_FACES:
            msg = f'{ front_face } is an invalid face'
            raise InvalidFaceError(msg)

        if len(faces) == 2 and faces not in ORIENTATIONS:
            msg = f'{ faces } is not a valid orientation'
            raise InvalidFaceError(msg)

        return top_face, front_face
