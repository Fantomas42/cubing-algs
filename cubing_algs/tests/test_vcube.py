import unittest

from cubing_algs.move import InvalidMoveError
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import INITIAL
from cubing_algs.vcube import InvalidCubeStateError
from cubing_algs.vcube import VCube


class VCubeTestCase(unittest.TestCase):
    maxDiff = None

    def test_state(self):
        cube = VCube()

        self.assertEqual(
            cube.state,
            INITIAL,
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
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        cube = VCube.from_cubies(cp, co, ep, eo)
        self.assertEqual(cube.state, facelets)

        cube = VCube()
        cube.rotate('F R')

        self.assertEqual(cube.state, facelets)

    def test_to_cubies(self):
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            VCube(facelets).to_cubies,
            (
                cp, co,
                ep, eo,
            ),
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
    c_version = False

    def test_rotate_u(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('U', self.c_version),
            'UUUUUUUUUBBBRRRRRRRRRFFFFFFDDDDDDDDDFFFLLLLLLLLLBBBBBB',
        )

        self.assertEqual(
            cube.rotate("U'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('U2', self.c_version),
            'UUUUUUUUULLLRRRRRRBBBFFFFFFDDDDDDDDDRRRLLLLLLFFFBBBBBB',
        )

    def test_rotate_r(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('R', self.c_version),
            'UUFUUFUUFRRRRRRRRRFFDFFDFFDDDBDDBDDBLLLLLLLLLUBBUBBUBB',
        )

        self.assertEqual(
            cube.rotate("R'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('R2', self.c_version),
            'UUDUUDUUDRRRRRRRRRFFBFFBFFBDDUDDUDDULLLLLLLLLFBBFBBFBB',
        )

    def test_rotate_f(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('F', self.c_version),
            'UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("F'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('F2', self.c_version),
            'UUUUUUDDDLRRLRRLRRFFFFFFFFFUUUDDDDDDLLRLLRLLRBBBBBBBBB',
        )

    def test_rotate_d(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('D', self.c_version),
            'UUUUUUUUURRRRRRFFFFFFFFFLLLDDDDDDDDDLLLLLLBBBBBBBBBRRR',
        )

        self.assertEqual(
            cube.rotate("D'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('D2', self.c_version),
            'UUUUUUUUURRRRRRLLLFFFFFFBBBDDDDDDDDDLLLLLLRRRBBBBBBFFF',
        )

    def test_rotate_l(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('L', self.c_version),
            'BUUBUUBUURRRRRRRRRUFFUFFUFFFDDFDDFDDLLLLLLLLLBBDBBDBBD',
        )

        self.assertEqual(
            cube.rotate("L'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('L2', self.c_version),
            'DUUDUUDUURRRRRRRRRBFFBFFBFFUDDUDDUDDLLLLLLLLLBBFBBFBBF',
        )

    def test_rotate_b(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('B', self.c_version),
            'RRRUUUUUURRDRRDRRDFFFFFFFFFDDDDDDLLLULLULLULLBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("B'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('B2', self.c_version),
            'DDDUUUUUURRLRRLRRLFFFFFFFFFDDDDDDUUURLLRLLRLLBBBBBBBBB',
        )

    def test_rotate_m(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('M', self.c_version),
            'UBUUBUUBURRRRRRRRRFUFFUFFUFDFDDFDDFDLLLLLLLLLBDBBDBBDB',
        )

        self.assertEqual(
            cube.rotate("M'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('M2', self.c_version),
            'UDUUDUUDURRRRRRRRRFBFFBFFBFDUDDUDDUDLLLLLLLLLBFBBFBBFB',
        )

    def test_rotate_s(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('S', self.c_version),
            'UUULLLUUURURRURRURFFFFFFFFFDDDRRRDDDLDLLDLLDLBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("S'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('S2', self.c_version),
            'UUUDDDUUURLRRLRRLRFFFFFFFFFDDDUUUDDDLRLLRLLRLBBBBBBBBB',
        )

    def test_rotate_e(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('E', self.c_version),
            'UUUUUUUUURRRFFFRRRFFFLLLFFFDDDDDDDDDLLLBBBLLLBBBRRRBBB',
        )

        self.assertEqual(
            cube.rotate("E'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('E2', self.c_version),
            'UUUUUUUUURRRLLLRRRFFFBBBFFFDDDDDDDDDLLLRRRLLLBBBFFFBBB',
        )

    def test_rotate_x(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('x', self.c_version),
            'FFFFFFFFFRRRRRRRRRDDDDDDDDDBBBBBBBBBLLLLLLLLLUUUUUUUUU',
        )

        self.assertEqual(
            cube.rotate("x'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('x2', self.c_version),
            'DDDDDDDDDRRRRRRRRRBBBBBBBBBUUUUUUUUULLLLLLLLLFFFFFFFFF',
        )

    def test_rotate_y(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('y', self.c_version),
            'UUUUUUUUUBBBBBBBBBRRRRRRRRRDDDDDDDDDFFFFFFFFFLLLLLLLLL',
        )

        self.assertEqual(
            cube.rotate("y'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('y2', self.c_version),
            'UUUUUUUUULLLLLLLLLBBBBBBBBBDDDDDDDDDRRRRRRRRRFFFFFFFFF',
        )

    def test_rotate_z(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('z', self.c_version),
            'LLLLLLLLLUUUUUUUUUFFFFFFFFFRRRRRRRRRDDDDDDDDDBBBBBBBBB',
        )

        self.assertEqual(
            cube.rotate("z'", self.c_version),
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('z2', self.c_version),
            'DDDDDDDDDLLLLLLLLLFFFFFFFFFUUUUUUUUURRRRRRRRRBBBBBBBBB',
        )

    def test_rotate_invalid_modifier(self):
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('z3', self.c_version)

    def test_rotate_invalid_move(self):
        cube = VCube()

        with self.assertRaises(InvalidMoveError):
            cube.rotate('T2', self.c_version)

    def test_real_case(self):
        cube = VCube()
        scramble = "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'"

        self.assertEqual(
            cube.rotate(scramble, self.c_version),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )

    def test_real_case_2(self):
        cube = VCube()
        scramble = "F R' F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2"

        self.assertEqual(
            cube.rotate(scramble, self.c_version),
            'LDBRUUBBDFLUFRLBDDLURLFDFRLLFUFDRFDBFUDBLBRUURBDFBRRLU',
        )

    def test_real_case_3(self):
        cube = VCube()
        scramble = "F R F' U' D2 B' L F U' F L' U F2 U' F2 B2 L2 D2 B2 D' L2 B'"

        self.assertEqual(
            cube.rotate(scramble, self.c_version),
            'UFFRUUBBDFLLFRDBUFLURLFDBRLDFUBDRLLRBDDDLBFRRDURBBLUFU',
        )

    def test_real_case_with_algorithm(self):
        cube = VCube()
        scramble = parse_moves(
            "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'",
        )

        self.assertEqual(
            cube.rotate(scramble, self.c_version),
            'FBFUUDUUDBFUFRLRRRLRLLFRRDBFBUBDBFUDRFBRLFLLULUDDBDBLD',
        )


class CVCubeRotateTestCase(VCubeRotateTestCase):
    c_version = True


class RegressionVCubeTestCase(unittest.TestCase):
    initial = 'UDBRUUDBDFLUFRLBDRLUDRFDBRLLFULDRFDURBFULUBBDRBFFBFRLL'

    def check_rotate(self, move):
        p_cube = VCube(self.initial)
        c_cube = VCube(self.initial)

        with self.subTest('Clockwise', move=move):
            self.assertEqual(
                p_cube.rotate(move, allow_fast=False),
                c_cube.rotate(move, allow_fast=True),
            )

        p_cube = VCube(self.initial)
        c_cube = VCube(self.initial)
        with self.subTest('Anti-Clockwise', move=move):
            self.assertEqual(
                p_cube.rotate(f"{ move }'", allow_fast=False),
                c_cube.rotate(f"{ move }'", allow_fast=True),
            )

        p_cube = VCube(self.initial)
        c_cube = VCube(self.initial)
        with self.subTest('Double', move=move):
            self.assertEqual(
                p_cube.rotate(f'{ move }2', allow_fast=False),
                c_cube.rotate(f'{ move }2', allow_fast=True),
            )

    def test_rotate_u(self):
        self.check_rotate('U')

    def test_rotate_r(self):
        self.check_rotate('R')

    def test_rotate_f(self):
        self.check_rotate('F')

    def test_rotate_d(self):
        self.check_rotate('D')

    def test_rotate_l(self):
        self.check_rotate('L')

    def test_rotate_b(self):
        self.check_rotate('B')

    def test_rotate_m(self):
        self.check_rotate('M')

    def test_rotate_s(self):
        self.check_rotate('S')

    def test_rotate_e(self):
        self.check_rotate('E')

    def test_rotate_x(self):
        self.check_rotate('x')

    def test_rotate_y(self):
        self.check_rotate('y')

    def test_rotate_z(self):
        self.check_rotate('z')
