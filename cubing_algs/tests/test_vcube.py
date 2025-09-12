import unittest
from io import StringIO
from unittest.mock import patch

from cubing_algs.constants import INITIAL_STATE
from cubing_algs.exceptions import InvalidCubeStateError
from cubing_algs.exceptions import InvalidFaceError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.masks import F2L_MASK
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.fat import unfat_rotation_moves
from cubing_algs.vcube import VCube


class VCubeTestCase(unittest.TestCase):
    maxDiff = None

    def test_state(self):
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

    def test_is_solved(self):
        cube = VCube()

        self.assertTrue(
            cube.is_solved,
        )

        cube.rotate('R2 U2')
        self.assertFalse(
            cube.is_solved,
        )

    def test_is_solved_oriented(self):
        cube = VCube()
        cube.rotate('z2')

        self.assertTrue(cube.is_solved)

    def test_rotate_history(self):
        cube = VCube()
        cube.rotate('R')

        self.assertEqual(cube.history, ['R'])

        cube.rotate('L', history=False)

        self.assertEqual(cube.history, ['R'])

    def test_rotate_move_history(self):
        cube = VCube()
        cube.rotate_move('R')

        self.assertEqual(cube.history, ['R'])

        cube.rotate_move('L', history=False)

        self.assertEqual(cube.history, ['R'])

    def test_copy(self):
        cube = VCube()
        cube.rotate('R2 F2 D2 B')
        copy = cube.copy()

        self.assertEqual(
            cube.state,
            copy.state,
        )
        self.assertFalse(copy.history)

    def test_full_copy(self):
        cube = VCube()
        cube.rotate('R2 F2 D2 B')
        copy = cube.copy(full=True)

        self.assertEqual(
            cube.state,
            copy.state,
        )
        self.assertTrue(copy.history)

    def test_from_cubies(self):
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

    def test_from_cubies_scheme(self):
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

    def test_to_cubies(self):
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

    def test_from_cubies_equality(self):
        cube = VCube()
        cube.rotate('F R')
        n_cube = VCube.from_cubies(*cube.to_cubies)

        self.assertEqual(
            cube.state,
            n_cube.state,
        )

    def test_from_cubies_oriented_equality(self):
        cube = VCube()
        cube.rotate('F R x')
        n_cube = VCube.from_cubies(*cube.to_cubies)

        self.assertEqual(
            cube.state,
            n_cube.state,
        )

    def test_display(self):
        cube = VCube()
        cube.rotate('F R U')

        result = cube.display()

        lines = [line for line in result.split('\n') if line.strip()]

        self.assertEqual(len(lines), 9)
        self.assertEqual(len(cube.history), 3)

    def test_display_orientation_restore(self):
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(len(cube.history), 3)

        state = cube.state

        cube.display(orientation='DF')

        self.assertEqual(len(cube.history), 3)
        self.assertEqual(state, cube.state)

    def test_display_orientation_different(self):
        cube_1 = VCube()
        cube_2 = VCube()

        view_1 = cube_1.display()
        view_2 = cube_2.display(orientation='DF')

        self.assertNotEqual(view_1, view_2)

    def test_get_face(self):
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

    def test_get_face_by_center(self):
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

    def test_get_face_center(self):
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

    def test_get_face_index(self):
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

    def test_get_face_center_indexes(self):
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

    def test_str(self):
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

    def test_repr(self):
        cube = VCube()
        cube.rotate('F R U')

        self.assertEqual(
            repr(cube),
            "VCube('LUULUUFFFLBBRRRRRRUUUFFDFFDRRBDDBDDBFFRLLDLLDLLDUBBUBB')",
        )


