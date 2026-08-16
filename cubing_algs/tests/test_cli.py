"""Tests for the command line interface."""
import io
import json
import logging
import unittest
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cubing_algs.cases import get_case
from cubing_algs.cli import main
from cubing_algs.cli import window_size
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves
from cubing_algs.vcube import VCube

# Main algorithm of the OLL 27 case, which is not the first of the
# alternatives the case also lists.
MAIN_OLL_27 = "L' U2 L U L' U L"


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

    def test_apply_size_builds_a_bigger_cube(self) -> None:
        """Apply with --size runs the algorithm on an NxN cube."""
        code, out, _err = self.run_cli(
            'apply', "Rw U Rw' U'", '--size', '5', '--state',
        )
        expected = VCube(size=5)
        expected.rotate("Rw U Rw' U'")

        self.assertEqual(code, 0)
        self.assertIn(f'Facelets: { expected.state }', out)
        self.assertIn('Solved:   no', out)

    def test_apply_setup_then_inverse_is_solved(self) -> None:
        """Apply reports a solved cube when moves cancel the setup."""
        code, out, _err = self.run_cli(
            'apply', "U R U' R'", '--setup', "R U R' U'", '--state',
        )
        self.assertEqual(code, 0)
        self.assertIn('Solved:   yes', out)

    def test_apply_render_writes_a_png(self) -> None:
        """Apply with --render writes the image instead of the net."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ) as rendered, TemporaryDirectory() as directory:
            path = Path(directory) / 'cube.png'
            code, out, _err = self.run_cli(
                'apply', "R U R' U'",
                '--mode', 'oll', '--render', str(path),
                '--image-size', '128', '--rotation', 'y90', '--distance', '20',
            )

        self.assertEqual(code, 0)
        self.assertIn(f'Rendered: { path }', out)
        self.assertEqual(
            rendered.call_args.kwargs,
            {
                'mode': 'oll',
                'mask': '',
                'palette': '',
                'image_size': 128,
                'rotation': 'y90',
                'distance': 20.0,
            },
        )

    def test_apply_render_replaces_the_terminal_net(self) -> None:
        """The cube goes to the file, not to the terminal, and once."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ), TemporaryDirectory() as directory:
            path = Path(directory) / 'cube.png'
            _code, out, _err = self.run_cli(
                'apply', "R U R' U'", '--render', str(path), '--state',
            )

        self.assertEqual(out.count('\n'), 3)
        self.assertIn('Facelets: ', out)

    def test_apply_view_opens_a_window(self) -> None:
        """Apply with --view hands the cube over to the viewer."""
        with mock.patch.object(VCube, 'view', autospec=True) as viewed:
            code, out, _err = self.run_cli(
                'apply', "R U R' U'", '--view', '--image-size', '320',
            )

        self.assertEqual(code, 0)
        self.assertEqual(out, '')
        self.assertEqual(viewed.call_args.kwargs['window_size'], (320, 320))

    def test_apply_view_opens_at_the_default_size(self) -> None:
        """No size asked for leaves the one of the viewer alone."""
        with mock.patch.object(VCube, 'view', autospec=True) as viewed:
            self.run_cli('apply', "R U R' U'", '--view')

        self.assertIsNone(viewed.call_args.kwargs['window_size'])

    def test_apply_orientation_is_held_before_the_algorithm(self) -> None:
        """The orientation is how the cube is held, so it comes first."""
        code, out, _err = self.run_cli(
            'apply', "R U R' U'", '--orientation', 'DF', '--state',
        )

        expected = VCube()
        expected.rotate('z2')
        expected.rotate("R U R' U'")

        self.assertEqual(code, 0)
        self.assertIn(f'Facelets: { expected.state }', out)

    def test_apply_orientation_holds_the_setup_too(self) -> None:
        """The setup is played in the orientation as well."""
        code, out, _err = self.run_cli(
            'apply', "U R U' R'", '--setup', "R U R' U'",
            '--orientation', 'RF', '--state',
        )

        expected = VCube()
        expected.rotate("z'")
        expected.rotate("R U R' U'")
        expected.rotate("U R U' R'")

        self.assertEqual(code, 0)
        self.assertIn(f'Facelets: { expected.state }', out)
        self.assertIn('Solved:   yes', out)

    def test_apply_orientation_reaches_the_render_as_a_turned_cube(
            self,
    ) -> None:
        """The backend is handed the turned cube, not the orientation."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ) as rendered, TemporaryDirectory() as directory:
            code, _out, _err = self.run_cli(
                'apply', "R U R' U'", '--orientation', 'DF',
                '--render', str(Path(directory) / 'cube.png'),
            )

        expected = VCube()
        expected.rotate('z2')
        expected.rotate("R U R' U'")

        self.assertEqual(code, 0)
        self.assertEqual(rendered.call_args.args[0].state, expected.state)
        self.assertNotIn('orientation', rendered.call_args.kwargs)

    def test_apply_orientation_reaches_the_viewer_as_a_turned_cube(
            self,
    ) -> None:
        """The viewer opens on the turned cube, not on the orientation."""
        with mock.patch.object(VCube, 'view', autospec=True) as viewed:
            code, _out, _err = self.run_cli(
                'apply', "R U R' U'", '--orientation', 'DF', '--view',
            )

        expected = VCube()
        expected.rotate('z2')
        expected.rotate("R U R' U'")

        self.assertEqual(code, 0)
        self.assertEqual(viewed.call_args.args[0].state, expected.state)
        self.assertNotIn('orientation', viewed.call_args.kwargs)

    def test_apply_invalid_orientation_fails(self) -> None:
        """Apply fails with an error message on an unknown orientation."""
        code, _out, err = self.run_cli(
            'apply', "R U R' U'", '--orientation', 'UU',
        )
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_apply_render_wins_over_view(self) -> None:
        """A file is written rather than a window opened."""
        with (
                mock.patch.object(
                    VCube, 'render', autospec=True, return_value=b'PNG',
                ),
                mock.patch.object(VCube, 'view', autospec=True) as viewed,
                TemporaryDirectory() as directory,
        ):
            self.run_cli(
                'apply', "R U R' U'", '--view',
                '--render', str(Path(directory) / 'cube.png'),
            )

        viewed.assert_not_called()


class AnimateCommandTestCase(CliTestCase):
    """Tests for the animate subcommand."""

    def test_animate_writes_an_animation(self) -> None:
        """Animate plays the algorithm and says where it landed."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('sexy.gif')],
        ) as animated:
            code, out, _err = self.run_cli(
                'animate', "R U R' U'", '--out', 'sexy.gif',
            )

        self.assertEqual(code, 0)
        self.assertIn('Animated: sexy.gif', out)
        self.assertEqual(str(animated.call_args.args[1]), "R U R' U'")
        self.assertEqual(animated.call_args.args[2], 'sexy.gif')

    def test_animate_sums_up_a_series_of_frames(self) -> None:
        """Without Pillow, the frames are counted rather than listed."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[
                    Path('sexy-000.png'),
                    Path('sexy-001.png'),
                    Path('sexy-002.png'),
                ],
        ):
            _code, out, _err = self.run_cli(
                'animate', "R U R' U'", '--out', 'sexy.gif',
            )

        self.assertEqual(
            out,
            'Animated: 3 frames, sexy-000.png to sexy-002.png\n',
        )

    def test_animate_display_options_reach_the_backend(self) -> None:
        """Every display option given lands on the animation."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('sexy.gif')],
        ) as animated:
            code, _out, _err = self.run_cli(
                'animate', "R U R' U'", '--out', 'sexy.gif',
                '--mode', 'pll', '--orientation', 'DF',
                '--mask', '1' * 54, '--palette', 'neon',
                '--image-size', '128', '--rotation', 'y90', '--distance', '20',
            )

        self.assertEqual(code, 0)
        self.assertEqual(
            animated.call_args.kwargs,
            {
                'mode': 'pll',
                'mask': '1' * 54,
                'palette': 'neon',
                'image_size': 128,
                'rotation': 'y90',
                'distance': 20.0,
            },
        )

    def test_animate_setup_reaches_the_cube(self) -> None:
        """The setup is played before the algorithm is animated."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('sexy.gif')],
        ) as animated:
            self.run_cli(
                'animate', "R U R' U'", '--out', 'sexy.gif',
                '--setup', "F R U'",
            )

        cube = VCube()
        cube.rotate("F R U'")

        self.assertEqual(animated.call_args.args[0].state, cube.state)

    def test_animate_orientation_turns_the_cube_before_the_setup(self) -> None:
        """The cube is turned first, then the setup is played on it."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('sexy.gif')],
        ) as animated:
            self.run_cli(
                'animate', "R U R' U'", '--out', 'sexy.gif',
                '--setup', "F R U'", '--orientation', 'DF',
            )

        expected = VCube()
        expected.rotate('z2')
        expected.rotate("F R U'")

        self.assertEqual(animated.call_args.args[0].state, expected.state)

    def test_animate_invalid_orientation_fails(self) -> None:
        """Animate fails with an error message on an unknown orientation."""
        code, _out, err = self.run_cli(
            'animate', "R U R' U'", '--out', 'nope.gif',
            '--orientation', 'UU',
        )
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_animate_size_builds_the_right_cube(self) -> None:
        """A cube of the size asked for is the one being animated."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('nxn.gif')],
        ) as animated:
            code, _out, _err = self.run_cli(
                'animate', "Rw U 3Rw' M2 x", '--out', 'nxn.gif', '--size', '5',
            )

        self.assertEqual(code, 0)
        self.assertEqual(animated.call_args.args[0].size, 5)

    def test_animate_invalid_moves_fails(self) -> None:
        """Animate fails with an error message on invalid input."""
        code, _out, err = self.run_cli(
            'animate', 'R T', '--out', 'nope.gif',
        )
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_animate_invalid_size_fails(self) -> None:
        """Animate fails on a cube size no cube can have."""
        code, _out, err = self.run_cli(
            'animate', "R U R' U'", '--out', 'nope.gif', '--size', '0',
        )
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)


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


class CompressCommandTestCase(CliTestCase):
    """Tests for the compress subcommand."""

    def test_compress_commutator(self) -> None:
        """Compress rewrites a commutator in bracket notation."""
        code, out, _err = self.run_cli('compress', "R U R' U'")
        self.assertEqual(code, 0)
        self.assertEqual(out, '[R, U]\n')

    def test_compress_conjugate(self) -> None:
        """Compress rewrites a conjugate wrapping a commutator."""
        code, out, _err = self.run_cli('compress', "F R U R' U' F'")
        self.assertEqual(code, 0)
        self.assertEqual(out, '[F: [R, U]]\n')

    def test_compress_invalid_moves_fails(self) -> None:
        """Compress fails with an error message on invalid input."""
        code, _out, err = self.run_cli('compress', 'R T')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)


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

    def test_case_shows_the_main_algorithm(self) -> None:
        """Case shows the main algorithm, the one the drawn case expects."""
        case = get_case('OLL', '27')

        code, out, _err = self.run_cli('case', 'OLL', '27')

        self.assertEqual(code, 0)
        self.assertIn(f'Main:        { case.main_algorithm }', out)

    def test_case_invalid_name_fails(self) -> None:
        """Case fails on an invalid case name."""
        code, _out, err = self.run_cli('case', 'OLL', 'NOPE')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_case_render_draws_the_case_itself(self) -> None:
        """The cube drawn is the one the main algorithm solves."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ) as rendered, TemporaryDirectory() as directory:
            path = Path(directory) / 'oll27.png'
            code, out, _err = self.run_cli(
                'case', 'OLL', '27', '--render', str(path),
                '--image-size', '128',
            )

        self.assertEqual(code, 0)
        self.assertIn(f'Rendered: { path }', out)
        self.assertFalse(rendered.call_args.args[0].is_solved)
        self.assertEqual(rendered.call_args.kwargs['mode'], 'oll')
        self.assertEqual(rendered.call_args.kwargs['image_size'], 128)

    def test_case_render_sets_the_cube_up_to_the_case(self) -> None:
        """The main algorithm played from there solves the cube."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ) as rendered, TemporaryDirectory() as directory:
            self.run_cli(
                'case', 'OLL', '27',
                '--render', str(Path(directory) / 'oll27.png'),
            )

        cube = rendered.call_args.args[0]
        self.assertFalse(cube.is_solved)

        cube.rotate(MAIN_OLL_27)
        self.assertTrue(cube.is_solved)

    def test_case_animate_plays_the_solution(self) -> None:
        """Animating a case plays its main algorithm from the case."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('oll27.gif')],
        ) as animated:
            code, out, _err = self.run_cli(
                'case', 'OLL', '27', '--animate', 'oll27.gif',
            )

        self.assertEqual(code, 0)
        self.assertIn('Animated: oll27.gif', out)
        self.assertEqual(str(animated.call_args.args[1]), MAIN_OLL_27)
        self.assertEqual(animated.call_args.args[2], 'oll27.gif')
        self.assertEqual(animated.call_args.kwargs['mode'], 'oll')

    def test_case_view_opens_a_window(self) -> None:
        """Viewing a case hands the case cube over to the viewer."""
        with mock.patch.object(VCube, 'view', autospec=True) as viewed:
            code, _out, _err = self.run_cli('case', 'PLL', 'Ua', '--view')

        self.assertEqual(code, 0)
        self.assertEqual(viewed.call_args.kwargs['mode'], 'pll')

    def test_case_orientation_sets_the_case_up_from_there(self) -> None:
        """The cube is turned first, then set up to the case on it."""
        with mock.patch.object(
                VCube, 'render', autospec=True, return_value=b'PNG',
        ) as rendered, TemporaryDirectory() as directory:
            code, _out, _err = self.run_cli(
                'case', 'OLL', '27', '--orientation', 'DF',
                '--render', str(Path(directory) / 'oll27.png'),
            )

        expected = VCube()
        expected.rotate('z2')
        expected.rotate(parse_moves(MAIN_OLL_27).transform(invert_moves))

        self.assertEqual(code, 0)
        self.assertEqual(rendered.call_args.args[0].state, expected.state)
        self.assertNotIn('orientation', rendered.call_args.kwargs)

    def test_case_orientation_still_solves_the_case(self) -> None:
        """The main algorithm played from there solves the turned cube."""
        with mock.patch.object(
                VCube, 'animate', autospec=True,
                return_value=[Path('oll27.gif')],
        ) as animated:
            self.run_cli(
                'case', 'OLL', '27', '--orientation', 'RF',
                '--animate', 'oll27.gif',
            )

        cube = animated.call_args.args[0]
        self.assertFalse(cube.is_solved)

        cube.rotate(MAIN_OLL_27)
        self.assertTrue(cube.is_solved)

    def test_case_invalid_orientation_fails(self) -> None:
        """Case fails with an error message on an unknown orientation."""
        with TemporaryDirectory() as directory:
            code, _out, err = self.run_cli(
                'case', 'OLL', '27', '--orientation', 'UU',
                '--render', str(Path(directory) / 'oll27.png'),
            )

        self.assertEqual(code, 1)
        self.assertIn('Error:', err)

    def test_case_without_gpu_options_draws_nothing(self) -> None:
        """The details alone never reach the GPU backend."""
        with (
                mock.patch.object(VCube, 'render', autospec=True) as rendered,
                mock.patch.object(VCube, 'view', autospec=True) as viewed,
                mock.patch.object(VCube, 'animate', autospec=True) as animated,
        ):
            self.run_cli('case', 'OLL', '27')

        rendered.assert_not_called()
        viewed.assert_not_called()
        animated.assert_not_called()


