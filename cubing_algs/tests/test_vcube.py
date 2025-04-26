import unittest


INITIAL = ''
for face in ['U', 'R', 'F', 'D', 'L', 'B']:
    INITIAL += face * 9


class VCube:
    def __init__(self):
        self.state = INITIAL
        self.history = []



    def rotate(self, move: str):

        return self.state


class VCubeTestCase(unittest.TestCase):

    def test_rotate_u(self):
        cube = VCube()

        self.assertEqual(
            cube.rotate('U'),
            'UUUUUUUUUBBBRRRRRRRRRFFFFFFDDDDDDDDDFFFLLLLLLLLLBBBBBB',
        )

        self.assertEqual(
            cube.rotate("U'"),
            INITIAL,
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
            INITIAL,
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
            INITIAL,
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
            INITIAL,
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
            INITIAL,
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
            INITIAL,
        )

        self.assertEqual(
            cube.rotate('B2'),
            'DDDUUUUUURRLRRLRRLFFFFFFFFFDDDDDDUUURLLRLLRLLBBBBBBBBB',
        )
