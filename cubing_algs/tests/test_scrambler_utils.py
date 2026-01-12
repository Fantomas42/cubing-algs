"""Tests for scrambler utility functions."""

import pytest

from cubing_algs.scrambler_utils import ALL_CORNERS
from cubing_algs.scrambler_utils import ALL_EDGES
from cubing_algs.scrambler_utils import CORNER_NAMES
from cubing_algs.scrambler_utils import D_CORNERS
from cubing_algs.scrambler_utils import D_EDGES
from cubing_algs.scrambler_utils import E_EDGES
from cubing_algs.scrambler_utils import EDGE_NAMES
from cubing_algs.scrambler_utils import F_CORNERS
from cubing_algs.scrambler_utils import U_CORNERS
from cubing_algs.scrambler_utils import U_EDGES
from cubing_algs.scrambler_utils import InvalidPieceSpecError
from cubing_algs.scrambler_utils import SolverNotAvailableError
from cubing_algs.scrambler_utils import parse_piece_spec
from cubing_algs.scrambler_utils import solve_to_algorithm
from cubing_algs.scrambler_utils import vcube_to_kociemba_string
from cubing_algs.vcube import VCube


class TestParsePieceSpec:
    """Tests for parse_piece_spec function."""

    def test_parse_all_corners(self) -> None:
        """Test parsing 'all' returns all corners."""
        result = parse_piece_spec('all', 'corner')
        assert result == ALL_CORNERS

    def test_parse_all_edges(self) -> None:
        """Test parsing 'all' returns all edges."""
        result = parse_piece_spec('all', 'edge')
        assert result == ALL_EDGES

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string returns all pieces."""
        assert parse_piece_spec('', 'corner') == ALL_CORNERS
        assert parse_piece_spec('', 'edge') == ALL_EDGES

    def test_parse_each_synonyms(self) -> None:
        """Test synonyms like 'each', 'every', 'any'."""
        for synonym in ['each', 'every', 'any']:
            assert parse_piece_spec(synonym, 'corner') == ALL_CORNERS
            assert parse_piece_spec(synonym, 'edge') == ALL_EDGES

    def test_parse_layer_u_corners(self) -> None:
        """Test parsing U layer returns U corners."""
        result = parse_piece_spec('U', 'corner')
        assert result == U_CORNERS

    def test_parse_layer_d_corners(self) -> None:
        """Test parsing D layer returns D corners."""
        result = parse_piece_spec('D', 'corner')
        assert result == D_CORNERS

    def test_parse_layer_f_corners(self) -> None:
        """Test parsing F layer returns F corners."""
        result = parse_piece_spec('F', 'corner')
        assert result == F_CORNERS

    def test_parse_layer_u_edges(self) -> None:
        """Test parsing U layer returns U edges."""
        result = parse_piece_spec('U', 'edge')
        assert result == U_EDGES

    def test_parse_layer_d_edges(self) -> None:
        """Test parsing D layer returns D edges."""
        result = parse_piece_spec('D', 'edge')
        assert result == D_EDGES

    def test_parse_layer_e_edges(self) -> None:
        """Test parsing E slice returns E edges."""
        result = parse_piece_spec('E', 'edge')
        assert result == E_EDGES

    def test_parse_specific_corner(self) -> None:
        """Test parsing specific corner by name."""
        result = parse_piece_spec('URF', 'corner')
        assert result == [0]  # URF is index 0

    def test_parse_multiple_specific_corners(self) -> None:
        """Test parsing multiple specific corners."""
        result = parse_piece_spec('URF UBR', 'corner')
        assert result == [0, 3]  # URF=0, UBR=3

    def test_parse_specific_edge(self) -> None:
        """Test parsing specific edge by name."""
        result = parse_piece_spec('UR', 'edge')
        assert result == [0]  # UR is index 0

    def test_parse_multiple_specific_edges(self) -> None:
        """Test parsing multiple specific edges."""
        result = parse_piece_spec('UR UF', 'edge')
        assert result == [0, 1]  # UR=0, UF=1

    def test_parse_mixed_layer_and_specific(self) -> None:
        """Test parsing mix of layer and specific pieces."""
        result = parse_piece_spec('U DFR', 'corner')
        expected = sorted(U_CORNERS + [4])  # U corners + DFR (index 4)
        assert result == expected

    def test_parse_case_insensitive(self) -> None:
        """Test parsing is case-insensitive."""
        result_upper = parse_piece_spec('URF', 'corner')
        result_lower = parse_piece_spec('urf', 'corner')
        result_mixed = parse_piece_spec('UrF', 'corner')
        assert result_upper == result_lower == result_mixed

    def test_parse_with_extra_whitespace(self) -> None:
        """Test parsing handles extra whitespace."""
        result = parse_piece_spec('  URF   UBR  ', 'corner')
        assert result == [0, 3]

    def test_parse_invalid_piece_type(self) -> None:
        """Test parsing with invalid piece type raises error."""
        with pytest.raises(InvalidPieceSpecError, match='piece_type must be'):
            parse_piece_spec('U', 'invalid')

    def test_parse_invalid_corner_name(self) -> None:
        """Test parsing invalid corner name raises error."""
        with pytest.raises(InvalidPieceSpecError, match='Unknown corner piece'):
            parse_piece_spec('XYZ', 'corner')

    def test_parse_invalid_edge_name(self) -> None:
        """Test parsing invalid edge name raises error."""
        with pytest.raises(InvalidPieceSpecError, match='Unknown edge piece'):
            parse_piece_spec('XY', 'edge')

    def test_parse_no_duplicates(self) -> None:
        """Test parsing removes duplicates."""
        result = parse_piece_spec('URF URF UBR', 'corner')
        assert result == [0, 3]  # No duplicates

    def test_parse_returns_sorted(self) -> None:
        """Test parsing returns sorted indices."""
        result = parse_piece_spec('UBR URF', 'corner')
        assert result == [0, 3]  # Sorted: 0, 3


class TestVCubeToKociemba:
    """Tests for VCube to Kociemba conversion."""

    def test_solved_cube_conversion(self) -> None:
        """Test converting solved cube to Kociemba format."""
        cube = VCube()
        kociemba_str = vcube_to_kociemba_string(cube)

        # Solved cube should have 9 of each face color
        assert len(kociemba_str) == 54
        assert kociemba_str.count('U') == 9
        assert kociemba_str.count('R') == 9
        assert kociemba_str.count('F') == 9
        assert kociemba_str.count('D') == 9
        assert kociemba_str.count('L') == 9
        assert kociemba_str.count('B') == 9

    def test_scrambled_cube_conversion(self) -> None:
        """Test converting scrambled cube to Kociemba format."""
        cube = VCube()
        cube.rotate("R U R' U'")
        kociemba_str = vcube_to_kociemba_string(cube)

        # Should still have 54 characters and 9 of each color
        assert len(kociemba_str) == 54
        assert kociemba_str.count('U') == 9
        assert kociemba_str.count('R') == 9
        assert kociemba_str.count('F') == 9
        assert kociemba_str.count('D') == 9
        assert kociemba_str.count('L') == 9
        assert kociemba_str.count('B') == 9

    def test_non_3x3x3_cube_raises_error(self) -> None:
        """Test that non-3x3x3 cubes raise ValueError."""
        cube = VCube(size=2)
        with pytest.raises(ValueError, match='only supports 3x3x3'):
            vcube_to_kociemba_string(cube)


class TestSolveToAlgorithm:
    """Tests for solve_to_algorithm function."""

    def test_solver_not_available_raises_error(self) -> None:
        """Test that missing kociemba package raises appropriate error."""
        # This test assumes kociemba is not installed
        # If it is installed, the test will be skipped
        try:
            import kociemba  # type: ignore[import-not-found] # noqa: F401
            pytest.skip('kociemba is installed, skipping unavailable test')
        except ImportError:
            pass

        solved_state = 'U' * 9 + 'R' * 9 + 'F' * 9 + 'D' * 9 + 'L' * 9 + 'B' * 9
        with pytest.raises(SolverNotAvailableError, match='pip install kociemba'):
            solve_to_algorithm(solved_state)

    def test_solve_solved_cube(self) -> None:
        """Test solving an already solved cube."""
        try:
            import kociemba  # type: ignore[import-not-found] # noqa: F401
        except ImportError:
            pytest.skip('kociemba not installed')

        solved_state = 'U' * 9 + 'R' * 9 + 'F' * 9 + 'D' * 9 + 'L' * 9 + 'B' * 9
        solution = solve_to_algorithm(solved_state)

        # Solved cube should return empty or very short solution
        assert isinstance(solution, str)
        assert len(solution) == 0 or solution.strip() == ''

    def test_solve_scrambled_cube(self) -> None:
        """Test solving a scrambled cube returns valid algorithm."""
        try:
            import kociemba  # type: ignore[import-not-found] # noqa: F401
        except ImportError:
            pytest.skip('kociemba not installed')

        cube = VCube()
        cube.rotate("R U R' U'")
        kociemba_str = vcube_to_kociemba_string(cube)
        solution = solve_to_algorithm(kociemba_str)

        # Should return a non-empty string with moves
        assert isinstance(solution, str)
        assert len(solution) > 0


class TestConstants:
    """Tests for constant definitions."""

    def test_corner_names_length(self) -> None:
        """Test CORNER_NAMES has 8 entries."""
        assert len(CORNER_NAMES) == 8

    def test_edge_names_length(self) -> None:
        """Test EDGE_NAMES has 12 entries."""
        assert len(EDGE_NAMES) == 12

    def test_corner_names_unique(self) -> None:
        """Test CORNER_NAMES has no duplicates."""
        assert len(CORNER_NAMES) == len(set(CORNER_NAMES))

    def test_edge_names_unique(self) -> None:
        """Test EDGE_NAMES has no duplicates."""
        assert len(EDGE_NAMES) == len(set(EDGE_NAMES))

    def test_layer_groups_no_overlap_corners(self) -> None:
        """Test U and D corner groups don't overlap."""
        assert set(U_CORNERS).isdisjoint(set(D_CORNERS))

    def test_layer_groups_cover_all_corners(self) -> None:
        """Test U and D groups cover all corners."""
        assert set(U_CORNERS) | set(D_CORNERS) == set(ALL_CORNERS)

    def test_layer_groups_no_overlap_edges(self) -> None:
        """Test U, D, and E edge groups don't overlap."""
        assert set(U_EDGES).isdisjoint(set(D_EDGES))
        assert set(U_EDGES).isdisjoint(set(E_EDGES))
        assert set(D_EDGES).isdisjoint(set(E_EDGES))

    def test_layer_groups_cover_all_edges(self) -> None:
        """Test U, D, and E groups cover all edges."""
        assert set(U_EDGES) | set(D_EDGES) | set(E_EDGES) == set(ALL_EDGES)