class VCubeOrientedCopyTestCase(unittest.TestCase):
    maxDiff = None

    def test_oriented_copy_faces(self):
        cube = VCube()

        self.assertNotEqual(
            cube.state,
            cube.oriented_copy('DF').state,
        )

    def test_oriented_copy_top_only(self):
        cube = VCube()

        self.assertNotEqual(
            cube.state,
            cube.oriented_copy('D').state,
        )

    def test_oriented_copy_faces_stable(self):
        cube = VCube()
        base_state = cube.state
        cube.oriented_copy('UF')

        self.assertEqual(
            cube.state,
            base_state,
        )

    def test_oriented_copy_invalid_empty(self):
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('')

    def test_oriented_copy_invalid_too_much(self):
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FRU')

    def test_oriented_copy_invalid_top_face(self):
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('TF')

    def test_oriented_copy_invalid_front_face(self):
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FT')

    def test_oriented_copy_invalid_opposite_face(self):
        cube = VCube()

        with self.assertRaises(InvalidFaceError):
            cube.oriented_copy('FB')

    def test_oriented_copy_history_preservation(self):
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

    def test_oriented_copy_history_tracking(self):
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

    def test_all_edge_reorientation(self):
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

    def test_all_reorientation(self):
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

    def test_initial(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBB'

        cube = VCube(initial)

        self.assertEqual(
            cube.state,
            initial,
        )

    def test_invalid_length_no_check(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        cube = VCube(initial, check=False)
        self.assertEqual(cube.state, initial)

    def test_invalid_length(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string must be 54 characters long',
        ):
            VCube(initial)

    def test_invalid_character(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBT'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string can only contains U R F D L B characters',
        ):
            VCube(initial)

    def test_invalid_face(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBF'

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'State string must have 9 of each color',
        ):
            VCube(initial)

    def test_invalid_centers_not_unique(self):
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

    def test_invalid_corner_orientation_sum(self):
        co = [1, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Sum of corner orientations must be divisible by 3',
        ):
            VCube().check_corner_sum(co)

    def test_invalid_edge_orientation_sum(self):
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Sum of edge orientations must be even',
        ):
            VCube().check_edge_sum(eo)

    def test_invalid_corner_permutation_duplicate(self):
        cp = [0, 0, 2, 3, 4, 5, 6, 7]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner permutation must contain exactly '
                'one instance of each corner',
        ):
            VCube().check_corner_permutations(cp)

    def test_invalid_edge_permutation_duplicate(self):
        ep = [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge permutation must contain exactly '
                'one instance of each edge',
        ):
            VCube().check_edge_permutations(ep)

    def test_invalid_corner_orientation_value(self):
        co = [3, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Corner orientation must be 0, 1, or 2 '
                'for each corner',
        ):
            VCube().check_corner_orientations(co)

    def test_invalid_edge_orientation_value(self):
        eo = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Edge orientation must be 0 or 1 '
                'for each edge',
        ):
            VCube().check_edge_orientations(eo)

    def test_invalid_center_orientation_value(self):
        so = [7, 0, 0, 0, 0, 0]

        with self.assertRaisesRegex(
                InvalidCubeStateError,
                'Center orientation must be between 0 and 5 '
                'for each center',
        ):
            VCube().check_center_orientations(so)

    def test_invalid_permutation_parity(self):
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
    def test_invalid_corner_same_colors(self, *_):
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
    def test_invalid_edge_same_colors(self, *_):
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
    def test_invalid_corner_opposite_colors(self, *_):
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
    def test_invalid_edge_opposite_colors(self, *_):
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

    def test_valid_complex_scramble(self):
        cube = VCube()
        complex_scramble = (
            "R U2 R' D' R U' R' D R' U "
            "R U' R' U R U2 R' U' R U' R'"
        )
        cube.rotate(complex_scramble)

        self.assertTrue(cube.check_integrity())

    def test_rotations_preserve_validity(self):
        cube = VCube()
        rotations = ['x', 'y', 'z', "x'", "y'", "z'", 'x2', 'y2', 'z2']

        for rotation in rotations:
            with self.subTest(rotation=rotation):
                cube_copy = cube.copy()
                cube_copy.rotate(rotation)
                self.assertTrue(cube_copy.check_integrity())

    def test_preserve_validity(self):
        cube = VCube()

        self.assertTrue(cube.check_integrity())

    def test_oriented_preserve_validity(self):
        cube = VCube()
        cube.rotate('z2')

        self.assertTrue(
            VCube(cube.state).check_integrity(),
        )


class VCubeRotateTestCase(unittest.TestCase):

    def test_rotate_types(self):
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

    def test_rotate_u(self):
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

    def test_rotate_r(self):
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

    def test_rotate_f(self):
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

    def test_rotate_d(self):
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

    def test_rotate_l(self):
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

    def test_rotate_b(self):
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

    def test_rotate_m(self):
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

    def test_rotate_s(self):
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

    def test_rotate_e(self):
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

    def test_rotate_x(self):
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

    def test_rotate_y(self):
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

    def test_rotate_z(self):
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

    def test_rotate_invalid_modifier(self):
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('z3')

    def test_rotate_invalid_move(self):
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('T2')

    def test_real_case(self):
        cube = VCube()
        scramble = "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'"

        self.assertEqual(
            cube.rotate(scramble),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )

    def test_real_case_2(self):
        cube = VCube()
        scramble = "F R' F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2"

        self.assertEqual(
            cube.rotate(scramble),
            'LDBRUUBBDFLUFRLBDDLURLFDFRLLFUFDRFDBFUDBLBRUURBDFBRRLU',
        )

    def test_real_case_3(self):
        cube = VCube()
        scramble = "F R F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2 B'"

        self.assertEqual(
            cube.rotate(scramble),
            'UFFRUUBBDFLLFRDBUFLURLFDBRLDFUBDRLLRBDDDLBFRRDURBBLUFU',
        )

    def test_real_case_with_algorithm(self):
        cube = VCube()
        scramble = parse_moves(
            "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'",
        )

        self.assertEqual(
            cube.rotate(scramble),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )


