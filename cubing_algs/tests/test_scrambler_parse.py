"""Tests for scrambler parsing functions."""
import unittest

from cubing_algs.constants import D_CORNERS
from cubing_algs.constants import D_EDGES
from cubing_algs.constants import E_EDGES
from cubing_algs.constants import F_CORNERS
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import U_CORNERS
from cubing_algs.constants import U_EDGES
from cubing_algs.exceptions import InvalidPieceSpecError
from cubing_algs.scrambler.parse import parse_piece_spec


class TestParsePieceSpec(unittest.TestCase):  # noqa: PLR0904
    """Tests for parse_piece_spec function."""

    def test_parse_all_corners(self) -> None:
        """Test parsing 'all' returns all corners."""
        result = parse_piece_spec('all', 'corner')
        self.assertEqual(result, SOLVED_CP)

    def test_parse_all_edges(self) -> None:
        """Test parsing 'all' returns all edges."""
        result = parse_piece_spec('all', 'edge')
        self.assertEqual(result, SOLVED_EP)

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string returns all pieces."""
        self.assertEqual(parse_piece_spec('', 'corner'), SOLVED_CP)
        self.assertEqual(parse_piece_spec('', 'edge'), SOLVED_EP)

    def test_parse_each_synonyms(self) -> None:
        """Test synonyms like 'each', 'every', 'any'."""
        for synonym in ['each', 'every', 'any']:
            self.assertEqual(parse_piece_spec(synonym, 'corner'), SOLVED_CP)
            self.assertEqual(parse_piece_spec(synonym, 'edge'), SOLVED_EP)

    def test_parse_layer_u_corners(self) -> None:
        """Test parsing U layer returns U corners."""
        result = parse_piece_spec('U', 'corner')
        self.assertEqual(result, U_CORNERS)

    def test_parse_layer_d_corners(self) -> None:
        """Test parsing D layer returns D corners."""
        result = parse_piece_spec('D', 'corner')
        self.assertEqual(result, D_CORNERS)

    def test_parse_layer_f_corners(self) -> None:
        """Test parsing F layer returns F corners."""
        result = parse_piece_spec('F', 'corner')
        self.assertEqual(result, F_CORNERS)

    def test_parse_layer_u_edges(self) -> None:
        """Test parsing U layer returns U edges."""
        result = parse_piece_spec('U', 'edge')
        self.assertEqual(result, U_EDGES)

    def test_parse_layer_d_edges(self) -> None:
        """Test parsing D layer returns D edges."""
        result = parse_piece_spec('D', 'edge')
        self.assertEqual(result, D_EDGES)

    def test_parse_layer_e_edges(self) -> None:
        """Test parsing E slice returns E edges."""
        result = parse_piece_spec('E', 'edge')
        self.assertEqual(result, E_EDGES)

    def test_parse_specific_corner(self) -> None:
        """Test parsing specific corner by name."""
        result = parse_piece_spec('URF', 'corner')
        self.assertEqual(result, [0])  # URF is index 0

    def test_parse_multiple_specific_corners(self) -> None:
        """Test parsing multiple specific corners."""
        result = parse_piece_spec('URF UBR', 'corner')
        self.assertEqual(result, [0, 3])  # URF=0, UBR=3

    def test_parse_specific_edge(self) -> None:
        """Test parsing specific edge by name."""
        result = parse_piece_spec('UR', 'edge')
        self.assertEqual(result, [0])  # UR is index 0

    def test_parse_multiple_specific_edges(self) -> None:
        """Test parsing multiple specific edges."""
        result = parse_piece_spec('UR UF', 'edge')
        self.assertEqual(result, [0, 1])  # UR=0, UF=1

    def test_parse_mixed_layer_and_specific(self) -> None:
        """Test parsing mix of layer and specific pieces."""
        result = parse_piece_spec('U DFR', 'corner')
        expected = sorted([*U_CORNERS, 4])  # U corners + DFR (index 4)
        self.assertEqual(result, expected)

    def test_parse_case_insensitive(self) -> None:
        """Test parsing is case-insensitive."""
        result_upper = parse_piece_spec('URF', 'corner')
        result_lower = parse_piece_spec('urf', 'corner')
        result_mixed = parse_piece_spec('UrF', 'corner')
        self.assertEqual(result_upper, result_lower)
        self.assertEqual(result_lower, result_mixed)

    def test_parse_with_extra_whitespace(self) -> None:
        """Test parsing handles extra whitespace."""
        result = parse_piece_spec('  URF   UBR  ', 'corner')
        self.assertEqual(result, [0, 3])

    def test_parse_with_multiple_spaces_between(self) -> None:
        """Test parsing handles multiple spaces between tokens."""
        result = parse_piece_spec('URF     UBR', 'corner')
        self.assertEqual(result, [0, 3])

    def test_parse_invalid_piece_type(self) -> None:
        """Test parsing with invalid piece type raises error."""
        with self.assertRaises(InvalidPieceSpecError):
            parse_piece_spec('U', 'invalid')  # type: ignore[arg-type]

    def test_parse_invalid_corner_name(self) -> None:
        """Test parsing invalid corner name raises error."""
        with self.assertRaises(InvalidPieceSpecError):
            parse_piece_spec('XYZ', 'corner')

    def test_parse_invalid_edge_name(self) -> None:
        """Test parsing invalid edge name raises error."""
        with self.assertRaises(InvalidPieceSpecError):
            parse_piece_spec('XY', 'edge')

    def test_parse_no_duplicates(self) -> None:
        """Test parsing removes duplicates."""
        result = parse_piece_spec('URF URF UBR', 'corner')
        self.assertEqual(result, [0, 3])  # No duplicates

    def test_parse_returns_sorted(self) -> None:
        """Test parsing returns sorted indices."""
        result = parse_piece_spec('UBR URF', 'corner')
        self.assertEqual(result, [0, 3])  # Sorted: 0, 3

    def test_parse_with_empty_tokens(self) -> None:
        """Test parsing handles empty tokens from multiple spaces."""
        result = parse_piece_spec('URF  UBR', 'corner')
        self.assertEqual(result, [0, 3])
