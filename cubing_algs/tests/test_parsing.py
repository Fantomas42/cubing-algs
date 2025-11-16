"""Tests for algorithm parsing functions."""

import unittest

from cubing_algs.exceptions import InvalidBracketError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.exceptions import InvalidOperatorError
from cubing_algs.move import Move
from cubing_algs.parsing import check_moves
from cubing_algs.parsing import clean_moves
from cubing_algs.parsing import clean_multiline_and_comments
from cubing_algs.parsing import parse_moves
from cubing_algs.parsing import parse_moves_cfop
from cubing_algs.parsing import split_moves


class CleanMovesTestCase(unittest.TestCase):
    """Tests for the clean_moves function."""

    def test_clean_moves(self) -> None:
        """Test clean moves."""
        moves = "R2 L2  (y):F B2' e U R` U’  "  # noqa: RUF001
        expect = "R2 L2 y F B2 E U R' U'"
        self.assertEqual(clean_moves(moves), expect)


class SplitMovesTestCase(unittest.TestCase):
    """Tests for the split_moves function."""

    def test_split_moves(self) -> None:
        """Test split moves."""
        moves = "R2L2yFB2EU'R'U'"
        expect = ['R2', 'L2', 'y', 'F', 'B2', 'E', "U'", "R'", "U'"]
        self.assertEqual(split_moves(moves), expect)

    def test_split_big_moves(self) -> None:
        """Test split big moves."""
        moves = "3R 3Uw' 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

        moves = "3R3Uw'3b2-3Dw3-4d"
        expect = ['3R', "3Uw'", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_moves(self) -> None:
        """Test split timed moves."""
        moves = "3R 3Uw'@1500 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_pauses(self) -> None:
        """Test split timed pauses."""
        moves = "3R 3Uw'@1500 .@2000 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '.@2000', '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_moves_with_pauses(self) -> None:
        """Test split timed moves with pauses."""
        moves = "3R 3Uw'@1500 . 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '.', '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)


class CheckMovesTestCase(unittest.TestCase):
    """Tests for the check_moves function."""

    def test_check_moves(self) -> None:
        """Test check moves."""
        moves = split_moves('R2 L2')
        self.assertTrue(check_moves(moves))

    def test_check_moves_invalid_move(self) -> None:
        """Test check moves invalid move."""
        moves = [Move('T2'), Move('R')]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_wide_standard_move(self) -> None:
        """Test check moves invalid wide standard move."""
        moves = [Move('Rw')]
        self.assertTrue(check_moves(moves))
        moves = [Move('Rw3')]
        self.assertFalse(check_moves(moves))
        moves = [Move("Rw2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_wide_sign_move(self) -> None:
        """Test check moves invalid wide sign move."""
        moves = [Move('r')]
        self.assertTrue(check_moves(moves))
        moves = [Move('r3')]
        self.assertFalse(check_moves(moves))
        moves = [Move("r2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_modifier(self) -> None:
        """Test check moves invalid modifier."""
        moves = [Move('R5')]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_too_long(self) -> None:
        """Test check moves invalid too long."""
        moves = [Move("R2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_layer(self) -> None:
        """Test check moves invalid layer."""
        moves = [Move('2-4R')]
        self.assertFalse(check_moves(moves))


class ParseMovesTestCase(unittest.TestCase):
    """Tests for the parse_moves function."""

    def test_parse_moves(self) -> None:
        """Test parse moves."""
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_moves_with_pauses(self) -> None:
        """Test parse moves with pauses."""
        moves = 'R2 . L2 .'
        expect = ['R2', '.', 'L2', '.']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

        moves = 'R2 ... L2 .'
        expect = ['R2', '.', '.', '.', 'L2', '.']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_list(self) -> None:
        """Test parse list."""
        moves = ['R2 L2']
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

        moves = ['R2', 'L2']
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_moves_invalid(self) -> None:
        """Test parse moves invalid."""
        moves = 'R2 T2'
        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_invalid_case_but_corrected(self) -> None:
        """Test parse moves invalid case but corrected."""
        moves = ['R2', 'X2']
        expect = ['R2', 'x2']
        self.assertEqual(
            parse_moves(moves, secure=False),
            expect,
        )

        moves = ['R2', 'm2']
        expect = ['R2', 'M2']
        self.assertEqual(
            parse_moves(moves, secure=False),
            expect,
        )

    def test_parse_moves_list_moves(self) -> None:
        """Test parse moves list moves."""
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_algorithm(self) -> None:
        """Test parse moves algorithm."""
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_conjugate(self) -> None:
        """Test parse moves conjugate."""
        moves = 'F [R, U] F'
        expect = ['F', 'R', 'U', "R'", "U'", 'F']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

        moves = 'F[R,U]F'
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_conjugate_malformed(self) -> None:
        """Test parse moves conjugate malformed."""
        moves = 'F [R, U F'

        self.assertRaises(
            InvalidBracketError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_conjugate_invalid_moves(self) -> None:
        """Test parse moves conjugate invalid moves."""
        moves = 'F [T, U] F'

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=True,
        )

    def test_parse_moves_conjugate_nested(self) -> None:
        """Test parse moves conjugate nested."""
        moves = 'F [[R, U], B] F'
        expect = [
            'F',
            'R', 'U', "R'", "U'",
            'B',
            'U', 'R', "U'", "R'",
            "B'",
            'F',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_commutator(self) -> None:
        """Test parse moves commutator."""
        moves = 'F [R: U] F'
        expect = ['F', 'R', 'U', "R'", 'F']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

        moves = 'F[R:U]F'
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_commutator_malformed(self) -> None:
        """Test parse moves commutator malformed."""
        moves = 'F [R: U F'

        self.assertRaises(
            InvalidBracketError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_commutator_invalid_moves(self) -> None:
        """Test parse moves commutator invalid moves."""
        moves = 'F [T: U] F'

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=True,
        )

    def test_parse_moves_commutator_nested(self) -> None:
        """Test parse moves commutator nested."""
        moves = 'F [[R: U]: B] F'
        expect = [
            'F',
            'R', 'U', "R'",
            'B',
            'R', "U'", "R'",
            'F',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_invalid_operator(self) -> None:
        """Test parse moves invalid operator."""
        moves = 'F [R; U] F'

        self.assertRaises(
            InvalidOperatorError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_complex_1(self) -> None:
        """Test parse moves complex 1."""
        moves = '[[R: U], D] B [F: [U, R]]'
        expect = [
            'R', 'U', "R'", 'D',
            'R', "U'", "R'", "D'",
            'B',
            'F', 'U', 'R', "U'", "R'", "F'",
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_complex_2(self) -> None:
        """Test parse moves complex 2."""
        moves = '[[R F: U L], D] B'
        expect = [
            'R', 'F', 'U', 'L', "F'", "R'",
            'D',
            'R', 'F', "L'", "U'", "F'", "R'",
            "D'",
            'B',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )


class ParseMovesCFOPTestCase(unittest.TestCase):
    """Tests for the parse_moves_cfop function."""

    def test_parse_moves_cfop(self) -> None:
        """Test parse moves cfop."""
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves_cfop(moves),
            expect,
        )

    def test_parse_moves_cfop_cleaned(self) -> None:
        """Test parse moves cfop cleaned."""
        moves = 'U R2 L2 y'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves_cfop(moves),
            expect,
        )

    def test_parse_moves_cfop_cleaned_advanced(self) -> None:
        """Test parse moves cfop cleaned."""
        moves = "U' y  R2 L2 U y2"
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves_cfop(moves),
            expect,
        )


class CleanMultilineAndCommentsTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for cleaning multiline text and removing comments."""

    def test_simple_text_without_comments_or_newlines_fast_path(self) -> None:
        """Test the fast path when no comments or newlines are present."""
        text = "R U R' U'"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U'")

    def test_simple_text_with_spaces_only(self) -> None:
        """Test text with only spaces but no comments or newlines."""
        text = "R  U   R'    U'"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R  U   R'    U'")

    def test_single_line_with_comment_at_end(self) -> None:
        """Test removing comment from end of single line."""
        text = "R U R' U' // This is a comment"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U'")

    def test_single_line_with_comment_at_start(self) -> None:
        """Test line starting with comment."""
        text = '// This is a comment'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_single_line_comment_only_no_moves(self) -> None:
        """Test line with only comment and whitespace."""
        text = '   // Just a comment   '
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_single_line_with_comment_in_middle(self) -> None:
        """Test comment appearing in middle of moves."""
        text = "R U // comment here R' U'"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, 'R U')

    def test_multiple_comment_markers_in_line(self) -> None:
        """Test line with multiple // markers."""
        text = 'R U // first comment // second comment'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, 'R U')

    def test_multiline_without_comments(self) -> None:
        """Test multiline text without any comments."""
        text = "R U R' U'\nD' R D\nF R F'"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_multiline_with_comments(self) -> None:
        """Test multiline text with comments on each line."""
        text = (
            "R U R' U' // first part\n"
            "D' R D // second part\n"
            "F R F' // third part"
        )
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_multiline_with_some_comments(self) -> None:
        """Test multiline where only some lines have comments."""
        text = "R U R' U' // with comment\nD' R D\nF R F' // another comment"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_multiline_with_empty_lines(self) -> None:
        """Test multiline with empty lines that should be ignored."""
        text = "R U R' U'\n\nD' R D\n   \nF R F'"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_multiline_with_comment_only_lines(self) -> None:
        """Test multiline with lines containing only comments."""
        text = (
            "R U R' U'\n"
            "// This is just a comment\n"
            "D' R D\n"
            "// Another comment\n"
            "F R F'"
        )
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_multiline_mixed_empty_and_comment_lines(self) -> None:
        """Test complex multiline with empty lines, comments, and moves."""
        text = """R U R' U' // setup

        // This is a comment line
        D' R D

        // Another comment

        F R F' // finish"""
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R U R' U' D' R D F R F'")

    def test_whitespace_only_before_comment(self) -> None:
        """Test line with only whitespace before comment."""
        text = 'R U\n   // whitespace before comment\nD R'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, 'R U D R')

    def test_whitespace_preservation_within_moves(self) -> None:
        """Test that whitespace between moves is preserved appropriately."""
        text = "R  U   R'\nD    R     D"
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, "R  U   R' D    R     D")

    def test_empty_string(self) -> None:
        """Test empty string input."""
        text = ''
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_whitespace_only_string(self) -> None:
        """Test string with only whitespace."""
        text = '   \n  \n   '
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_newline_only_string(self) -> None:
        """Test string with only newlines."""
        text = '\n\n\n'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_comment_markers_only(self) -> None:
        """Test string with only comment markers."""
        text = '//\n//\n//'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_single_newline_character(self) -> None:
        """Test string that is just a newline character."""
        text = '\n'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, '')

    def test_comment_with_no_space_after_marker(self) -> None:
        """Test comment marker directly followed by text."""
        text = 'R U//comment\nD R'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, 'R U D R')

    def test_moves_after_comment_removal_with_extra_spaces(self) -> None:
        """Test extra spaces are handled correctly after comment removal."""
        text = 'R U   // comment with spaces\n   D R   // another comment'
        result = clean_multiline_and_comments(text)
        self.assertEqual(result, 'R U D R')


class ParseMovesMultilineIntegrationTestCase(unittest.TestCase):
    """Tests for multiline move parsing integration."""

    def test_parse_moves_multiline_basic(self) -> None:
        """Test basic multiline parsing integration."""
        multiline_moves = """R U R' U'
        D' R D"""
        single_line_moves = "R U R' U' D' R D"

        multiline_result = parse_moves(multiline_moves)
        single_line_result = parse_moves(single_line_moves)

        self.assertEqual(multiline_result, single_line_result)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D']
        self.assertEqual(list(multiline_result), expected)

    def test_parse_moves_multiline_with_comments(self) -> None:
        """Test multiline parsing with comments."""
        multiline_moves = """R U R' U' // first pair
        D' R D // second pair
        F R F' // third pair"""
        single_line_moves = "R U R' U' D' R D F R F'"

        multiline_result = parse_moves(multiline_moves)
        single_line_result = parse_moves(single_line_moves)

        self.assertEqual(multiline_result, single_line_result)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D', 'F', 'R', "F'"]
        self.assertEqual(list(multiline_result), expected)

    def test_parse_moves_multiline_complex_scramble(self) -> None:
        """Test parsing a complex multiline scramble with comments."""
        scramble = """R2 U2 R2 D2 F2 U2 L2 U2 R2 // cross edges
        B' R' F R B R' F' R // F2L-1
        U' R U R' U R U R' // F2L-2
        U2 R U R' U R U' R' // F2L-3
        U R U' R' F R F' // F2L-4 + OLL
        R U R' F' R U R' U' R' F R2 U' R' U' // PLL"""

        expected_moves = [
            'R2', 'U2', 'R2', 'D2', 'F2', 'U2', 'L2', 'U2', 'R2',
            "B'", "R'", 'F', 'R', 'B', "R'", "F'", 'R',
            "U'", 'R', 'U', "R'", 'U', 'R', 'U', "R'",
            'U2', 'R', 'U', "R'", 'U', 'R', "U'", "R'",
            'U', 'R', "U'", "R'", 'F', 'R', "F'",
            'R', 'U', "R'", "F'", 'R', 'U', "R'", "U'", "R'", 'F', 'R2', "U'",
            "R'", "U'",
        ]

        result = parse_moves(scramble)
        self.assertEqual(list(result), expected_moves)

    def test_parse_moves_multiline_with_empty_lines(self) -> None:
        """Test multiline parsing with empty lines."""
        multiline_moves = """R U R' U'

        D' R D

        F R F'"""

        result = parse_moves(multiline_moves)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D', 'F', 'R', "F'"]
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_comment_only_lines(self) -> None:
        """Test multiline parsing with comment-only lines."""
        multiline_moves = """R U R' U'
        // This is just a comment
        D' R D
        // Another comment line
        F R F'"""

        result = parse_moves(multiline_moves)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D', 'F', 'R', "F'"]
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_with_commutators(self) -> None:
        """Test multiline parsing with commutators and comments."""
        multiline_moves = """F [R, U] F' // setup and commutator
        D' R D // additional moves"""

        result = parse_moves(multiline_moves)
        expected = ['F', 'R', 'U', "R'", "U'", "F'", "D'", 'R', 'D']
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_with_conjugates(self) -> None:
        """Test multiline parsing with conjugates and comments."""
        multiline_moves = """[R: U R U'] // conjugate
        F R F' // more moves"""

        result = parse_moves(multiline_moves)
        expected = ['R', 'U', 'R', "U'", "R'", 'F', 'R', "F'"]
        self.assertEqual(list(result), expected)

    def test_parse_moves_backward_compatibility_single_line(self) -> None:
        """Test that single line input still works exactly as before."""
        single_line = "R U R' U' D' R D F R F'"
        result = parse_moves(single_line)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D', 'F', 'R', "F'"]
        self.assertEqual(list(result), expected)

    def test_parse_moves_backward_compatibility_with_existing_comments(
            self) -> None:
        """Test backward compatibility when comments were in single line."""
        moves_with_comment = "R U R' U' // this should work"
        result = parse_moves(moves_with_comment)
        expected = ['R', 'U', "R'", "U'"]
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_secure_mode(self) -> None:
        """Test multiline parsing with secure mode enabled."""
        multiline_moves = """R U R' U' // first part
        D' R D // second part"""

        result = parse_moves(multiline_moves, secure=True)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D']
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_non_secure_mode(self) -> None:
        """Test multiline parsing with secure mode disabled."""
        multiline_moves = """R U R' U' // first part
        D' R D // second part"""

        result = parse_moves(multiline_moves, secure=False)
        expected = ['R', 'U', "R'", "U'", "D'", 'R', 'D']
        self.assertEqual(list(result), expected)

    def test_parse_moves_multiline_with_pauses(self) -> None:
        """Test multiline parsing with pause notation."""
        multiline_moves = """R U . R' U' // with pause
        D' R D . // ending pause"""

        result = parse_moves(multiline_moves)
        expected = ['R', 'U', '.', "R'", "U'", "D'", 'R', 'D', '.']
        self.assertEqual(list(result), expected)
