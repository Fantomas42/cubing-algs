"""Tests for the diagnostic of the GPU rendering backend."""
import io
import unittest
from typing import Any
from typing import ClassVar
from unittest import mock

from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.doctor import build_parser
from cubing_algs.display.gl.doctor import check_dependencies
from cubing_algs.display.gl.doctor import check_standalone
from cubing_algs.display.gl.doctor import check_window
from cubing_algs.display.gl.doctor import main
from cubing_algs.display.gl.doctor import report

DOCTOR = 'cubing_algs.display.gl.doctor'


def run_main(*, standalone: bool, window: bool) -> int:
    """
    Run the diagnostic with both checks forced to an outcome.

    Returns:
        The exit code of the diagnostic.

    """
    with mock.patch(f'{ DOCTOR }.check_dependencies'), \
         mock.patch(
             f'{ DOCTOR }.check_standalone', return_value=standalone,
         ), \
         mock.patch(f'{ DOCTOR }.check_window', return_value=window):
        return main([])


class FakeContext:
    """A context stub exposing what describe() reads."""

    version_code = 460

    info: ClassVar[dict[str, Any]] = {
        'GL_VENDOR': 'Fake',
        'GL_RENDERER': 'Fake Renderer',
        'GL_VERSION': '4.6 (Core Profile)',
    }

    def __init__(self) -> None:
        """Start with a context nobody released yet."""
        self.released = False

    def release(self) -> None:
        """Record that the context was released."""
        self.released = True


class DoctorTestCase(unittest.TestCase):
    """Base capturing what the doctor writes on standard output."""

    def setUp(self) -> None:
        """Redirect standard output to a buffer."""
        self.buffer = io.StringIO()
        patcher = mock.patch('sys.stdout', self.buffer)
        patcher.start()
        self.addCleanup(patcher.stop)

    @property
    def printed(self) -> str:
        """Give back everything written so far."""
        return self.buffer.getvalue()


class TestReport(DoctorTestCase):
    """Tests for report function."""

    def test_capabilities_are_listed(self) -> None:
        """Test that the label and the capabilities are printed."""
        context: Any = FakeContext()

        report('Some context', context)

        self.assertIn('Some context', self.printed)
        self.assertIn('renderer', self.printed)
        self.assertIn('Fake Renderer', self.printed)


class TestCheckDependencies(DoctorTestCase):
    """Tests for check_dependencies function."""

    def test_extra_is_named(self) -> None:
        """Test that the extra to install is spelled out."""
        with mock.patch(f'{ DOCTOR }.has_moderngl', return_value=True), \
             mock.patch(f'{ DOCTOR }.has_glfw', return_value=True):
            check_dependencies()

        self.assertIn('extra: opengl', self.printed)

    def test_available_dependencies(self) -> None:
        """Test that installed dependencies are reported as available."""
        with mock.patch(f'{ DOCTOR }.has_moderngl', return_value=True), \
             mock.patch(f'{ DOCTOR }.has_glfw', return_value=True):
            check_dependencies()

        self.assertIn('moderngl          : available', self.printed)
        self.assertIn('glfw              : available', self.printed)

    def test_missing_dependencies(self) -> None:
        """Test that absent dependencies are reported as missing."""
        with mock.patch(f'{ DOCTOR }.has_moderngl', return_value=False), \
             mock.patch(f'{ DOCTOR }.has_glfw', return_value=False):
            check_dependencies()

        self.assertIn('moderngl          : MISSING', self.printed)
        self.assertIn('glfw              : MISSING', self.printed)


class TestCheckStandalone(DoctorTestCase):
    """Tests for check_standalone function."""

    def test_gradient_is_written(self) -> None:
        """Test that a working context leads to an encoded image."""
        context = FakeContext()

        with mock.patch(
                f'{ DOCTOR }.create_standalone_context',
                return_value=context,
        ), mock.patch(
                f'{ DOCTOR }.render_gradient',
                return_value=b'\x00' * 16,
        ) as gradient, mock.patch(f'{ DOCTOR }.write_png') as write:
            self.assertTrue(check_standalone('/somewhere/out.png', 2))

        gradient.assert_called_once_with(context, 2)
        write.assert_called_once_with(
            '/somewhere/out.png', b'\x00' * 16, (2, 2),
        )
        self.assertTrue(context.released)

    def test_unavailable_context(self) -> None:
        """Test that a missing headless context is reported."""
        with mock.patch(
                f'{ DOCTOR }.create_standalone_context',
                side_effect=GLContextError('no EGL here'),
        ):
            self.assertFalse(check_standalone('/somewhere/out.png', 2))

        self.assertIn('UNAVAILABLE', self.printed)
        self.assertIn('no EGL here', self.printed)


class TestCheckWindow(DoctorTestCase):
    """Tests for check_window function."""

    def test_window_is_destroyed(self) -> None:
        """Test that a working window is closed once checked."""
        context = FakeContext()

        with mock.patch(
                f'{ DOCTOR }.create_window',
                return_value='window',
        ), mock.patch(
                f'{ DOCTOR }.create_window_context',
                return_value=context,
        ), mock.patch(f'{ DOCTOR }.destroy_window') as destroy:
            self.assertTrue(check_window(64))

        destroy.assert_called_once_with('window')
        self.assertTrue(context.released)

    def test_unavailable_window(self) -> None:
        """Test that a missing windowed context is reported."""
        with mock.patch(
                f'{ DOCTOR }.create_window',
                side_effect=GLContextError('no display'),
        ):
            self.assertFalse(check_window(64))

        self.assertIn('UNAVAILABLE', self.printed)
        self.assertIn('no display', self.printed)


class TestBuildParser(unittest.TestCase):
    """Tests for build_parser function."""

    def test_defaults(self) -> None:
        """Test that the diagnostic runs without any argument."""
        options = build_parser().parse_args([])

        self.assertTrue(options.out.endswith('gl-doctor.png'))
        self.assertEqual(options.image_size, 512)

    def test_options(self) -> None:
        """Test that destination and size can be chosen."""
        options = build_parser().parse_args(
            ['--out', 'a.png', '--image-size', '64'],
        )

        self.assertEqual(options.out, 'a.png')
        self.assertEqual(options.image_size, 64)


class TestMain(DoctorTestCase):
    """Tests for main function."""

    def test_everything_works(self) -> None:
        """Test that a fully capable machine exits cleanly."""
        self.assertEqual(run_main(standalone=True, window=True), 0)

    def test_headless_only(self) -> None:
        """Test that a machine without window still succeeds."""
        self.assertEqual(run_main(standalone=True, window=False), 0)
        self.assertIn('viewer is unavailable', self.printed)

    def test_window_only(self) -> None:
        """Test that a machine without offscreen rendering fails."""
        self.assertEqual(run_main(standalone=False, window=True), 1)
        self.assertIn('Offscreen rendering is unavailable', self.printed)

    def test_nothing_works(self) -> None:
        """Test that a machine without any context fails."""
        self.assertEqual(run_main(standalone=False, window=False), 1)
        self.assertIn('No OpenGL context at all', self.printed)
