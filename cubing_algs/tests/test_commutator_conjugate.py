import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from cubing_algs.commutator_conjugate import expand_commutators_and_conjugates
from cubing_algs.commutator_conjugate import find_innermost_brackets
from cubing_algs.commutator_conjugate import invert_moves
from cubing_algs.commutator_conjugate import split_on_separator
from cubing_algs.exceptions import InvalidBracketError
from cubing_algs.exceptions import InvalidOperatorError


class TestFindInnermostBrackets(unittest.TestCase):

    def test_no_brackets(self):
        """Should return None when no brackets are present"""
        self.assertIsNone(find_innermost_brackets("R U R' U'"))

    def test_single_level_brackets(self):
        """Should find brackets at depth 1"""
        result = find_innermost_brackets("[R U R']")
        self.assertEqual(result, (0, 7))

    def test_nested_brackets(self):
        """Should find the deepest nested brackets"""
        result = find_innermost_brackets('[[R U], D]')
        self.assertEqual(result, (1, 5))  # Inner brackets [R U]

    def test_multiple_nested_brackets(self):
        """Should find first occurrence of deepest brackets"""
        result = find_innermost_brackets('[[R U], [D F]]')
        self.assertEqual(result, (1, 5))  # First inner brackets [R U]

    def test_complex_nesting(self):
        """Should handle complex nested structures"""
        result = find_innermost_brackets('[A [B [C D] E] F]')
        self.assertEqual(result, (6, 10))  # Innermost [C D]

    def test_empty_brackets(self):
        """Should handle empty brackets"""
        result = find_innermost_brackets('[]')
        self.assertEqual(result, (0, 1))

    def test_malformed_brackets_opening_only(self):
        """Should return None for malformed brackets (opening only)"""
        self.assertIsNone(find_innermost_brackets('[R U'))

    def test_malformed_brackets_closing_only(self):
        """Should return None for malformed brackets (closing only)"""
        self.assertIsNone(find_innermost_brackets('R U]'))


class TestSplitOnSeparator(unittest.TestCase):

    def test_no_separator(self):
        """Should return None when separator is not found"""
        self.assertIsNone(split_on_separator("R U R'", ','))

    def test_top_level_comma(self):
        """Should split on comma at top level"""
        result = split_on_separator('R U, D F', ',')
        self.assertEqual(result, ('R U', ' D F'))

    def test_top_level_colon(self):
        """Should split on colon at top level"""
        result = split_on_separator('R U: D F', ':')
        self.assertEqual(result, ('R U', ' D F'))

    def test_separator_inside_brackets(self):
        """Should not split on separator inside brackets"""
        self.assertIsNone(split_on_separator('R [U, D] F', ','))

    def test_nested_brackets_with_separator(self):
        """Should handle nested brackets with separator inside"""
        self.assertIsNone(split_on_separator('[[R, U], D]', ','))

    def test_multiple_separators_top_level(self):
        """Should split on first occurrence at top level"""
        result = split_on_separator('A, B, C', ',')
        self.assertEqual(result, ('A', ' B, C'))

    def test_separator_at_beginning(self):
        """Should handle separator at beginning"""
        result = split_on_separator(',R U', ',')
        self.assertEqual(result, ('', 'R U'))

    def test_separator_at_end(self):
        """Should handle separator at end"""
        result = split_on_separator('R U,', ',')
        self.assertEqual(result, ('R U', ''))


class TestInvertMoves(unittest.TestCase):

    @patch('cubing_algs.commutator_conjugate.Algorithm')
    @patch('cubing_algs.commutator_conjugate.mirror_moves')
    def test_invert_moves(self, mock_mirror_moves, mock_algorithm_class):
        """
        Should create algorithm, transform with mirror_moves,
        and return string
        """
        # Setup mocks
        mock_algorithm_instance = MagicMock()
        mock_transformed_algo = MagicMock()
        mock_algorithm_class.return_value = mock_algorithm_instance
        mock_algorithm_instance.__add__.return_value = mock_algorithm_instance
        mock_algorithm_instance.transform.return_value = mock_transformed_algo
        mock_transformed_algo.__str__.return_value = "R' U' R U"

        # Test
        result = invert_moves("R U R' U'")

        # Assertions
        mock_algorithm_class.assert_called_once()
        mock_algorithm_instance.__add__.assert_called_once_with("R U R' U'")
        mock_algorithm_instance.transform.assert_called_once_with(mock_mirror_moves)
        self.assertEqual(result, "R' U' R U")


