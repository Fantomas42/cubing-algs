# ruff: noqa: PLR6301
from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.exceptions import InvalidCubeStateError
from cubing_algs.exceptions import InvalidFaceError
from cubing_algs.facelets import facelets_to_cubies

CORNER_NUMBER = 8
CORNER_VALID_ORIENTATIONS = {0, 1, 2}

EDGE_NUMBER = 12
EDGE_VALID_ORIENTATIONS = {0, 1}


def count_inversions(permutation: list[int]) -> int:
    inversions = 0

    for i in range(len(permutation)):
        for j in range(i + 1, len(permutation)):
            if permutation[i] > permutation[j]:
                inversions += 1

    return inversions


class VCubeIntegrityChecker:
    """
    Check integrity of VCube
    """
    size: int
    face_size: int
    face_number: int

    _state: str

    def check_integrity(self) -> bool:
        self.check_length()

        color_counts: dict[str, int] = {}
        for i in self._state:
            color_counts.setdefault(i, 0)
            color_counts[i] += 1

        self.check_characters(color_counts)
        self.check_colors(color_counts)
        self.check_centers()

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
        expected_length = self.face_number * self.face_size

        if len(self._state) != expected_length:
            msg = f'State string must be { expected_length } characters long'
            raise InvalidCubeStateError(msg)

    def check_characters(self, color_counts: dict[str, int]) -> None:
        if set(color_counts.keys()) - set(FACE_ORDER):
            msg = (
                'State string can only '
                f'contains { " ".join(FACE_ORDER) } characters'
            )
            raise InvalidCubeStateError(msg)

    def check_colors(self, color_counts: dict[str, int]) -> None:
        if not all(count == self.face_size for count in color_counts.values()):
            msg = f'State string must have { self.face_size } of each color'
            raise InvalidCubeStateError(msg)

    def check_centers(self) -> None:
        actual_centers = set(self.get_face_center_indexes())

        if len(actual_centers) != self.face_number:
            msg = 'Face centers must be unique'
            raise InvalidCubeStateError(msg)

    def check_corner_permutations(self, cp: list[int]) -> None:
        if len(cp) != CORNER_NUMBER or set(cp) != set(range(CORNER_NUMBER)):
            msg = (
                'Corner permutation must contain exactly '
                'one instance of each corner (0-7)'
            )
            raise InvalidCubeStateError(msg)

    def check_corner_orientations(self, co: list[int]) -> None:
        if len(co) != CORNER_NUMBER or any(
                orientation not in CORNER_VALID_ORIENTATIONS
                for orientation in co
        ):
            msg = 'Corner orientation must be 0, 1, or 2 for each corner'
            raise InvalidCubeStateError(msg)

    def check_corner_sum(self, co: list[int]) -> None:
        if sum(co) % 3:
            msg = 'Sum of corner orientations must be divisible by 3'
            raise InvalidCubeStateError(msg)

    def check_corner_colors(self, cp: list[int], co: list[int]) -> None:
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

    def check_edge_permutations(self, ep: list[int]) -> None:
        if len(ep) != EDGE_NUMBER or set(ep) != set(range(EDGE_NUMBER)):
            msg = (
                'Edge permutation must contain exactly '
                'one instance of each edge (0-11)'
            )
            raise InvalidCubeStateError(msg)

    def check_edge_orientations(self, eo: list[int]) -> None:
        if len(eo) != EDGE_NUMBER or any(
                orientation not in EDGE_VALID_ORIENTATIONS
                for orientation in eo
        ):
            msg = 'Edge orientation must be 0 or 1 for each edge'
            raise InvalidCubeStateError(msg)

    def check_edge_sum(self, eo: list[int]) -> None:
        if sum(eo) % 2:
            msg = 'Sum of edge orientations must be even'
            raise InvalidCubeStateError(msg)

    def check_edge_colors(self, ep: list[int], eo: list[int]) -> None:
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

    def check_permutation_parity(self, cp: list[int], ep: list[int]) -> None:
        corner_parity = count_inversions(cp) % 2
        edge_parity = count_inversions(ep) % 2

        if corner_parity != edge_parity:
            msg = 'Corner and edge permutation parities must be equal'
            raise InvalidCubeStateError(msg)

    def check_center_orientations(self, so: list[int]) -> None:
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

    def check_face_orientations(self, faces: str) -> tuple[str, str]:
        if not faces:
            msg = 'Specify at leat one face to orient'
            raise InvalidFaceError(msg)

        if len(faces) > 2:
            msg = f'Too much faces ({ len(faces) })'
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

        return top_face, front_face
