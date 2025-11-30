"""Tests for multiplier and inversion notation parsing."""
import unittest

from cubing_algs.parenthesis import (
    expand_parenthesis_multipliers_and_inversions,
)


class ExpandParenthesisMultipliersTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for the expand_parenthesis_multipliers_and_inversions function."""

    def test_simple_multiplier(self) -> None:
        """Test simple parenthesis multiplier."""
        moves = '(R U)3'
        expected = 'R U R U R U'
        result = expand_parenthesis_multipliers_and_inversions(moves)
        self.assertEqual(result, expected)

    def test_complex_multiplier(self) -> None:
        """Test multiplier with complex move sequence."""
        moves = "(R U R' U')3"
        expected = "R U R' U' R U R' U' R U R' U'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_with_spaces(self) -> None:
        """Test multiplier with extra spaces."""
        moves = "( R U R' U' )3"
        expected = "R U R' U' R U R' U' R U R' U'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_without_spaces(self) -> None:
        """Test multiplier without extra spaces."""
        moves = "(RUR'U')3"
        expected = "R U R' U' R U R' U' R U R' U'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_in_sequence(self) -> None:
        """Test multiplier in middle of sequence."""
        moves = "R (U R')2 U"
        expected = "R U R' U R' U"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiple_multipliers(self) -> None:
        """Test multiple multipliers in one sequence."""
        moves = '(R U)2 (F R)2'
        expected = 'R U R U F R F R'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_nested_multipliers(self) -> None:
        """Test nested parenthesis multipliers."""
        moves = '((R U)2)3'
        expected = 'R U R U R U R U R U R U'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_with_single_move(self) -> None:
        """Test multiplier with single move."""
        moves = '(R)4'
        expected = 'R R R R'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_with_wide_moves(self) -> None:
        """Test multiplier with wide moves."""
        moves = '(Rw U)2'
        expected = 'Rw U Rw U'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_zero(self) -> None:
        """Test multiplier with zero (edge case)."""
        moves = "R (U R')0 F"
        expected = 'R  F'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiplier_one(self) -> None:
        """Test multiplier with one."""
        moves = '(R U)1'
        expected = 'R U'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_no_multiplier(self) -> None:
        """Test that parentheses without numbers are left unchanged."""
        moves = '(R U) R'
        expected = '(R U) R'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_no_parentheses(self) -> None:
        """Test string without parentheses."""
        moves = "R U R' U'"
        expected = "R U R' U'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    # Inversion tests
    def test_simple_inversion(self) -> None:
        """Test simple parenthesis inversion."""
        moves = "(R U)'"
        expected = "U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_complex_inversion(self) -> None:
        """Test inversion with complex move sequence."""
        moves = "(R U R' U')'"
        expected = "U R U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_complex_inversion_without_spaces(self) -> None:
        """Test multiplier without extra spaces."""
        moves = "(RUR'U')'"
        expected = "U R U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_inversion_with_double_moves(self) -> None:
        """Test inversion with R2 moves (should stay R2)."""
        moves = "(R U2 R')'"
        expected = "R U2 R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_inversion_single_move(self) -> None:
        """Test inversion with single move."""
        moves = "(R)'"
        expected = "R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_inversion_single_prime_move(self) -> None:
        """Test inversion with single prime move."""
        moves = "(R')'"
        expected = 'R'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_multiple_inversions(self) -> None:
        """Test multiple inversions in sequence."""
        moves = "(R U)' (F D)'"
        expected = "U' R' D' F'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    # Multiplier then inversion tests
    def test_multiplier_then_inversion(self) -> None:
        """Test multiplier followed by inversion."""
        moves = "(R U R' U')3'"
        expected = "U R U' R' U R U' R' U R U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_simple_multiplier_then_inversion(self) -> None:
        """Test simple multiplier then inversion."""
        moves = "(R U)2'"
        expected = "U' R' U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_simple_multiplier_then_inversion_without_spaces(self) -> None:
        """Test simple multiplier then inversion without spaces."""
        moves = "(RU)2'"
        expected = "U' R' U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_single_move_multiplier_then_inversion(self) -> None:
        """Test single move with multiplier then inversion."""
        moves = "(R)3'"
        expected = "R' R' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    # Nested inversion tests
    def test_nested_inversion_then_multiplier(self) -> None:
        """Test nested: inversion inside, then multiplier outside."""
        moves = "((R U)')2"
        expected = "U' R' U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_nested_multiplier_then_inversion(self) -> None:
        """Test nested: multiplier inside, then inversion outside."""
        moves = "((R U)2)'"
        expected = "U' R' U' R'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_double_nested_inversion(self) -> None:
        """Test double inversion (should cancel out)."""
        moves = "((R U)')'"
        expected = 'R U'
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    # Edge cases
    def test_empty_parenthesis_inversion(self) -> None:
        """Test empty parenthesis with inversion."""
        moves = "()'"
        expected = ''
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_inversion_with_wide_moves(self) -> None:
        """Test inversion with wide moves."""
        moves = "(Rw U)'"
        expected = "U' Rw'"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)

    def test_inversion_in_sequence(self) -> None:
        """Test inversion in middle of sequence."""
        moves = "R (U R')' F"
        expected = "R R U' F"
        result = expand_parenthesis_multipliers_and_inversions(moves)

        self.assertEqual(result, expected)
