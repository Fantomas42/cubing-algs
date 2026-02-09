"""Tests for the solved_state module."""
import unittest

from cubing_algs.constants import CORNER_NUMBER
from cubing_algs.constants import EDGE_NUMBER
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_SO
from cubing_algs.solved_state import get_solved_cubies
from cubing_algs.solved_state import get_solved_facelets


class GetInitialStateTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for the get_solved_facelets function."""

    def test_default_size_returns_54_characters(self) -> None:
        """Test default size (3x3x3) returns 54 characters."""
        state = get_solved_facelets()
        self.assertEqual(len(state), 54)

    def test_default_size_matches_docstring_example(self) -> None:
        """Test default size matches docstring example for 3x3x3."""
        expected = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        self.assertEqual(get_solved_facelets(), expected)
        self.assertEqual(get_solved_facelets(3), expected)

    def test_size_2_returns_24_characters(self) -> None:
        """Test size 2 (2x2x2) returns 24 characters."""
        state = get_solved_facelets(2)
        self.assertEqual(len(state), 24)

    def test_size_2_matches_docstring_example(self) -> None:
        """Test size 2 matches docstring example for 2x2x2."""
        expected = 'UUUURRRRFFFFDDDDLLLLBBBB'
        self.assertEqual(get_solved_facelets(2), expected)

    def test_size_4_returns_96_characters(self) -> None:
        """Test size 4 (4x4x4) returns 96 characters."""
        state = get_solved_facelets(4)
        self.assertEqual(len(state), 96)

    def test_size_4_has_correct_format(self) -> None:
        """Test size 4 has correct format with 16 facelets per face."""
        expected = (
            'U' * 16 + 'R' * 16 + 'F' * 16 +
            'D' * 16 + 'L' * 16 + 'B' * 16
        )
        self.assertEqual(get_solved_facelets(4), expected)

    def test_size_5_returns_150_characters(self) -> None:
        """Test size 5 (5x5x5) returns 150 characters."""
        state = get_solved_facelets(5)
        self.assertEqual(len(state), 150)

    def test_size_5_has_correct_format(self) -> None:
        """Test size 5 has correct format with 25 facelets per face."""
        expected = (
            'U' * 25 + 'R' * 25 + 'F' * 25 +
            'D' * 25 + 'L' * 25 + 'B' * 25
        )
        self.assertEqual(get_solved_facelets(5), expected)

    def test_size_6_returns_216_characters(self) -> None:
        """Test size 6 (6x6x6) returns 216 characters."""
        state = get_solved_facelets(6)
        self.assertEqual(len(state), 216)

    def test_size_7_returns_294_characters(self) -> None:
        """Test size 7 (7x7x7) returns 294 characters."""
        state = get_solved_facelets(7)
        self.assertEqual(len(state), 294)

    def test_size_1_returns_6_characters(self) -> None:
        """Test edge case: size 1 (1x1x1) returns 6 characters."""
        state = get_solved_facelets(1)
        self.assertEqual(len(state), 6)

    def test_size_1_has_correct_format(self) -> None:
        """Test edge case: size 1 has one facelet per face."""
        expected = 'URFDLB'
        self.assertEqual(get_solved_facelets(1), expected)

    def test_length_formula_6_times_size_squared(self) -> None:
        """Test that length follows formula: 6 * size * size."""
        for size in range(1, 10):
            state = get_solved_facelets(size)
            expected_length = 6 * size * size
            self.assertEqual(
                len(state),
                expected_length,
                f'Size {size} should have {expected_length} characters',
            )

    def test_face_order_matches_constant(self) -> None:
        """Test that faces appear in the order defined by FACE_ORDER."""
        state = get_solved_facelets(3)
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
        state = get_solved_facelets(2)
        facelets_per_face = 4

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_each_face_has_correct_number_of_facelets_size_4(self) -> None:
        """Test each face has exactly size*size facelets for 4x4x4."""
        state = get_solved_facelets(4)
        facelets_per_face = 16

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_contains_only_valid_face_characters(self) -> None:
        """Test state contains only valid face characters from FACE_ORDER."""
        state = get_solved_facelets(3)
        valid_chars = set(FACE_ORDER)

        for char in state:
            self.assertIn(
                char,
                valid_chars,
                f'Character {char} is not a valid face',
            )

    def test_all_six_faces_present(self) -> None:
        """Test that all six faces are present in the state."""
        state = get_solved_facelets(3)
        unique_faces = set(state)

        self.assertEqual(len(unique_faces), 6)
        self.assertEqual(unique_faces, set(FACE_ORDER))

    def test_face_count_is_equal_for_all_faces(self) -> None:
        """Test each face appears exactly size*size times."""
        size = 3
        state = get_solved_facelets(size)
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
        state = get_solved_facelets(10)
        self.assertEqual(len(state), 600)

    def test_size_10_has_correct_format(self) -> None:
        """Test larger cube: size 10 has 100 facelets per face."""
        state = get_solved_facelets(10)
        facelets_per_face = 100

        for i, face in enumerate(FACE_ORDER):
            start = i * facelets_per_face
            end = start + facelets_per_face
            face_section = state[start:end]

            self.assertEqual(len(face_section), facelets_per_face)
            self.assertTrue(all(c == face for c in face_section))

    def test_state_is_string_type(self) -> None:
        """Test that returned value is a string."""
        state = get_solved_facelets(3)
        self.assertIsInstance(state, str)

    def test_different_sizes_produce_different_lengths(self) -> None:
        """Test that different sizes produce states with different lengths."""
        sizes = [2, 3, 4, 5]
        states = [get_solved_facelets(size) for size in sizes]
        lengths = [len(state) for state in states]

        # All lengths should be unique
        self.assertEqual(len(lengths), len(set(lengths)))

    def test_u_face_always_first(self) -> None:
        """Test that U face is always first in the state string."""
        for size in [1, 2, 3, 4, 5]:
            state = get_solved_facelets(size)
            facelets_per_face = size * size
            self.assertTrue(
                state[:facelets_per_face] == 'U' * facelets_per_face,
            )

    def test_b_face_always_last(self) -> None:
        """Test that B face is always last in the state string."""
        for size in [1, 2, 3, 4, 5]:
            state = get_solved_facelets(size)
            facelets_per_face = size * size
            self.assertTrue(
                state[-facelets_per_face:] == 'B' * facelets_per_face,
            )

    def test_consistent_results_for_same_size(self) -> None:
        """Test that calling with same size produces identical results."""
        for size in [2, 3, 4, 5]:
            state1 = get_solved_facelets(size)
            state2 = get_solved_facelets(size)
            self.assertEqual(state1, state2)


class GetSolvedCubiesTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for the get_solved_cubies function."""

    def test_default_size_returns_tuple(self) -> None:
        """Test default size (3x3x3) returns a tuple."""
        result = get_solved_cubies()
        self.assertIsInstance(result, tuple)

    def test_default_size_returns_5_elements(self) -> None:
        """Test default size (3x3x3) returns tuple with 5 elements."""
        result = get_solved_cubies()
        self.assertEqual(len(result), 5)

    def test_default_size_corner_permutation(self) -> None:
        """Test default size returns correct corner permutation."""
        cp, _, _, _, _ = get_solved_cubies()
        self.assertEqual(cp, SOLVED_CP)
        self.assertEqual(cp, [0, 1, 2, 3, 4, 5, 6, 7])

    def test_default_size_corner_orientation(self) -> None:
        """Test default size returns correct corner orientation."""
        _, co, _, _, _ = get_solved_cubies()
        self.assertEqual(co, SOLVED_CO)
        self.assertEqual(len(co), CORNER_NUMBER)

    def test_default_size_edge_permutation(self) -> None:
        """Test default size returns correct edge permutation."""
        _, _, ep, _, _ = get_solved_cubies()
        expected_edges = EDGE_NUMBER * (3 - 2)
        self.assertEqual(ep, list(range(expected_edges)))
        self.assertEqual(ep, list(range(12)))

    def test_default_size_edge_orientation(self) -> None:
        """Test default size returns correct edge orientation."""
        _, _, _, eo, _ = get_solved_cubies()
        expected_edges = EDGE_NUMBER * (3 - 2)
        self.assertEqual(eo, [0] * expected_edges)
        self.assertEqual(len(eo), 12)

    def test_default_size_spatial_orientation(self) -> None:
        """Test default size returns correct spatial orientation."""
        _, _, _, _, so = get_solved_cubies()
        self.assertEqual(so, SOLVED_SO)
        self.assertEqual(so, [0, 1, 2, 3, 4, 5])

    def test_size_3_returns_tuple_with_5_elements(self) -> None:
        """Test explicit size 3 returns tuple with 5 elements."""
        result = get_solved_cubies(3)
        self.assertEqual(len(result), 5)

    def test_size_3_matches_default(self) -> None:
        """Test explicit size 3 matches default behavior."""
        result_default = get_solved_cubies()
        result_3 = get_solved_cubies(3)
        self.assertEqual(result_default, result_3)

    def test_size_1(self) -> None:
        """Test size 1 (1x1x1) has correct representation."""
        cp, co, ep, eo, so = get_solved_cubies(1)
        self.assertEqual(cp, [])
        self.assertEqual(co, [])
        self.assertEqual(ep, [])
        self.assertEqual(eo, [])
        self.assertEqual(so, SOLVED_SO)

    def test_size_2_edge_calculation(self) -> None:
        """Test size 2 (2x2x2) has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(2)
        expected_edges = EDGE_NUMBER * (2 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 0)
        self.assertEqual(len(eo), 0)

    def test_size_2_has_empty_edge_lists(self) -> None:
        """Test size 2 (2x2x2) has empty edge permutation and orientation."""
        _, _, ep, eo, _ = get_solved_cubies(2)
        self.assertEqual(ep, [])
        self.assertEqual(eo, [])

    def test_size_2_corner_permutation_unchanged(self) -> None:
        """Test size 2 corner permutation is same as default."""
        cp_2, _, _, _, _ = get_solved_cubies(2)
        self.assertEqual(cp_2, SOLVED_CP)

    def test_size_2_spatial_orientation_unchanged(self) -> None:
        """Test size 2 spatial orientation is same as default."""
        _, _, _, _, so_2 = get_solved_cubies(2)
        self.assertEqual(so_2, SOLVED_SO)

    def test_size_4_edge_calculation(self) -> None:
        """Test size 4 (4x4x4) has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(4)
        expected_edges = EDGE_NUMBER * (4 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 24)
        self.assertEqual(len(eo), 24)

    def test_size_4_edge_permutation_range(self) -> None:
        """Test size 4 edge permutation is sequential from 0."""
        _, _, ep, _, _ = get_solved_cubies(4)
        self.assertEqual(ep, list(range(24)))

    def test_size_4_edge_orientation_all_zeros(self) -> None:
        """Test size 4 edge orientation is all zeros."""
        _, _, _, eo, _ = get_solved_cubies(4)
        self.assertEqual(eo, [0] * 24)
        self.assertTrue(all(o == 0 for o in eo))

    def test_size_5_edge_calculation(self) -> None:
        """Test size 5 (5x5x5) has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(5)
        expected_edges = EDGE_NUMBER * (5 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 36)
        self.assertEqual(len(eo), 36)

    def test_size_6_edge_calculation(self) -> None:
        """Test size 6 (6x6x6) has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(6)
        expected_edges = EDGE_NUMBER * (6 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 48)

    def test_size_7_edge_calculation(self) -> None:
        """Test size 7 (7x7x7) has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(7)
        expected_edges = EDGE_NUMBER * (7 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 60)

    def test_size_1_edge_calculation(self) -> None:
        """Test edge case: size 1 (1x1x1) has empty edge lists."""
        _, _, ep, eo, _ = get_solved_cubies(1)
        # Even though formula gives -12, list(range(-12)) returns []
        self.assertEqual(ep, [])
        self.assertEqual(eo, [])
        self.assertEqual(len(ep), 0)
        self.assertEqual(len(eo), 0)

    def test_size_1_edge_lists_are_empty(self) -> None:
        """Test edge case: size 1 produces empty edge lists."""
        _, _, ep, eo, _ = get_solved_cubies(1)
        # list(range(-12)) returns [], and [0] * -12 returns []
        self.assertEqual(ep, list(range(-12)))
        self.assertEqual(eo, [0] * -12)
        self.assertEqual(ep, [])
        self.assertEqual(eo, [])

    def test_edge_formula_calculation(self) -> None:
        """Test edge calculation formula: edges = EDGE_NUMBER * (size - 2)."""
        for size in [2, 3, 4, 5, 6, 7]:
            _, _, ep, _, _ = get_solved_cubies(size)
            expected_edges = EDGE_NUMBER * (size - 2)
            self.assertEqual(
                len(ep),
                expected_edges,
                f'Size {size} should have {expected_edges} edges',
            )

    def test_edge_permutation_is_sequential_from_zero(self) -> None:
        """Test edge permutation is always sequential starting from 0."""
        for size in [2, 3, 4, 5, 6]:
            _, _, ep, _, _ = get_solved_cubies(size)
            expected_edges = EDGE_NUMBER * (size - 2)
            if expected_edges > 0:
                self.assertEqual(ep, list(range(expected_edges)))
                self.assertEqual(ep[0], 0)
                self.assertEqual(ep[-1], expected_edges - 1)

    def test_edge_orientation_length_matches_permutation_length(self) -> None:
        """Test edge orientation has same length as edge permutation."""
        for size in [2, 3, 4, 5, 6, 7]:
            _, _, ep, eo, _ = get_solved_cubies(size)
            self.assertEqual(
                len(eo),
                len(ep),
                f'Size {size}: eo length should match ep length',
            )

    def test_edge_orientation_all_zeros_for_all_sizes(self) -> None:
        """Test edge orientation is all zeros for all valid sizes."""
        for size in [2, 3, 4, 5, 6]:
            _, _, _, eo, _ = get_solved_cubies(size)
            if len(eo) > 0:
                self.assertTrue(
                    all(o == 0 for o in eo),
                    f'Size {size}: all edge orientations should be 0',
                )

    def test_corner_permutation_constant_across_sizes(self) -> None:
        """Test corner permutation is constant regardless of size."""
        for size in [2, 3, 4, 5, 6]:
            cp, _, _, _, _ = get_solved_cubies(size)
            self.assertEqual(cp, SOLVED_CP)

    def test_corner_permutation_length_is_8(self) -> None:
        """Test corner permutation length is always 8."""
        for size in [2, 3, 4, 5, 6]:
            cp, _, _, _, _ = get_solved_cubies(size)
            self.assertEqual(len(cp), CORNER_NUMBER)
            self.assertEqual(len(cp), 8)

    def test_corner_orientation_length_is_8(self) -> None:
        """Test corner orientation length is always 8."""
        for size in [2, 3, 4, 5, 6]:
            _, co, _, _, _ = get_solved_cubies(size)
            self.assertEqual(len(co), CORNER_NUMBER)
            self.assertEqual(len(co), 8)

    def test_spatial_orientation_constant_across_sizes(self) -> None:
        """Test spatial orientation is constant regardless of size."""
        for size in [2, 3, 4, 5, 6]:
            _, _, _, _, so = get_solved_cubies(size)
            self.assertEqual(so, SOLVED_SO)

    def test_spatial_orientation_length_is_6(self) -> None:
        """Test spatial orientation length is always 6."""
        for size in [2, 3, 4, 5, 6]:
            _, _, _, _, so = get_solved_cubies(size)
            self.assertEqual(len(so), FACE_NUMBER)
            self.assertEqual(len(so), 6)

    def test_spatial_orientation_is_sequential_from_zero(self) -> None:
        """Test spatial orientation is [0, 1, 2, 3, 4, 5]."""
        _, _, _, _, so = get_solved_cubies()
        self.assertEqual(so, [0, 1, 2, 3, 4, 5])

    def test_return_type_structure(self) -> None:
        """Test returned tuple has correct structure (5 lists)."""
        result = get_solved_cubies()
        self.assertEqual(len(result), 5)
        for i, element in enumerate(result):
            self.assertIsInstance(
                element,
                list,
                f'Element {i} should be a list',
            )

    def test_corner_permutation_is_list_not_tuple(self) -> None:
        """Test corner permutation is returned as a list."""
        cp, _, _, _, _ = get_solved_cubies()
        self.assertIsInstance(cp, list)

    def test_corner_orientation_is_list_not_tuple(self) -> None:
        """Test corner orientation is returned as a list."""
        _, co, _, _, _ = get_solved_cubies()
        self.assertIsInstance(co, list)

    def test_edge_permutation_is_list_not_tuple(self) -> None:
        """Test edge permutation is returned as a list."""
        _, _, ep, _, _ = get_solved_cubies()
        self.assertIsInstance(ep, list)

    def test_edge_orientation_is_list_not_tuple(self) -> None:
        """Test edge orientation is returned as a list."""
        _, _, _, eo, _ = get_solved_cubies()
        self.assertIsInstance(eo, list)

    def test_spatial_orientation_is_list_not_tuple(self) -> None:
        """Test spatial orientation is returned as a list."""
        _, _, _, _, so = get_solved_cubies()
        self.assertIsInstance(so, list)

    def test_consistent_results_for_same_size(self) -> None:
        """Test that calling with same size produces identical results."""
        for size in [2, 3, 4, 5]:
            result1 = get_solved_cubies(size)
            result2 = get_solved_cubies(size)
            self.assertEqual(result1, result2)

    def test_different_sizes_produce_different_edge_counts(self) -> None:
        """Test that different sizes produce different edge counts."""
        sizes = [2, 3, 4, 5]
        edge_counts = []
        for size in sizes:
            _, _, ep, _, _ = get_solved_cubies(size)
            edge_counts.append(len(ep))

        # All edge counts should be unique
        self.assertEqual(len(edge_counts), len(set(edge_counts)))

    def test_corner_elements_are_integers(self) -> None:
        """Test corner permutation contains only integers."""
        cp, _, _, _, _ = get_solved_cubies()
        for element in cp:
            self.assertIsInstance(element, int)

    def test_edge_permutation_elements_are_integers(self) -> None:
        """Test edge permutation contains only integers."""
        _, _, ep, _, _ = get_solved_cubies()
        for element in ep:
            self.assertIsInstance(element, int)

    def test_edge_orientation_elements_are_integers(self) -> None:
        """Test edge orientation contains only integers."""
        _, _, _, eo, _ = get_solved_cubies()
        for element in eo:
            self.assertIsInstance(element, int)

    def test_spatial_orientation_elements_are_integers(self) -> None:
        """Test spatial orientation contains only integers."""
        _, _, _, _, so = get_solved_cubies()
        for element in so:
            self.assertIsInstance(element, int)

    def test_size_10_edge_calculation(self) -> None:
        """Test larger cube: size 10 has correct edge calculation."""
        _, _, ep, eo, _ = get_solved_cubies(10)
        expected_edges = EDGE_NUMBER * (10 - 2)
        self.assertEqual(len(ep), expected_edges)
        self.assertEqual(len(eo), expected_edges)
        self.assertEqual(len(ep), 96)

    def test_edge_permutation_no_duplicates(self) -> None:
        """Test edge permutation has no duplicate values."""
        for size in [3, 4, 5, 6]:
            _, _, ep, _, _ = get_solved_cubies(size)
            self.assertEqual(len(ep), len(set(ep)))

    def test_corner_permutation_no_duplicates(self) -> None:
        """Test corner permutation has no duplicate values."""
        cp, _, _, _, _ = get_solved_cubies()
        self.assertEqual(len(cp), len(set(cp)))

    def test_spatial_orientation_no_duplicates(self) -> None:
        """Test spatial orientation has no duplicate values."""
        _, _, _, _, so = get_solved_cubies()
        self.assertEqual(len(so), len(set(so)))
