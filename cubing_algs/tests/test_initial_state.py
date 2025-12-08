"""Tests for the initial_state module."""

import unittest

from cubing_algs.constants import FACE_ORDER
from cubing_algs.initial_state import get_initial_state


class GetInitialStateTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for the get_initial_state function."""

    def test_default_size_returns_54_characters(self) -> None:
        """Test default size (3x3x3) returns 54 characters."""
        state = get_initial_state()
        self.assertEqual(len(state), 54)

    def test_default_size_matches_docstring_example(self) -> None:
        """Test default size matches docstring example for 3x3x3."""
        expected = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        self.assertEqual(get_initial_state(), expected)
        self.assertEqual(get_initial_state(3), expected)

    def test_size_2_returns_24_characters(self) -> None:
        """Test size 2 (2x2x2) returns 24 characters."""
        state = get_initial_state(2)
        self.assertEqual(len(state), 24)

    def test_size_2_matches_docstring_example(self) -> None:
        """Test size 2 matches docstring example for 2x2x2."""
        expected = 'UUUURRRRFFFFDDDDLLLLBBBB'
        self.assertEqual(get_initial_state(2), expected)

    def test_size_4_returns_96_characters(self) -> None:
        """Test size 4 (4x4x4) returns 96 characters."""
        state = get_initial_state(4)
        self.assertEqual(len(state), 96)

    def test_size_4_has_correct_format(self) -> None:
        """Test size 4 has correct format with 16 facelets per face."""
        expected = (
            'U' * 16 + 'R' * 16 + 'F' * 16 +
            'D' * 16 + 'L' * 16 + 'B' * 16
        )
        self.assertEqual(get_initial_state(4), expected)

    def test_size_5_returns_150_characters(self) -> None:
        """Test size 5 (5x5x5) returns 150 characters."""
        state = get_initial_state(5)
        self.assertEqual(len(state), 150)

    def test_size_5_has_correct_format(self) -> None:
        """Test size 5 has correct format with 25 facelets per face."""
        expected = (
            'U' * 25 + 'R' * 25 + 'F' * 25 +
            'D' * 25 + 'L' * 25 + 'B' * 25
        )
        self.assertEqual(get_initial_state(5), expected)

    def test_size_6_returns_216_characters(self) -> None:
        """Test size 6 (6x6x6) returns 216 characters."""
        state = get_initial_state(6)
        self.assertEqual(len(state), 216)

    def test_size_7_returns_294_characters(self) -> None:
        """Test size 7 (7x7x7) returns 294 characters."""
        state = get_initial_state(7)
        self.assertEqual(len(state), 294)

    def test_size_1_returns_6_characters(self) -> None:
        """Test edge case: size 1 (1x1x1) returns 6 characters."""
        state = get_initial_state(1)
        self.assertEqual(len(state), 6)

    def test_size_1_has_correct_format(self) -> None:
        """Test edge case: size 1 has one facelet per face."""
        expected = 'URFDLB'
        self.assertEqual(get_initial_state(1), expected)

    def test_length_formula_6_times_size_squared(self) -> None:
        """Test that length follows formula: 6 * size * size."""
        for size in range(1, 10):
            state = get_initial_state(size)
            expected_length = 6 * size * size
            self.assertEqual(
                len(state),
                expected_length,
                f'Size {size} should have {expected_length} characters',
            )

    def test_face_order_matches_constant(self) -> None:
        """Test that faces appear in the order defined by FACE_ORDER."""
        state = get_initial_state(3)
        facelets_per_face = 9

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(
                face_section,
                face * facelets_per_face,
                (
                    f'Face {face} at position {i} '
                    f'should be {facelets_per_face} {face}s'
                ),
            )

    def test_each_face_has_correct_number_of_facelets_size_2(self) -> None:
        """Test each face has exactly size*size facelets for 2x2x2."""
        state = get_initial_state(2)
        facelets_per_face = 4

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_each_face_has_correct_number_of_facelets_size_4(self) -> None:
        """Test each face has exactly size*size facelets for 4x4x4."""
        state = get_initial_state(4)
        facelets_per_face = 16

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_contains_only_valid_face_characters(self) -> None:
        """Test state contains only valid face characters from FACE_ORDER."""
        state = get_initial_state(3)
        valid_chars = set(FACE_ORDER)

        for char in state:
            self.assertIn(
                char,
                valid_chars,
                f'Character {char} is not a valid face',
            )

    def test_all_six_faces_present(self) -> None:
        """Test that all six faces are present in the state."""
        state = get_initial_state(3)
        unique_faces = set(state)

        self.assertEqual(len(unique_faces), 6)
        self.assertEqual(unique_faces, set(FACE_ORDER))

    def test_face_count_is_equal_for_all_faces(self) -> None:
        """Test each face appears exactly size*size times."""
        size = 3
        state = get_initial_state(size)
        expected_count = size * size

        for face in FACE_ORDER:
            count = state.count(face)
            self.assertEqual(
                count,
                expected_count,
                f'Face {face} should appear {expected_count} times',
            )

    def test_size_10_returns_600_characters(self) -> None:
        """Test larger cube: size 10 (10x10x10) returns 600 characters."""
        state = get_initial_state(10)
        self.assertEqual(len(state), 600)

    def test_size_10_has_correct_format(self) -> None:
        """Test larger cube: size 10 has 100 facelets per face."""
        state = get_initial_state(10)
        facelets_per_face = 100

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_state_is_string_type(self) -> None:
        """Test that returned value is a string."""
        state = get_initial_state(3)
        self.assertIsInstance(state, str)

    def test_different_sizes_produce_different_lengths(self) -> None:
        """Test that different sizes produce states with different lengths."""
        sizes = [2, 3, 4, 5]
        states = [get_initial_state(size) for size in sizes]
        lengths = [len(state) for state in states]

        # All lengths should be unique
        self.assertEqual(len(lengths), len(set(lengths)))

    def test_u_face_always_first(self) -> None:
        """Test that U face is always first in the state string."""
        for size in [1, 2, 3, 4, 5]:
            state = get_initial_state(size)
            facelets_per_face = size * size
            self.assertTrue(
                state[:facelets_per_face] == 'U' * facelets_per_face,
            )

    def test_b_face_always_last(self) -> None:
        """Test that B face is always last in the state string."""
        for size in [1, 2, 3, 4, 5]:
            state = get_initial_state(size)
            facelets_per_face = size * size
            self.assertTrue(
                state[-facelets_per_face:] == 'B' * facelets_per_face,
            )

    def test_consistent_results_for_same_size(self) -> None:
        """Test that calling with same size produces identical results."""
        for size in [2, 3, 4, 5]:
            state1 = get_initial_state(size)
            state2 = get_initial_state(size)
            self.assertEqual(state1, state2)
