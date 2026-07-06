"""Tests for the command line interface."""
import io
import logging
import unittest
from contextlib import redirect_stderr
from contextlib import redirect_stdout

from cubing_algs.cli import main


class CliTestCase(unittest.TestCase):
    """Base class running the CLI and capturing its output."""

    @staticmethod
    def run_cli(*argv: str) -> tuple[int, str, str]:
        """
        Run the CLI capturing its outputs.

        Returns:
            Exit code, stdout and stderr contents.

        """
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()


class ParseCommandTestCase(CliTestCase):
    """Tests for the parse subcommand."""

    def test_parse_normalizes_algorithm(self) -> None:
        """Parse outputs the normalized algorithm."""
        code, out, _err = self.run_cli('parse', "R U R' U'")
        self.assertEqual(code, 0)
        self.assertEqual(out, "R U R' U'\n")

    def test_parse_invalid_moves_fails(self) -> None:
        """Parse fails with an error message on invalid input."""
        code, _out, err = self.run_cli('parse', 'R T')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_parse_invalid_moves_reports_single_diagnostic(self) -> None:
        """Parse silences the library log duplicating the CLI error."""
        code, _out, err = self.run_cli('parse', 'R T')
        self.assertEqual(code, 1)
        self.assertEqual(err.count('invalid move'), 1)
        self.assertFalse(
            logging.getLogger('cubing_algs.parsing').isEnabledFor(
                logging.ERROR,
            ),
        )


class MetricsCommandTestCase(CliTestCase):
    """Tests for the metrics subcommand."""

    def test_metrics_reports_scores(self) -> None:
        """Metrics outputs the metric scores of the algorithm."""
        code, out, _err = self.run_cli('metrics', "R U R' U'")
        self.assertEqual(code, 0)
        self.assertIn('htm:         4', out)
        self.assertIn('qtm:         4', out)
        self.assertIn('generators:  R U', out)


class ApplyCommandTestCase(CliTestCase):
    """Tests for the apply subcommand."""

    def test_apply_displays_cube(self) -> None:
        """Apply displays a non-empty cube rendering."""
        code, out, _err = self.run_cli('apply', "R U R' U'")
        self.assertEqual(code, 0)
        self.assertTrue(out)

    def test_apply_state_reports_facelets(self) -> None:
        """Apply with --state prints facelets and solved status."""
        code, out, _err = self.run_cli(
            'apply', "R U R' U'", '--state',
        )
        self.assertEqual(code, 0)
        self.assertIn(
            'Facelets: '
            'UULUUFUUFRRUBRRURRFFDFFUFFFDDRDDDDDDBLLLLLLLLBRRBBBBBB',
            out,
        )
        self.assertIn('Solved:   no', out)

    def test_apply_setup_then_inverse_is_solved(self) -> None:
        """Apply reports a solved cube when moves cancel the setup."""
        code, out, _err = self.run_cli(
            'apply', "U R U' R'", '--setup', "R U R' U'", '--state',
        )
        self.assertEqual(code, 0)
        self.assertIn('Solved:   yes', out)


class TransformCommandTestCase(CliTestCase):
    """Tests for the transform subcommand."""

    def test_transform_invert(self) -> None:
        """Transform inverts the algorithm."""
        code, out, _err = self.run_cli('transform', "R U R' U'", 'invert')
        self.assertEqual(code, 0)
        self.assertEqual(out, "U R U' R'\n")

    def test_transform_chain(self) -> None:
        """Transform chains multiple transforms in order."""
        code, out, _err = self.run_cli(
            'transform', "R U U R'", 'compress', 'invert',
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "R U2 R'\n")

    def test_transform_unknown_name_fails(self) -> None:
        """Transform fails on an unknown transform name."""
        code, _out, err = self.run_cli('transform', 'R U', 'unknown')
        self.assertEqual(code, 1)
        self.assertIn('unknown transform(s): unknown', err)
        self.assertIn('invert', err)


class CasesCommandTestCase(CliTestCase):
    """Tests for the cases subcommand."""

    def test_cases_lists_collections(self) -> None:
        """Cases without argument lists the collections."""
        code, out, _err = self.run_cli('cases')
        self.assertEqual(code, 0)
        self.assertIn('CFOP/OLL', out)
        self.assertIn('CFOP/PLL', out)

    def test_cases_lists_collection_cases(self) -> None:
        """Cases with a collection lists its cases and algorithms."""
        code, out, _err = self.run_cli('cases', 'OLL')
        self.assertEqual(code, 0)
        self.assertIn('OLL 27', out)

    def test_cases_invalid_collection_fails(self) -> None:
        """Cases fails on an invalid collection name."""
        code, _out, err = self.run_cli('cases', 'NOPE')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)


class CaseCommandTestCase(CliTestCase):
    """Tests for the case subcommand."""

    def test_case_shows_details(self) -> None:
        """Case shows the details of a single case."""
        code, out, _err = self.run_cli('case', 'OLL', '27')
        self.assertEqual(code, 0)
        self.assertIn('OLL 27', out)
        self.assertIn('Probability:', out)
        self.assertIn('Algorithms:', out)
        self.assertIn("R U R' U R U2 R'", out)

    def test_case_invalid_name_fails(self) -> None:
        """Case fails on an invalid case name."""
        code, _out, err = self.run_cli('case', 'OLL', 'NOPE')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)


if __name__ == '__main__':
    unittest.main()