class TestExpandCommutatorsAndConjugates(unittest.TestCase):

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_simple_commutator(self, mock_invert_moves):
        """Should expand simple commutator [A, B] to A B A' B'"""
        mock_invert_moves.side_effect = lambda x: f"{x}'"

        result = expand_commutators_and_conjugates('[R U, D F]')
        expected = " R U D F R U' D F' "
        self.assertEqual(result.strip(), expected.strip())

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_simple_conjugate(self, mock_invert_moves):
        """Should expand simple conjugate [A: B] to A B A'"""
        mock_invert_moves.return_value = "R'"

        result = expand_commutators_and_conjugates('[R: U]')
        expected = " R U R' "
        self.assertEqual(result.strip(), expected.strip())

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_nested_commutator(self, mock_invert_moves):
        """Should handle nested commutators"""
        mock_invert_moves.side_effect = lambda x: f"({x})'"

        result = expand_commutators_and_conjugates('[[R, U], D]')
        # Inner commutator [R, U] expands to "R U R' U'"
        # Then outer commutator with D
        self.assertIn("R U (R)' (U)'", result)

    def test_no_brackets(self):
        """Should return unchanged string when no brackets"""
        result = expand_commutators_and_conjugates("R U R' U'")
        self.assertEqual(result, "R U R' U'")

    def test_malformed_bracket_raises_error(self):
        """Should raise InvalidBracketError for malformed brackets"""
        with self.assertRaises(InvalidBracketError) as context:
            expand_commutators_and_conjugates("[R U R'")
        self.assertIn('Malformed bracket', str(context.exception))

    def test_invalid_operator_raises_error(self):
        """Should raise InvalidOperatorError for invalid operators"""
        with self.assertRaises(InvalidOperatorError) as context:
            expand_commutators_and_conjugates('[R U | D F]')
        self.assertIn('Invalid operator', str(context.exception))

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_empty_bracket_parts(self, mock_invert_moves):
        """Should handle empty bracket parts"""
        mock_invert_moves.return_value = ''

        result = expand_commutators_and_conjugates('[, D]')
        expected = '  D  '
        self.assertEqual(result.strip(), expected.strip())

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_multiple_brackets_same_level(self, mock_invert_moves):
        """Should handle multiple brackets at same level"""
        mock_invert_moves.side_effect = lambda x: f"{x}'"

        result = expand_commutators_and_conjugates('[R, U] [D, F]')
        # Should expand both commutators
        self.assertIn("R U R' U'", result)
        self.assertIn("D F D' F'", result)

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_mixed_operators(self, mock_invert_moves):
        """Should handle mix of commutators and conjugates"""
        mock_invert_moves.side_effect = lambda x: f"{x}'"

        result = expand_commutators_and_conjugates('[R: U] [D, F]')
        # Should have conjugate (R U R') and commutator (D F D' F')
        self.assertIn("R U R'", result)
        self.assertIn("D F D' F'", result)

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_recursive_expansion(self, mock_invert_moves):
        """Should recursively expand nested structures"""
        mock_invert_moves.side_effect = lambda x: f'inv({x})'

        # Test that recursive calls are made
        with patch(
                'cubing_algs.commutator_conjugate.expand_commutators_and_conjugates',
                wraps=expand_commutators_and_conjugates,
        ) as mock_expand:
            expand_commutators_and_conjugates('[[R, U]: D]')
            # Should make multiple recursive calls
            self.assertGreater(mock_expand.call_count, 1)


class TestEdgeCases(unittest.TestCase):

    def test_empty_string(self):
        """Should handle empty strings gracefully"""
        self.assertIsNone(find_innermost_brackets(''))
        self.assertIsNone(split_on_separator('', ','))
        self.assertEqual(expand_commutators_and_conjugates(''), '')

    def test_whitespace_handling(self):
        """Should handle whitespace in brackets"""
        result = find_innermost_brackets('[ R U ]')
        self.assertEqual(result, (0, 6))

        result = split_on_separator(' R U , D F ', ',')
        self.assertEqual(result, (' R U ', ' D F '))

    @patch('cubing_algs.commutator_conjugate.invert_moves')
    def test_single_character_moves(self, mock_invert_moves):
        """Should handle single character moves"""
        mock_invert_moves.side_effect = lambda x: f"{x}'"

        result = expand_commutators_and_conjugates('[R, U]')
        expected = " R U R' U' "
        self.assertEqual(result.strip(), expected.strip())

    def test_deeply_nested_brackets(self):
        """Should handle deeply nested bracket structures"""
        nested = '[[[[[A]]]]]'
        result = find_innermost_brackets(nested)
        self.assertEqual(result, (4, 6))  # Innermost [A]
