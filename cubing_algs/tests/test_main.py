"""Tests for the ``python -m cubing_algs`` entry point."""
import runpy
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch


class MainEntryPointTestCase(unittest.TestCase):
    """Tests for the ``__main__`` module."""

    def test_runs_main_and_exits_with_its_return_code(self) -> None:
        """Running the module executes the CLI and exits with its code."""
        argv = ['cubing_algs', 'parse', "R U R' U'"]
        with (
            patch.object(sys, 'argv', argv),
            redirect_stdout(StringIO()) as out,
            self.assertRaises(SystemExit) as ctx,
        ):
            runpy.run_module('cubing_algs.__main__', run_name='__main__')

        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(out.getvalue(), "R U R' U'\n")

    def test_importing_the_module_does_not_run_the_cli(self) -> None:
        """Importing the module normally does not trigger the CLI."""
        namespace = runpy.run_module(
            'cubing_algs.__main__', run_name='cubing_algs.__main__',
        )

        self.assertEqual(namespace['__name__'], 'cubing_algs.__main__')
