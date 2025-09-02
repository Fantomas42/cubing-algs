import unittest
from io import StringIO
from unittest.mock import patch

from cubing_algs.constants import INITIAL_STATE
from cubing_algs.move import InvalidMoveError
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.fat import unfat_rotation_moves
from cubing_algs.vcube import InvalidCubeStateError
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

    def test_initial(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBB'

        cube = VCube(initial)

        self.assertEqual(
            cube.state,
            initial,
        )

    def test_initial_bad_size_no_check(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        cube = VCube(initial, check=False)
        self.assertEqual(cube.state, initial)

    def test_initial_bad_size(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFB'

        with self.assertRaises(InvalidCubeStateError):
            VCube(initial)

    def test_initial_bad_char(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBT'

        with self.assertRaises(InvalidCubeStateError):
            VCube(initial)

    def test_initial_bad_face(self):
        initial = 'DUUDUUDUULLLRRRRRRFBBFFBFFBDDUDDUDDURRRLLLLLLFFBFBBFBF'

        with self.assertRaises(InvalidCubeStateError):
            VCube(initial)

    def test_is_solved(self):
        cube = VCube()

        self.assertTrue(
            cube.is_solved,
        )

        cube.rotate('R2 U2')
        self.assertFalse(
            cube.is_solved,
        )

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

        cube.display('z2')

        self.assertEqual(len(cube.history), 3)
        self.assertEqual(state, cube.state)

    def test_display_orientation_different(self):
        cube_1 = VCube()
        cube_2 = VCube()

        view_1 = cube_1.display()
        view_2 = cube_2.display('z2')

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


class VCubeRotateTestCase(unittest.TestCase):

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
        orientations = ['', 'x', 'y', 'z', 'x2', 'y2', 'z2']

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    self.cube.show(orientation=orientation)

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