class VCubeRotateWideTestCase(unittest.TestCase):

    def check_rotate(self, raw_move):
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
                            unfat_rotation_moves,
                        ),
                    ),
                )

    def test_rotate_u(self):
        self.check_rotate('u')

    def test_rotate_r(self):
        self.check_rotate('r')

    def test_rotate_f(self):
        self.check_rotate('f')

    def test_rotate_d(self):
        self.check_rotate('d')

    def test_rotate_l(self):
        self.check_rotate('l')

    def test_rotate_b(self):
        self.check_rotate('b')


class VCubeRotateWideCancelTestCase(unittest.TestCase):

    def check_rotate(self, raw_move):
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
                            unfat_rotation_moves,
                        ),
                    ),
                )

        self.assertTrue(cube_wide.is_solved)
        self.assertTrue(cube.is_solved)

    def test_rotate_u(self):
        self.check_rotate('u')

    def test_rotate_r(self):
        self.check_rotate('r')

    def test_rotate_f(self):
        self.check_rotate('f')

    def test_rotate_d(self):
        self.check_rotate('d')

    def test_rotate_l(self):
        self.check_rotate('l')

    def test_rotate_b(self):
        self.check_rotate('b')


class VCubeRotateWideDoubleCancelTestCase(unittest.TestCase):

    def check_rotate(self, raw_move):
        move = Move(raw_move).doubled

        cube = VCube()
        cube_wide = VCube()

        self.assertEqual(
            cube.rotate(move),
            cube_wide.rotate(
                parse_moves(
                    str(move),
                ).transform(
                    unfat_rotation_moves,
                ),
            ),
        )

        self.assertEqual(
            cube.rotate(move),
            cube_wide.rotate(
                parse_moves(
                    str(move),
                ).transform(
                    unfat_rotation_moves,
                ),
            ),
        )

        self.assertTrue(cube_wide.is_solved)
        self.assertTrue(cube.is_solved)

    def test_rotate_u(self):
        self.check_rotate('u')

    def test_rotate_r(self):
        self.check_rotate('r')

    def test_rotate_f(self):
        self.check_rotate('f')

    def test_rotate_d(self):
        self.check_rotate('d')

    def test_rotate_l(self):
        self.check_rotate('l')

    def test_rotate_b(self):
        self.check_rotate('b')


class VCubeRotateWideAdvancedTestCase(unittest.TestCase):

    def check_rotate(self, raw_move):
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
                            unfat_rotation_moves,
                        ),
                    ),
                )

    def test_rotate_u(self):
        self.check_rotate('u')

    def test_rotate_r(self):
        self.check_rotate('r')

    def test_rotate_f(self):
        self.check_rotate('f')

    def test_rotate_d(self):
        self.check_rotate('d')

    def test_rotate_l(self):
        self.check_rotate('l')

    def test_rotate_b(self):
        self.check_rotate('b')


class TestVCubeShow(unittest.TestCase):

    def setUp(self):
        self.cube = VCube()

    def test_show_default_parameters(self):
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show()

        output = captured_output.getvalue()

        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)

    def test_show_with_orientation(self):
        orientations = ['', 'DF', 'FR']

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    self.cube.show(orientation=orientation)

                output = captured_output.getvalue()
                self.assertIsInstance(output, str)
                self.assertGreater(len(output), 0)

    def test_show_with_mode(self):
        modes = ['f2l', 'oll', 'pll']

        for mode in modes:
            with self.subTest(mode=mode):
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    self.cube.show(mode=mode)

                output = captured_output.getvalue()
                self.assertIsInstance(output, str)
                self.assertGreater(len(output), 0)

    def test_show_scrambled_cube(self):
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

    def test_show_output_consistency(self):
        captured_output1 = StringIO()
        with patch('sys.stdout', captured_output1):
            self.cube.show()
        output1 = captured_output1.getvalue()

        captured_output2 = StringIO()
        with patch('sys.stdout', captured_output2):
            self.cube.show()
        output2 = captured_output2.getvalue()

        self.assertEqual(output1, output2)

    def test_show_vs_display_consistency(self):
        display_result = self.cube.display()

        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show()
        show_result = captured_output.getvalue()

        self.assertEqual(display_result, show_result)

    def test_show_empty_parameters(self):
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            self.cube.show(orientation='')

        output = captured_output.getvalue()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)
