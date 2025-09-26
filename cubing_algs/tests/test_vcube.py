import unittest
from io import StringIO
from typing import Any
from unittest.mock import patch

from cubing_algs.constants import FACES
from cubing_algs.constants import INITIAL_STATE
from cubing_algs.exceptions import InvalidCubeStateError
from cubing_algs.exceptions import InvalidFaceError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.masks import F2L_MASK
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.wide import unwide_rotation_moves
from cubing_algs.vcube import VCube


class VCubeTestCase(unittest.TestCase):
    maxDiff = None

    def test_state(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.state,
            INITIAL_STATE,
        )

        result = cube.rotate('R2 U2')
        self.assertEqual(
            result,
            'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBB',
        )

        self.assertEqual(
            result,
            cube.state,
        )

    def test_is_solved(self) -> None:
        cube = VCube()

        self.assertTrue(
            cube.is_solved,
        )

        cube.rotate('R2 U2')
        self.assertFalse(
            cube.is_solved,
        )

    def test_is_solved_oriented(self) -> None:
        cube = VCube()
        cube.rotate('z2')

        self.assertTrue(cube.is_solved)

    def test_rotate_history(self) -> None:
        cube = VCube()
        cube.rotate('R')

        self.assertEqual(cube.history, ['R'])

        cube.rotate('L', history=False)

        self.assertEqual(cube.history, ['R'])

    def test_rotate_move_history(self) -> None:
        cube = VCube()
        cube.rotate_move('R')

        self.assertEqual(cube.history, ['R'])

        cube.rotate_move('L', history=False)

        self.assertEqual(cube.history, ['R'])

    def test_copy(self) -> None:
        cube = VCube()
        cube.rotate('R2 F2 D2 B')
        copy = cube.copy()

        self.assertEqual(
            cube.state,
            copy.state,
        )
        self.assertFalse(copy.history)

    def test_full_copy(self) -> None:
        cube = VCube()
        cube.rotate('R2 F2 D2 B')
        copy = cube.copy(full=True)

        self.assertEqual(
            cube.state,
            copy.state,
        )
        self.assertTrue(copy.history)

    def test_from_cubies(self) -> None:
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        cube = VCube.from_cubies(cp, co, ep, eo, so)
        self.assertEqual(cube.state, facelets)

        cube = VCube()
        cube.rotate('F R')

        self.assertEqual(cube.state, facelets)

    def test_from_cubies_scheme(self) -> None:
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = '111111011111011011011010010010001001110110000111111100'

        cube = VCube.from_cubies(
            cp, co, ep, eo, so,
            F2L_MASK,
        )
        self.assertEqual(cube.state, facelets)

        cube = VCube(F2L_MASK, check=False)
        cube.rotate('F R')

        self.assertEqual(cube.state, facelets)

    def test_to_cubies(self) -> None:
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            VCube(facelets).to_cubies,
            (
                cp, co,
                ep, eo,
                so,
            ),
        )

    def test_from_cubies_equality(self) -> None:
        cube = VCube()
        cube.rotate('F R')
        n_cube = VCube.from_cubies(*cube.to_cubies)

        self.assertEqual(
            cube.state,
            n_cube.state,
        )

    def test_from_cubies_oriented_equality(self) -> None:
        cube = VCube()
        cube.rotate('F R x')
        n_cube = VCube.from_cubies(*cube.to_cubies)

        self.assertEqual(
            cube.state,
            n_cube.state,
        )

    def test_display(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        result = cube.display()

        lines = [line for line in result.split('\n') if line.strip()]

        self.assertEqual(len(lines), 9)
        self.assertEqual(len(cube.history), 3)

    def test_display_orientation_restore(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(len(cube.history), 3)

        state = cube.state

        cube.display(orientation='DF')

        self.assertEqual(len(cube.history), 3)
        self.assertEqual(state, cube.state)

    def test_display_orientation_different(self) -> None:
        cube_1 = VCube()
        cube_2 = VCube()

        view_1 = cube_1.display()
        view_2 = cube_2.display(orientation='DF')

        self.assertNotEqual(view_1, view_2)

    def test_get_face(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            cube.get_face('U'),
            'LUULUUFFF',
        )

        cube.rotate('z2')

        self.assertEqual(
            cube.get_face('U'),
            'BDDBDDBRR',
        )

    def test_get_face_by_center(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            cube.get_face_by_center('U'),
            'LUULUUFFF',
        )

        cube.rotate('z2')

        self.assertEqual(
            cube.get_face_by_center('U'),
            'FFFUULUUL',
        )

    def test_get_face_center(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            cube.get_face_by_center('U'),
            'LUULUUFFF',
        )

        cube.rotate('z2')

        self.assertEqual(
            cube.get_face_by_center('U'),
            'FFFUULUUL',
        )

    def test_get_face_index(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            cube.get_face_index('U'),
            0,
        )

        cube.rotate('z2')

        self.assertEqual(
            cube.get_face_index('U'),
            3,
        )

    def test_get_face_center_indexes(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            cube.get_face_center_indexes(),
            ['U', 'R', 'F', 'D', 'L', 'B'],
        )

        cube.rotate('z2')

        self.assertEqual(
            cube.get_face_center_indexes(),
            ['D', 'L', 'F', 'U', 'R', 'B'],
        )

    def test_str(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            str(cube),
            'U: LUULUUFFF\n'
            'R: LBBRRRRRR\n'
            'F: UUUFFDFFD\n'
            'D: RRBDDBDDB\n'
            'L: FFRLLDLLD\n'
            'B: LLDUBBUBB',
        )

    def test_repr(self) -> None:
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            repr(cube),
            "VCube('LUULUUFFFLBBRRRRRRUUUFFDFFDRRBDDBDDBFFRLLDLLDLLDUBBUBB')",
        )


class VCubeOrientedCopyTestCase(unittest.TestCase):
    maxDiff = None

    def test_oriented_copy_faces(self) -> None:
        cube = VCube()

        self.assertNotEqual(
            cube.state,
            cube.oriented_copy('DF').state,
        )

    def test_oriented_copy_top_only(self) -> None:
        cube = VCube()

        self.assertNotEqual(
            cube.state,
            cube.oriented_copy('D').state,
        )

    def test_oriented_copy_faces_stable(self) -> None:
        cube = VCube()
        base_state = cube.state
        cube.oriented_copy('UF')

        self.assertEqual(
            cube.state,
            base_state,
        )

    def test_oriented_copy_invalid_empty(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('')

    def test_oriented_copy_invalid_too_much(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FRU')

    def test_oriented_copy_invalid_top_face(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('TF')

    def test_oriented_copy_invalid_front_face(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FT')

    def test_oriented_copy_invalid_opposite_face(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FB')

    def test_oriented_copy_history_preservation(self) -> None:
        cube = VCube()
        cube.rotate('R F')

        self.assertEqual(
            len(cube.history),
            2,
        )

        oriented = cube.oriented_copy('DF')

        self.assertEqual(
            len(cube.history),
            2,
        )

        self.assertEqual(
            len(oriented.history),
            0,
        )

    def test_oriented_copy_history_tracking(self) -> None:
        cube = VCube()
        cube.rotate('R F')

        oriented = cube.oriented_copy('DF', full=True)

        self.assertEqual(
            oriented.history,
            ['R', 'F', 'z2'],
        )

        oriented = cube.oriented_copy('DR', full=True)

        self.assertEqual(
            oriented.history,
            ['R', 'F', 'y', 'z2'],
        )

    def test_all_edge_reorientation(self) -> None:
        orientations = [
            'UF', 'UB', 'UR', 'UL',
            'DF', 'DB', 'DR', 'DL',
            'FU', 'FD', 'FR', 'FL',
            'BU', 'BD', 'BR', 'BL',
            'RU', 'RD', 'RF', 'RB',
            'LU', 'LD', 'LF', 'LB',
        ]

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                cube = VCube().oriented_copy(orientation)

                self.assertEqual(
                    cube.state[4],
                    orientation[0],
                )

                self.assertEqual(
                    cube.state[21],
                    orientation[1],
                )

    def test_all_reorientation(self) -> None:
        orientations = [
            'U', 'R', 'F', 'D', 'L', 'B',
        ]

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                cube = VCube().oriented_copy(orientation)

                self.assertEqual(
                    cube.state[4],
                    orientation[0],
                )


class VCubeCheckIntegrityTestCase(unittest.TestCase):
    """Tests pour les nouvelles vérifications de check_integrity"""

    def test_initial(self) -> None:
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBB'

        cube = VCube(initial)

        self.assertEqual(
            cube.state,
            initial,
        )

    def test_invalid_length_no_check(self) -> None:
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        cube = VCube(initial, check=False)
        self.assertEqual(cube.state, initial)

    def test_invalid_length(self) -> None:
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string must be 54 characters long',
        ):
            VCube(initial)

    def test_invalid_character(self) -> None:
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBT'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string can only contains U R F D L B characters',
        ):
            VCube(initial)

    def test_invalid_face(self) -> None:
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBF'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string must have 9 of each color',
        ):
            VCube(initial)

    def test_invalid_centers_not_unique(self) -> None:
        invalid_state = (
            'UUUUUUUUR'
            'RRRRURRRR'
            'FFFFFFFFF'
            'DDDDDDDDD'
            'LLLLLLLLL'
            'BBBBBBBBB'
        )

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Face centers must be unique',
        ):
            VCube(invalid_state)

    def test_invalid_corner_orientation_sum(self) -> None:
        co = [1, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Sum of corner orientations must be divisible by 3',
        ):
            VCube().check_corner_sum(co)

    def test_invalid_edge_orientation_sum(self) -> None:
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Sum of edge orientations must be even',
        ):
            VCube().check_edge_sum(eo)

    def test_invalid_corner_permutation_duplicate(self) -> None:
        cp = [0, 0, 2, 3, 4, 5, 6, 7]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner permutation must contain exactly '
                'one instance of each corner',
        ):
            VCube().check_corner_permutations(cp)

    def test_invalid_edge_permutation_duplicate(self) -> None:
        ep = [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge permutation must contain exactly '
                'one instance of each edge',
        ):
            VCube().check_edge_permutations(ep)

    def test_invalid_corner_orientation_value(self) -> None:
        co = [3, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner orientation must be 0, 1, or 2 '
                'for each corner',
        ):
            VCube().check_corner_orientations(co)

    def test_invalid_edge_orientation_value(self) -> None:
        eo = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge orientation must be 0 or 1 '
                'for each edge',
        ):
            VCube().check_edge_orientations(eo)

    def test_invalid_center_orientation_value(self) -> None:
        so = [7, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Center orientation must be between 0 and 5 '
                'for each center',
        ):
            VCube().check_center_orientations(so)

    def test_invalid_permutation_parity(self) -> None:
        # Swap 0,1 = 1 inversion (odd)
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        # Identity = 0 inversions (even)
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner and edge permutation parities must be equal',
        ):
            VCube().check_permutation_parity(cp, ep)

    @unittest.mock.patch.object(VCube, 'check_colors')
    def test_invalid_corner_same_colors(self, *_: Any) -> None:
        invalid_state = list(INITIAL_STATE)
        # Corner URF: same color on the 2 faces
        invalid_state[8] = invalid_state[9]
        invalid_state = ''.join(invalid_state)

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner 0 must have 3 different colors, got',
        ):
            VCube(invalid_state)

    @unittest.mock.patch.object(VCube, 'check_colors')
    def test_invalid_edge_same_colors(self, *_: Any) -> None:
        invalid_state = list(INITIAL_STATE)
        # Edge UR: same color on the 2 faces
        invalid_state[5] = invalid_state[10]
        invalid_state = ''.join(invalid_state)

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge 0 must have 2 different colors, got ',
        ):
            VCube(invalid_state)

    @unittest.mock.patch.object(VCube, 'check_colors')
    def test_invalid_corner_opposite_colors(self, *_: Any) -> None:
        invalid_state = list(INITIAL_STATE)
        invalid_state[8] = 'U'  # Face U
        invalid_state[9] = 'D'  # Opposite face D
        invalid_state[20] = 'F'  # Third face
        invalid_state = ''.join(invalid_state)

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner 0 cannot have opposite colors '
                'U and D',
        ):
            VCube(invalid_state)

    @unittest.mock.patch.object(VCube, 'check_colors')
    def test_invalid_edge_opposite_colors(self, *_: Any) -> None:
        invalid_state = list(INITIAL_STATE)
        invalid_state[5] = 'F'
        invalid_state[10] = 'B'  # Opposite color
        invalid_state = ''.join(invalid_state)

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge 0 cannot have opposite colors '
                'F and B',
        ):
            VCube(invalid_state)

    def test_valid_complex_scramble(self) -> None:
        cube = VCube()
        complex_scramble = (
            "R U2 R' D' R U' R' D R' U "
            "R U' R' U R U2 R' U' R U' R'"
        )
        cube.rotate(complex_scramble)

        self.assertTrue(cube.check_integrity())

    def test_rotations_preserve_validity(self) -> None:
        cube = VCube()
        rotations = ['x', 'y', 'z', "x'", "y'", "z'", 'x2', 'y2', 'z2']

        for rotation in rotations:
            with self.subTest(rotation=rotation):
                cube_copy = cube.copy()
                cube_copy.rotate(rotation)
                self.assertTrue(cube_copy.check_integrity())

    def test_preserve_validity(self) -> None:
        cube = VCube()

        self.assertTrue(cube.check_integrity())

    def test_oriented_preserve_validity(self) -> None:
        cube = VCube()
        cube.rotate('z2')

        self.assertTrue(
            VCube(cube.state).check_integrity(),
        )