class WindowSizeTestCase(unittest.TestCase):
    """Tests for the window size a pixel count asks for."""

    def test_a_size_is_squared(self) -> None:
        """A pixel count opens a square window."""
        self.assertEqual(window_size(320), (320, 320))

    def test_no_size_leaves_the_default_one(self) -> None:
        """No pixel count leaves the default size of the viewer alone."""
        self.assertIsNone(window_size(0))


class InfoCommandTestCase(CliTestCase):
    """Tests for the info subcommand."""

    def test_info_outputs_full_analysis(self) -> None:
        """Info outputs the complete to_dict payload as JSON."""
        code, out, _err = self.run_cli('info', "R U R' U'")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data['moves'], "R U R' U'")
        for section in (
                'metrics', 'ergonomics', 'structure', 'memory', 'impacts',
        ):
            self.assertIn(section, data)

    def test_info_section_keeps_overview_and_requested(self) -> None:
        """Info with a section drops other analysis blocks."""
        code, out, _err = self.run_cli(
            'info', "R U R' U'", '--section', 'metrics',
        )
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn('moves', data)
        self.assertIn('metrics', data)
        self.assertNotIn('ergonomics', data)
        self.assertNotIn('impacts', data)

    def test_info_multiple_sections(self) -> None:
        """Info accepts a comma-separated list of sections."""
        code, out, _err = self.run_cli(
            'info', "R U R' U'", '--section', 'metrics,memory',
        )
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn('metrics', data)
        self.assertIn('memory', data)
        self.assertNotIn('structure', data)

    def test_info_size_reaches_impacts(self) -> None:
        """Info forwards the cube size to the impacts computation."""
        code, out, _err = self.run_cli('info', 'Rw U', '--size', '4')
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn('impacts', data)

    def test_info_unknown_section_fails(self) -> None:
        """Info fails on an unknown section name."""
        code, _out, err = self.run_cli('info', "R U R' U'", '--section', 'foo')
        self.assertEqual(code, 1)
        self.assertIn('unknown section(s): foo', err)

    def test_info_invalid_moves_fails(self) -> None:
        """Info fails with an error message on invalid input."""
        code, _out, err = self.run_cli('info', 'R T')
        self.assertEqual(code, 1)
        self.assertIn('Error:', err)
