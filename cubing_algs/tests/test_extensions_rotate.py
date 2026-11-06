"""
Tests for the unified rotation kernel.

The golden fixtures were generated from the three extensions it replaces
(rotate_2x2x2, rotate_3x3x3 and rotate_dynamic): every canonical move of
the cubes from 2x2x2 to 7x7x7, decomposed into face layers.
"""
import json
import unittest
from pathlib import Path

from cubing_algs.extensions.rotate import rotate_move
from cubing_algs.extensions.rotate import rotate_moves

FIXTURES = Path(__file__).parent / 'fixtures' / 'rotate_permutations.json'
GOLDEN = json.loads(FIXTURES.read_text())['sizes']

Permutation = list[int]


def unique_state(size: int, first: int = 0x100) -> str:
    """
    Build a state whose facelets are all distinct characters.

    Returns:
        A state of 6 * size * size characters, from first onwards.

    """
    return ''.join(chr(first + i) for i in range(6 * size * size))


def apply(state: str, permutation: Permutation) -> str:
    """
    Apply a gather permutation to a state.

    Returns:
        The state, its facelet i taken at permutation[i].

    """
    return ''.join(state[index] for index in permutation)


def expected_move(size: int, move: str, state: str) -> str:
    """
    Rotate a state by composing the golden layer permutations.

    Returns:
        The state after the move, as the replaced extensions computed it.

    """
    golden = GOLDEN[str(size)]
    face, first, last, turns = golden['moves'][move]
    for _ in range(turns):
        for layer in range(first, last + 1):
            state = apply(state, golden['layers'][f'{face}{layer}'])
    return state


class TestGoldenMoves(unittest.TestCase):
    """Every canonical move matches the extensions it replaces."""

    def test_rotate_move(self) -> None:
        """Each move, one at a time, on every size from 2 to 7."""
        for size_key, golden in GOLDEN.items():
            size = int(size_key)
            state = unique_state(size)
            for move in golden['moves']:
                with self.subTest(size=size, move=move):
                    self.assertEqual(
                        rotate_move(state, move),
                        expected_move(size, move, state),
                    )

    def test_rotate_moves(self) -> None:
        """Long sequences mixing every kind of move."""
        for size_key, golden in GOLDEN.items():
            size = int(size_key)
            moves = list(golden['moves'])
            for offset in range(7):
                sequence = moves[offset::7]
                state = unique_state(size)
                expected = state
                for move in sequence:
                    expected = expected_move(size, move, expected)
                with self.subTest(size=size, offset=offset):
                    self.assertEqual(
                        rotate_moves(state, ' '.join(sequence)),
                        expected,
                    )

    def test_explicit_size(self) -> None:
        """An explicit size matching the state is accepted."""
        for size in range(2, 8):
            state = unique_state(size)
            with self.subTest(size=size):
                self.assertEqual(
                    rotate_move(state, 'R', size),
                    expected_move(size, 'R', state),
                )
                self.assertEqual(
                    rotate_moves(state, "R U'", size=size),
                    expected_move(
                        size, "U'", expected_move(size, 'R', state),
                    ),
                )


class TestSeparators(unittest.TestCase):
    """Moves are separated by one or more spaces."""

    state = unique_state(3)

    def test_empty_sequence(self) -> None:
        """No move leaves the state unchanged."""
        for moves in ('', ' ', '   '):
            with self.subTest(moves=moves):
                self.assertEqual(rotate_moves(self.state, moves), self.state)

    def test_extra_spaces(self) -> None:
        """Leading, trailing and repeated spaces are ignored."""
        expected = rotate_moves(self.state, "R U R'")
        for moves in (" R U R'", "R U R' ", "R  U   R'", "  R U  R'  "):
            with self.subTest(moves=moves):
                self.assertEqual(rotate_moves(self.state, moves), expected)

    def test_single_move_with_space(self) -> None:
        """rotate_move takes exactly one move."""
        with self.assertRaises(ValueError):
            rotate_move(self.state, 'R U')


class TestStateEncodings(unittest.TestCase):
    """States of any string width rotate the same way."""

    def test_widths(self) -> None:
        """ASCII, latin-1, UCS-2 and UCS-4 facelets."""
        reference = unique_state(4, 0x21)
        expected = rotate_moves(reference, "Rw U2 3Fw' x")
        for first in (0x21, 0xA0, 0x100, 0x1F300):
            state = unique_state(4, first)
            with self.subTest(first=hex(first)):
                result = rotate_moves(state, "Rw U2 3Fw' x")
                self.assertEqual(
                    [ord(c) - first for c in result],
                    [ord(c) - 0x21 for c in expected],
                )

    def test_latin1_single_character(self) -> None:
        """A state mixing ASCII and one latin-1 character stays canonical."""
        state = 'é' + 'U' * 53
        result = rotate_move(state, 'R')
        self.assertEqual(sorted(result), sorted(state))
        self.assertEqual(rotate_moves(result, "R'"), state)