class VCubeRotateTestCase(unittest.TestCase):

    def test_rotate_types(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate(parse_moves('R F') + 'z2'),
            'BDDBDDRRRBLLDLLDLLDDDFFFFFFLLLFUUFUURRFRRURRUBBUBBUBBU',
        )

        cube = VCube()

        self.assertEqual(
            cube.rotate('z' + parse_moves('R F')),
            'LLFLLFDDDLUULUUFUUFFFFFFRRRUUURRBRRBDDRDDRDDBLBBLBBLBB',
        )

        cube = VCube()

        self.assertEqual(
            cube.rotate('z2' + parse_moves('R F')),
            'DDFDDFRRRDLLDLLFLLFFFFFFUUULLLUUBUUBRRURRURRBDBBDBBDBB',
        )

    def test_rotate_u(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('U'),
            'UUUUUUUUUBBBRRRRRRRRRFFFFFFDDDDDDDDDFFFLLLLLLLLLBBBBBB',
        )

        self.assertEqual(
            cube.rotate("U'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('U2'),
            'UUUUUUUUULLLRRRRRRBBBFFFFFFDDDDDDDDDRRRLLLLLLFFFBBBBBB',
        )

    def test_rotate_r(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('R'),
            'UUFUUFUUFRRRRRRRRRFFDFFDFFDDDBDDBDDBLLLLLLLLLUBBUBBUBB',
        )

        self.assertEqual(
            cube.rotate("R'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('R2'),
            'UUDUUDUUDRRRRRRRRRFFBFFBFFBDDUDDUDDULLLLLLLLLFBBFBBFBB',
        )

    def test_rotate_f(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('F'),
            'UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("F'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('F2'),
            'UUUUUUDDDLRRLRRLRRFFFFFFFFFUUUDDDDDDLLRLLRLLRBBBBBBBBB',
        )

    def test_rotate_d(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('D'),
            'UUUUUUUUURRRRRRFFFFFFFFFLLLDDDDDDDDDLLLLLLBBBBBBBBBRRR',
        )

        self.assertEqual(
            cube.rotate("D'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('D2'),
            'UUUUUUUUURRRRRRLLLFFFFFFBBBDDDDDDDDDLLLLLLRRRBBBBBBFFF',
        )

    def test_rotate_l(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('L'),
            'BUUBUUBUURRRRRRRRRUFFUFFUFFFDDFDDFDDLLLLLLLLLBBDBBDBBD',
        )

        self.assertEqual(
            cube.rotate("L'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('L2'),
            'DUUDUUDUURRRRRRRRRBFFBFFBFFUDDUDDUDDLLLLLLLLLBBFBBFBBF',
        )

    def test_rotate_b(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('B'),
            'RRRUUUUUURRDRRDRRDFFFFFFFFFDDDDDDLLLULLULLULLBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("B'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('B2'),
            'DDDUUUUUURRLRRLRRLFFFFFFFFFDDDDDDUUURLLRLLRLLBBBBBBBBB',
        )

    def test_rotate_m(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('M'),
            'UBUUBUUBURRRRRRRRRFUFFUFFUFDFDDFDDFDLLLLLLLLLBDBBDBBDB',
        )

        self.assertEqual(
            cube.rotate("M'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('M2'),
            'UDUUDUUDURRRRRRRRRFBFFBFFBFDUDDUDDUDLLLLLLLLLBFBBFBBFB',
        )

    def test_rotate_s(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('S'),
            'UUULLLUUURURRURRURFFFFFFFFFDDDRRRDDDLDLLDLLDLBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("S'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('S2'),
            'UUUDDDUUURLRRLRRLRFFFFFFFFFDDDUUUDDDLRLLRLLRLBBBBBBBBB',
        )

    def test_rotate_e(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('E'),
            'UUUUUUUUURRRFFFRRRFFFLLLFFFDDDDDDDDDLLLBBBLLLBBBRRRBBB',
        )

        self.assertEqual(
            cube.rotate("E'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('E2'),
            'UUUUUUUUURRRLLLRRRFFFBBBFFFDDDDDDDDDLLLRRRLLLBBBFFFBBB',
        )

    def test_rotate_x(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('x'),
            'FFFFFFFFFRRRRRRRRRDDDDDDDDDBBBBBBBBBLLLLLLLLLUUUUUUUUU',
        )

        self.assertEqual(
            cube.rotate("x'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('x2'),
            'DDDDDDDDDRRRRRRRRRBBBBBBBBBUUUUUUUUULLLLLLLLLFFFFFFFFF',
        )

    def test_rotate_y(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('y'),
            'UUUUUUUUUBBBBBBBBBRRRRRRRRRDDDDDDDDDFFFFFFFFFLLLLLLLLL',
        )

        self.assertEqual(
            cube.rotate("y'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('y2'),
            'UUUUUUUUULLLLLLLLLBBBBBBBBBDDDDDDDDDRRRRRRRRRFFFFFFFFF',
        )

    def test_rotate_z(self) -> None:
        cube = VCube()

        self.assertEqual(
            cube.rotate('z'),
            'LLLLLLLLLUUUUUUUUUFFFFFFFFFRRRRRRRRRDDDDDDDDDBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("z'"),
            INITIAL_STATE,
        )

        self.assertEqual(
            cube.rotate('z2'),
            'DDDDDDDDDLLLLLLLLLFFFFFFFFFUUUUUUUUURRRRRRRRRBBBBBBBBB',
        )

    def test_rotate_invalid_modifier(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('z3')

    def test_rotate_invalid_move(self) -> None:
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('T2')

    def test_real_case(self) -> None:
        cube = VCube()
        scramble = "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'"

        self.assertEqual(
            cube.rotate(scramble),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )

    def test_real_case_2(self) -> None:
        cube = VCube()
        scramble = "F R' F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2"

        self.assertEqual(
            cube.rotate(scramble),
            'LDBRUUBBDFLUFRLBDDLURLFDFRLLFUFDRFDBFUDBLBRUURBDFBRRLU',
        )

    def test_real_case_3(self) -> None:
        cube = VCube()
        scramble = "F R F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2 B'"

        self.assertEqual(
            cube.rotate(scramble),
            'UFFRUUBBDFLLFRDBUFLURLFDBRLDFUBDRLLRBDDDLBFRRDURBBLUFU',
        )

    def test_real_case_with_algorithm(self) -> None:
        cube = VCube()
        scramble = parse_moves(
            "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'",
        )

        self.assertEqual(
            cube.rotate(scramble),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )


class VCubeRotateWideSiGNTestCase(unittest.TestCase):

    def check_rotate(self, raw_move: str) -> None:
        base_move = Move(raw_move)

        for move, name in zip(
                [base_move, base_move.inverted, base_move.doubled],
                ['Base', 'Inverted', 'Doubled'],
                strict=True,
        ):
            with self.subTest(name, move=move):
                cube = VCube()
                cube_wide = VCube()

                self.assertEqual(
                    cube.rotate(move),
                    cube_wide.rotate(
                        parse_moves(
                            str(move),
                        ).transform(
                            unwide_rotation_moves,
                        ),
                    ),
                )

    def test_rotate_u(self) -> None:
        self.check_rotate('u')

    def test_rotate_r(self) -> None:
        self.check_rotate('r')

    def test_rotate_f(self) -> None:
        self.check_rotate('f')

    def test_rotate_d(self) -> None:
        self.check_rotate('d')

    def test_rotate_l(self) -> None:
        self.check_rotate('l')

    def test_rotate_b(self) -> None:
        self.check_rotate('b')


class VCubeRotateWideStandardTestCase(unittest.TestCase):

    def check_rotate(self, raw_move: str) -> None:
        base_move = Move(raw_move)

        for move, name in zip(
                [base_move, base_move.inverted, base_move.doubled],
                ['Base', 'Inverted', 'Doubled'],
                strict=True,
        ):
            with self.subTest(name, move=move):
                cube = VCube()
                cube_wide = VCube()

                self.assertEqual(
                    cube.rotate(move),
                    cube_wide.rotate(
                        parse_moves(
                            str(move),
                        ).transform(
                            unwide_rotation_moves,
                        ),
                    ),
                )

    def test_rotate_u(self) -> None:
        self.check_rotate('Uw')

    def test_rotate_r(self) -> None:
        self.check_rotate('Rw')

    def test_rotate_f(self) -> None:
        self.check_rotate('Fw')

    def test_rotate_d(self) -> None:
        self.check_rotate('Dw')

    def test_rotate_l(self) -> None:
        self.check_rotate('Lw')

    def test_rotate_b(self) -> None:
        self.check_rotate('Bw')


class VCubeRotateWideCancelTestCase(unittest.TestCase):

    def check_rotate(self, raw_move: str) -> None:
        base_move = Move(raw_move)

        cube = VCube()
        cube_wide = VCube()

        for move, name in zip(
                [base_move, base_move.inverted],
                ['Base', 'Inverted'],
                strict=True,
        ):
            with self.subTest(name, move=move):
                self.assertEqual(
                    cube.rotate(move),
                    cube_wide.rotate(
                        parse_moves(
                            str(move),
                        ).transform(
                            unwide_rotation_moves,
                        ),
                    ),
                )

        self.assertTrue(cube_wide.is_solved)
        self.assertTrue(cube.is_solved)

    def test_rotate_u(self) -> None:
        self.check_rotate('u')

    def test_rotate_r(self) -> None:
        self.check_rotate('r')

    def test_rotate_f(self) -> None:
        self.check_rotate('f')

    def test_rotate_d(self) -> None:
        self.check_rotate('d')

    def test_rotate_l(self) -> None:
        self.check_rotate('l')

    def test_rotate_b(self) -> None:
        self.check_rotate('b')


class VCubeRotateWideDoubleCancelTestCase(unittest.TestCase):

    def check_rotate(self, raw_move: str) -> None:
        move = Move(raw_move).doubled

        cube = VCube()
        cube_wide = VCube()

        self.assertEqual(
            cube.rotate(move),
            cube_wide.rotate(
                parse_moves(
                    str(move),
                ).transform(
                    unwide_rotation_moves,
                ),
            ),
        )

        self.assertEqual(
            cube.rotate(move),
            cube_wide.rotate(
                parse_moves(
                    str(move),
                ).transform(
                    unwide_rotation_moves,
                ),
            ),
        )

        self.assertTrue(cube_wide.is_solved)
        self.assertTrue(cube.is_solved)

    def test_rotate_u(self) -> None:
        self.check_rotate('u')

    def test_rotate_r(self) -> None:
        self.check_rotate('r')

    def test_rotate_f(self) -> None:
        self.check_rotate('f')

    def test_rotate_d(self) -> None:
        self.check_rotate('d')

    def test_rotate_l(self) -> None:
        self.check_rotate('l')

    def test_rotate_b(self) -> None:
        self.check_rotate('b')


class VCubeRotateWideAdvancedTestCase(unittest.TestCase):

    def check_rotate(self, raw_move: str) -> None:
        base_move = Move(raw_move)

        cube = VCube()
        cube.rotate("R U R' U'")
        cube_wide = VCube()
        cube_wide.rotate("R U R' U'")

        for move, name in zip(
                [base_move, base_move.inverted],
                ['Base', 'Inverted'],
                strict=True,
        ):
            with self.subTest(name, move=move):
                self.assertEqual(
                    cube.rotate(move),
                    cube_wide.rotate(
                        parse_moves(
                            str(move),
                        ).transform(
                            unwide_rotation_moves,
                        ),
                    ),
                )

    def test_rotate_u(self) -> None:
        self.check_rotate('u')

    def test_rotate_r(self) -> None:
        self.check_rotate('r')

    def test_rotate_f(self) -> None:
        self.check_rotate('f')

    def test_rotate_d(self) -> None:
        self.check_rotate('d')

    def test_rotate_l(self) -> None:
        self.check_rotate('l')

    def test_rotate_b(self) -> None:
        self.check_rotate('b')


class TestVCubeShow(unittest.TestCase):

    def setUp(self) -> None:
        self.cube = VCube()

    def test_show_default_parameters(self) -> None:
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show()

        output = captured_output.getvalue()

        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)

    def test_show_with_orientation(self) -> None:
        orientations = ['', 'DF', 'FR']

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    self.cube.show(orientation=orientation)

                output = captured_output.getvalue()
                self.assertIsInstance(output, str)
                self.assertGreater(len(output), 0)

    def test_show_with_mode(self) -> None:
        modes = ['f2l', 'oll', 'pll']

        for mode in modes:
            with self.subTest(mode=mode):
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    self.cube.show(mode=mode)

                output = captured_output.getvalue()
                self.assertIsInstance(output, str)
                self.assertGreater(len(output), 0)

    def test_show_scrambled_cube(self) -> None:
        self.cube.rotate("R U R' U'")

        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show()

        output = captured_output.getvalue()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)

        face_letters = ['U', 'R', 'F', 'D', 'L', 'B']
        for letter in face_letters:
            self.assertEqual(output.count(letter), 9)

    def test_show_output_consistency(self) -> None:
        captured_output1 = StringIO()
        with patch('sys.stdout', captured_output1):
            self.cube.show()
        output1 = captured_output1.getvalue()

        captured_output2 = StringIO()
        with patch('sys.stdout', captured_output2):
            self.cube.show()
        output2 = captured_output2.getvalue()

        self.assertEqual(output1, output2)

    def test_show_vs_display_consistency(self) -> None:
        display_result = self.cube.display()

        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show()
        show_result = captured_output.getvalue()

        self.assertEqual(display_result, show_result)

    def test_show_empty_parameters(self) -> None:
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show(orientation='')

        output = captured_output.getvalue()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)


class TestVCubeIsEqual(unittest.TestCase):

    def setUp(self) -> None:
        self.cube1 = VCube()
        self.cube2 = VCube()

    def test_is_equal_strict_identical_cubes(self) -> None:
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=True))
        self.assertTrue(self.cube1.is_equal(self.cube2))

    def test_is_equal_strict_identical_states_after_moves(self) -> None:
        self.cube1.rotate("R U R'")
        self.cube2.rotate("R U R'")
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=True))

    def test_is_equal_strict_different_states(self) -> None:
        self.cube1.rotate("R U R'")
        self.cube2.rotate("L U L'")
        self.assertFalse(self.cube1.is_equal(self.cube2, strict=True))

    def test_is_equal_strict_different_orientations(self) -> None:
        self.cube1.rotate('x')  # Rotate cube
        # Both cubes are solved but have different orientations
        self.assertFalse(self.cube1.is_equal(self.cube2, strict=True))

    def test_is_equal_non_strict_identical_cubes(self) -> None:
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_same_cube_different_orientations(self) -> None:
        self.cube1.rotate('x')  # Rotate the first cube
        # Both cubes should be considered equal in non-strict mode
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_complex_orientations(self) -> None:
        # Test various rotations that should still be equal in non-strict mode
        rotations = ['x', 'y', 'z', 'x2', 'y2', 'z2', "x'", "y'", "z'"]

        for rotation in rotations:
            with self.subTest(rotation=rotation):
                cube1 = VCube()
                cube2 = VCube()
                cube1.rotate(rotation)
                self.assertTrue(cube1.is_equal(cube2, strict=False))

    def test_is_equal_non_strict_combined_rotations(self) -> None:
        self.cube1.rotate('x y z')
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_scrambled_cubes_same_pattern(self) -> None:
        scramble = "R U R' U'"
        self.cube1.rotate(scramble)
        self.cube2.rotate(scramble)

        # Both have same pattern
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=True))

        # Apply different orientations
        self.cube1.rotate('x')
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_different_scrambles(self) -> None:
        self.cube1.rotate("R U R'")
        self.cube2.rotate("L U L'")
        self.assertFalse(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_scramble_vs_solved(self) -> None:
        self.cube1.rotate("R U R' U'")  # Not solved
        # cube2 remains solved
        self.assertFalse(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_non_strict_scrambled_and_oriented(self) -> None:
        # Apply same scramble to both cubes
        scramble = "R U2 R' D' R U' R' D"
        self.cube1.rotate(scramble)
        self.cube2.rotate(scramble)

        # Orient first cube differently
        self.cube1.rotate('y x')

        # Should still be equal in non-strict mode
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

        # But not in strict mode
        self.assertFalse(self.cube1.is_equal(self.cube2, strict=True))

    def test_is_equal_with_invalid_states(self) -> None:
        # Test with cubes that have invalid states but same pattern
        invalid_state = list(INITIAL_STATE)
        invalid_state[4] = 'R'   # Change top center to R
        invalid_state[22] = 'D'  # Change front center to D
        invalid_state = ''.join(invalid_state)

        cube1 = VCube(invalid_state, check=False)
        cube2 = VCube(invalid_state, check=False)

        self.assertTrue(cube1.is_equal(cube2, strict=True))
        self.assertTrue(cube1.is_equal(cube2, strict=False))

    def test_is_equal_edge_case_empty_history(self) -> None:
        # Test that history doesn't affect equality
        self.cube1.rotate("R U R'", history=True)
        self.cube2.rotate("R U R'", history=False)

        self.assertTrue(self.cube1.is_equal(self.cube2, strict=True))
        self.assertTrue(self.cube1.is_equal(self.cube2, strict=False))

    def test_is_equal_reflexive_property(self) -> None:
        # A cube should always be equal to itself
        self.assertTrue(self.cube1.is_equal(self.cube1, strict=True))
        self.assertTrue(self.cube1.is_equal(self.cube1, strict=False))

        # Even after moves
        self.cube1.rotate("R U R' U'")
        self.assertTrue(self.cube1.is_equal(self.cube1, strict=True))
        self.assertTrue(self.cube1.is_equal(self.cube1, strict=False))

    def test_is_equal_symmetric_property(self) -> None:
        # If A equals B, then B equals A
        cube_oriented = VCube()
        cube_oriented.rotate('x')  # Apply orientation rotation

        test_cases = [
            (VCube(), VCube()),  # Both solved
            (VCube(), cube_oriented),  # One oriented (for non-strict)
        ]

        for cube_a, cube_b in test_cases:
            with self.subTest(cube_a=repr(cube_a), cube_b=repr(cube_b)):
                # Strict mode
                result_ab = cube_a.is_equal(cube_b, strict=True)
                result_ba = cube_b.is_equal(cube_a, strict=True)
                self.assertEqual(result_ab, result_ba)

                # Non-strict mode
                result_ab_ns = cube_a.is_equal(cube_b, strict=False)
                result_ba_ns = cube_b.is_equal(cube_a, strict=False)
                self.assertEqual(result_ab_ns, result_ba_ns)


class TestVCubeOrientation(unittest.TestCase):

    def setUp(self) -> None:
        self.cube = VCube()

    def test_orientation_solved_cube(self) -> None:
        # Solved cube should have 'UF' orientation (top=U, front=F)
        self.assertEqual(self.cube.orientation, 'UF')

    def test_orientation_after_basic_rotations(self) -> None:
        # Test each basic rotation
        expected_orientations = {
            'x': 'FD',   # x rotation: top becomes front, front becomes down
            'y': 'UR',   # y rotation: top stays, front becomes right
            'z': 'LF',   # z rotation: top becomes left, front stays
            "x'": 'BU',  # x' rotation: top becomes back, front becomes up
            "y'": 'UL',  # y' rotation: top stays, front becomes left
            "z'": 'RF',  # z' rotation: top becomes right, front stays
        }

        for move, expected in expected_orientations.items():
            with self.subTest(move=move):
                cube = VCube()
                cube.rotate(move)
                self.assertEqual(cube.orientation, expected)

    def test_orientation_after_double_rotations(self) -> None:
        expected_orientations = {
            'x2': 'DB',  # x2: top becomes down, front becomes back
            'y2': 'UB',  # y2: top stays, front becomes back
            'z2': 'DF',  # z2: top becomes down, front stays
        }

        for move, expected in expected_orientations.items():
            with self.subTest(move=move):
                cube = VCube()
                cube.rotate(move)
                self.assertEqual(cube.orientation, expected)

    def test_orientation_combined_rotations(self) -> None:
        # Test combinations of rotations
        test_cases = [
            ('x y', 'FR'),    # x then y
            ('y x', 'RD'),    # y then x
            ('z x', 'FR'),    # z then x
            ('x y z', 'DR'),  # x, y, then z
        ]

        for moves, expected in test_cases:
            with self.subTest(moves=moves):
                cube = VCube()
                cube.rotate(moves)
                self.assertEqual(cube.orientation, expected)

    def test_orientation_with_face_moves(self) -> None:
        # Basic face moves (R, U, F, D, B) shouldn't change center positions
        # Slice moves (M, E, S) are expected to change centers
        face_moves = ['R', 'U', 'F', 'D', 'B', 'L']

        for move in face_moves:
            with self.subTest(move=move):
                cube = VCube()
                original_orientation = cube.orientation
                cube.rotate(move)
                self.assertEqual(cube.orientation, original_orientation)

    def test_orientation_with_slice_moves(self) -> None:
        # Slice moves (M, E, S) are expected to change center positions
        slice_moves = {
            'M': 'BU',  # Middle slice affects centers
            'E': 'UL',  # Equatorial slice affects centers
            'S': 'LF',  # Standing slice affects centers
        }

        for move, expected in slice_moves.items():
            with self.subTest(move=move):
                cube = VCube()
                cube.rotate(move)
                self.assertEqual(cube.orientation, expected)

    def test_orientation_with_complex_sequences(self) -> None:
        # Test that face moves don't affect orientation
        # even in complex sequences
        # Using only moves that don't change centers: R, U, F, D, B L
        original_orientation = self.cube.orientation

        # Complex sequence with only face moves that preserve centers
        self.cube.rotate("R U R' U' R' F R2 U' R' U' R U R' F'")
        self.assertEqual(self.cube.orientation, original_orientation)

    def test_orientation_scrambled_cube(self) -> None:
        # Orientation should still work correctly on scrambled cubes
        self.cube.rotate("R U R' U' F R F' U2 R' U R U2")
        original_orientation = self.cube.orientation

        # Apply rotation to scrambled cube
        self.cube.rotate('x')
        self.assertNotEqual(self.cube.orientation, original_orientation)
        self.assertEqual(self.cube.orientation, 'FD')

    def test_orientation_all_24_possible_orientations(self) -> None:
        # Test all 24 possible orientations of a cube
        # Each face can be on top (6),
        # and for each top face, 4 different front faces
        orientations_found = set()

        # Generate various rotation combinations to cover all orientations
        rotation_sequences = [
            '',         # UF
            'x',        # FR
            'x2',       # DB
            "x'",       # BU
            'y',        # UL
            'y x',      # LU
            'y x2',     # BD
            "y x'",     # DL
            'y2',       # UB
            'y2 x',     # BR
            'y2 x2',    # DF
            "y2 x'",    # FD
            "y'",       # UR
            "y' x",     # RD
            "y' x2",    # BF
            "y' x'",    # FB
            'z',        # LF
            'z x',      # FU
            'z x2',     # RB
            "z x'",     # BL
            "z'",       # RF
            "z' x",     # FD
            "z' x2",    # LB
            "z' x'",    # BR
        ]

        for moves in rotation_sequences:
            cube = VCube()
            if moves:
                cube.rotate(moves)
            orientation = cube.orientation
            orientations_found.add(orientation)

        # Should find multiple unique orientations
        self.assertEqual(len(orientations_found), 24)

    def test_orientation_consistency_with_oriented_copy(self) -> None:
        # Test that orientation property is consistent with oriented_copy method
        target_orientations = ['UF', 'DF', 'FR', 'BL', 'UL', 'DR']

        for target in target_orientations:
            with self.subTest(target=target):
                cube = VCube()
                oriented_cube = cube.oriented_copy(target)
                self.assertEqual(oriented_cube.orientation, target)

    def test_orientation_with_invalid_state(self) -> None:
        # Test orientation with an unchecked/invalid state
        # Create a state with modified centers
        invalid_state = list(INITIAL_STATE)
        invalid_state[4] = 'R'   # Change top center to R
        invalid_state[22] = 'D'  # Change front center to D
        invalid_state = ''.join(invalid_state)

        cube = VCube(invalid_state, check=False)
        self.assertEqual(cube.orientation, 'RD')

    def test_orientation_property_type(self) -> None:
        # Test that orientation always returns a string
        self.assertIsInstance(self.cube.orientation, str)

        # Should always be exactly 2 characters
        self.assertEqual(len(self.cube.orientation), 2)

        # After moves, still 2 characters
        self.cube.rotate("x y z R U R'")
        self.assertIsInstance(self.cube.orientation, str)
        self.assertEqual(len(self.cube.orientation), 2)

    def test_orientation_valid_face_characters(self) -> None:
        # Orientation should only contain valid face characters
        rotations = ['', 'x', 'y', 'z', 'x2', 'y2', 'z2', 'x y', 'z x y']

        for rotation in rotations:
            with self.subTest(rotation=rotation):
                cube = VCube()
                if rotation:
                    cube.rotate(rotation)

                orientation = cube.orientation
                self.assertTrue(
                    all(char in FACES for char in orientation),
                )

    def test_orientation_specific_positions(self) -> None:
        # Test that orientation correctly reads positions 4 and 21
        cube = VCube()

        # Verify initial state
        self.assertEqual(cube.state[4], 'U')   # Top center
        self.assertEqual(cube.state[21], 'F')  # Front center
        self.assertEqual(cube.orientation, 'UF')

        # After x rotation
        cube.rotate('x')
        self.assertEqual(cube.state[4], 'F')   # Top center now F
        self.assertEqual(cube.state[21], 'D')  # Front center now D
        self.assertEqual(cube.orientation, 'FD')

    def test_orientation_edge_case_positions(self) -> None:
        # Test edge case: what if centers are swapped in an invalid way
        state = list(VCube().state)
        # Swap some centers to create an unusual but testable state
        state[4] = 'D'   # Top center = D
        state[22] = 'U'  # Front center = U
        state[31] = 'F'  # Bottom center = F (to maintain some validity)

        cube = VCube(''.join(state), check=False)
        self.assertEqual(cube.orientation, 'DU')