class TestStateValidation(unittest.TestCase):
    """The state length is checked before any memory access."""

    def test_length_not_a_cube(self) -> None:
        """A length that is not 6 * size * size is rejected."""
        for state in ('', 'UUU', 'U' * 53, 'U' * 55, 'U' * 7):
            with self.subTest(length=len(state)):
                with self.assertRaises(ValueError):
                    rotate_move(state, 'R')
                with self.assertRaises(ValueError):
                    rotate_moves(state, 'R')

    def test_size_out_of_range(self) -> None:
        """Sizes 1 and above 20 are not supported."""
        for size in (1, 21):
            with self.subTest(size=size), self.assertRaises(ValueError):
                rotate_move('U' * (6 * size * size), 'R')

    def test_size_mismatch(self) -> None:
        """An explicit size must match the state length."""
        with self.assertRaises(ValueError):
            rotate_move(unique_state(3), 'R', 4)
        with self.assertRaises(ValueError):
            rotate_moves(unique_state(3), 'R', size=2)

    def test_wrong_types(self) -> None:
        """State and moves must be strings."""
        with self.assertRaises(TypeError):
            rotate_move(b'U' * 54, 'R')  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            rotate_moves('U' * 54, None)  # type: ignore[arg-type]


class TestRejectedMoves(unittest.TestCase):
    """Moves outside the grammar raise instead of being guessed."""

    rejected = (
        '', "'", '2', 'w', 'Q', 'm', 'e', 's',
        'R3', 'Rx', "R''", 'R22', "R'2", "R2''",
        'fw', 'xw', 'Mw', '2M', '2x', '2-3x',
        '0R', '0Rw', '0-2Rw', '3-2Rw', '2-3R', '-2Rw', '2-Rw', '2-',
    )

    def test_rejected_on_every_size(self) -> None:
        """Malformed moves, on even and odd cubes."""
        for size in (3, 4):
            state = unique_state(size)
            for move in self.rejected:
                with self.subTest(size=size, move=move):
                    with self.assertRaises(ValueError):
                        rotate_move(state, move)
                    if move:
                        with self.assertRaises(ValueError):
                            rotate_moves(state, f'R {move} U')

    def test_layer_exceeds_size(self) -> None:
        """A layer beyond the cube is rejected."""
        for move in ('4R', '4Rw', '2-4Rw', '4r', '4-5Rw'):
            with self.subTest(move=move):
                with self.assertRaises(ValueError) as context:
                    rotate_move(unique_state(3), move)
                self.assertIn('exceeds cube size 3', str(context.exception))

    def test_slices_on_even_cubes(self) -> None:
        """M, E and S need a middle layer."""
        for move in ('M', "E'", 'S2'):
            with self.subTest(move=move):
                with self.assertRaises(ValueError) as context:
                    rotate_move(unique_state(4), move)
                self.assertIn(
                    f'{move[0]} moves are only allowed on odd-sized cubes',
                    str(context.exception),
                )
                self.assertIn('4x4x4', str(context.exception))

    def test_failure_leaves_no_partial_state(self) -> None:
        """An invalid move in a sequence raises, nothing is returned."""
        with self.assertRaises(ValueError) as context:
            rotate_moves(unique_state(3), 'R U Q F')
        self.assertIn('Q', str(context.exception))


class TestHalfTurnPrime(unittest.TestCase):
    """`2'` is a half turn, the same permutation as `2`."""

    def test_every_face(self) -> None:
        """Faces, wide moves, rotations and slices."""
        state = unique_state(5)
        for base in ('R', 'Uw', '3Fw', '2-3l', 'x', 'M', 'E', 'S', '2D'):
            with self.subTest(base=base):
                self.assertEqual(
                    rotate_move(state, f"{base}2'"),
                    rotate_move(state, f'{base}2'),
                )


class TestLargeCubes(unittest.TestCase):
    """Layer numbers of more than one digit."""

    size = 12
    state = unique_state(12)

    def layers(self, first: int, last: int, face: str = 'R') -> str:
        """
        Turn the layers one by one.

        Returns:
            The state after each layer from first to last turned once.

        """
        return rotate_moves(
            self.state,
            ' '.join(f'{n}{face}' for n in range(first, last + 1)),
        )

    def test_wide_prefix(self) -> None:
        """10Rw turns the ten outer layers."""
        self.assertEqual(rotate_move(self.state, '10Rw'), self.layers(1, 10))
        self.assertEqual(rotate_move(self.state, '10r'), self.layers(1, 10))

    def test_range(self) -> None:
        """2-11Rw turns the inner layers."""
        self.assertEqual(
            rotate_move(self.state, '2-11Rw'), self.layers(2, 11),
        )

    def test_single_layer(self) -> None:
        """The last layer from R is the L layer turned backwards."""
        self.assertEqual(
            rotate_move(self.state, '12R'), rotate_move(self.state, "L'"),
        )
        self.assertEqual(
            rotate_move(self.state, '12Rw'), rotate_move(self.state, 'x'),
        )

    def test_exceeds(self) -> None:
        """13R does not exist on a 12x12x12."""
        with self.assertRaises(ValueError):
            rotate_move(self.state, '13R')
        with self.assertRaises(ValueError):
            rotate_move(self.state, '99999999999999999999Rw')


class TestPermutationCache(unittest.TestCase):
    """Results stay right once the permutation cache is full."""

    def test_every_range_of_a_20x20(self) -> None:
        """All the wide ranges of the largest cube, twice."""
        size = 20
        state = unique_state(size)
        for face in 'URFDLB':
            for first in range(1, size + 1):
                for last in range(first, size + 1):
                    move = f'{first}-{last}{face}w'
                    expected = rotate_moves(
                        state,
                        ' '.join(
                            f'{n}{face}' for n in range(first, last + 1)
                        ),
                    )
                    with self.subTest(move=move):
                        self.assertEqual(rotate_move(state, move), expected)
                        self.assertEqual(rotate_move(state, move), expected)
