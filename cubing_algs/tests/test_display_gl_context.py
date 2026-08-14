"""Tests for the context creation of the GPU rendering backend."""
import os
import unittest
from typing import Any
from typing import ClassVar
from unittest import mock

from cubing_algs.display.gl.constants import GLFW_VARIANT_ENVIRONMENT
from cubing_algs.display.gl.constants import GLFW_VARIANT_FALLBACK
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.context import has_moderngl
from cubing_algs.display.gl.context import select_glfw_variant
from cubing_algs.display.gl.context import try_standalone_backend

requires_moderngl = unittest.skipUnless(
    has_moderngl(),
    'moderngl is not installed',
)

requires_glfw = unittest.skipUnless(
    has_glfw(),
    'glfw is not installed',
)


class FakeContext:
    """A context stub exposing what describe() reads."""

    version_code = 460

    info: ClassVar[dict[str, Any]] = {
        'GL_VENDOR': 'Fake',
        'GL_RENDERER': 'Fake Renderer',
        'GL_VERSION': '4.6 (Core Profile)',
        'GL_MAX_SAMPLES': 8,
        'GL_MAX_TEXTURE_SIZE': 4096,
    }


class TestExtras(unittest.TestCase):
    """Tests for the optional extras detection."""

    def test_render_extra_is_boolean(self) -> None:
        """Test that the render extra detection answers a boolean."""
        self.assertIsInstance(has_moderngl(), bool)

    def test_viewer_extra_is_boolean(self) -> None:
        """Test that the viewer extra detection answers a boolean."""
        self.assertIsInstance(has_glfw(), bool)


class TestMissingExtras(unittest.TestCase):
    """Tests for the errors raised when an extra is missing."""

    def test_standalone_without_moderngl(self) -> None:
        """Test that a headless context needs moderngl."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=False,
        ), self.assertRaises(GLContextError) as context:
            create_standalone_context()

        self.assertIn('moderngl', str(context.exception))

    def test_window_context_without_moderngl(self) -> None:
        """Test that a windowed context needs moderngl."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=False,
        ), self.assertRaises(GLContextError) as context:
            create_window_context()

        self.assertIn('moderngl', str(context.exception))

    def test_window_without_glfw(self) -> None:
        """Test that a window needs glfw."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_glfw',
                return_value=False,
        ), self.assertRaises(GLContextError) as context:
            create_window((64, 64))

        self.assertIn('glfw', str(context.exception))


class TestStandaloneFailures(unittest.TestCase):
    """Tests for the reporting of failed context creations."""

    def test_every_backend_is_reported(self) -> None:
        """Test that the error message gathers all the attempts."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=True,
        ), mock.patch(
                'cubing_algs.display.gl.context.try_standalone_backend',
                side_effect=[
                    (None, 'default: no such backend'),
                    (None, 'egl: no such backend'),
                ],
        ), self.assertRaises(GLContextError) as context:
            create_standalone_context()

        message = str(context.exception)

        self.assertIn('default: no such backend', message)
        self.assertIn('egl: no such backend', message)

    def test_first_backend_answering_wins(self) -> None:
        """Test that the first successful backend is returned."""
        expected = FakeContext()

        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=True,
        ), mock.patch(
                'cubing_algs.display.gl.context.try_standalone_backend',
                return_value=(expected, ''),
        ):
            self.assertIs(create_standalone_context(), expected)

    def test_every_library_is_reported(self) -> None:
        """Test that a windowed failure lists the tried libraries."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=True,
        ), mock.patch(
                'cubing_algs.display.gl.context.try_window_library',
                side_effect=[
                    (None, 'default: cannot open shared object file'),
                    (None, 'libGL.so.1: cannot open shared object file'),
                ],
        ), self.assertRaises(GLContextError) as context:
            create_window_context()

        message = str(context.exception)

        self.assertIn('default: cannot open', message)
        self.assertIn('libGL.so.1: cannot open', message)


@requires_moderngl
class TestUnknownBackend(unittest.TestCase):
    """Tests for a standalone backend the driver knows nothing about."""

    def test_failure_is_returned_not_raised(self) -> None:
        """Test that an unusable backend reports its own name."""
        context, failure = try_standalone_backend('nowhere', 330)

        self.assertIsNone(context)
        self.assertIn('nowhere', failure)


@requires_glfw
class TestWindowFailures(unittest.TestCase):
    """Tests for the failures of the windowing library."""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Choose the glfw variant before anything imports the library.

        pyGLFW reads its variant once, when it is imported, and patching
        one of its functions imports it. Leaving that to chance would
        load the Wayland variant on a Wayland session, and every later
        test needing a windowed context would fail.
        """
        select_glfw_variant()

    def test_glfw_cannot_start(self) -> None:
        """Test that a glfw refusing to start is reported."""
        with mock.patch('glfw.init', return_value=False), \
                self.assertRaises(GLContextError) as context:
            create_window((64, 64))

        self.assertIn('could not be initialized', str(context.exception))

    def test_window_cannot_be_created(self) -> None:
        """Test that a refused window shuts glfw down again."""
        with mock.patch('glfw.init', return_value=True), \
                mock.patch('glfw.window_hint'), \
                mock.patch('glfw.create_window', return_value=None), \
                mock.patch('glfw.terminate') as terminate, \
                self.assertRaises(GLContextError) as context:
            create_window((64, 64))

        self.assertIn('could not create', str(context.exception))
        terminate.assert_called_once_with()


class TestSelectGlfwVariant(unittest.TestCase):
    """Tests for select_glfw_variant function."""

    def test_wayland_selects_x11(self) -> None:
        """Test that a Wayland session falls back on the X11 variant."""
        environment = {'WAYLAND_DISPLAY': 'wayland-0'}

        with mock.patch.dict(os.environ, environment, clear=True):
            select_glfw_variant()

            self.assertEqual(
                os.environ[GLFW_VARIANT_ENVIRONMENT],
                GLFW_VARIANT_FALLBACK,
            )

    def test_explicit_variant_is_kept(self) -> None:
        """Test that a variant chosen by the user is left alone."""
        environment = {
            'WAYLAND_DISPLAY': 'wayland-0',
            GLFW_VARIANT_ENVIRONMENT: 'wayland',
        }

        with mock.patch.dict(os.environ, environment, clear=True):
            select_glfw_variant()

            self.assertEqual(
                os.environ[GLFW_VARIANT_ENVIRONMENT],
                'wayland',
            )

    def test_without_wayland_nothing_is_set(self) -> None:
        """Test that an X11 session is left untouched."""
        with mock.patch.dict(os.environ, {'DISPLAY': ':0'}, clear=True):
            select_glfw_variant()

            self.assertNotIn(GLFW_VARIANT_ENVIRONMENT, os.environ)


class TestDescribe(unittest.TestCase):
    """Tests for describe function."""

    def test_capabilities(self) -> None:
        """Test that the capabilities are summarized as strings."""
        context: Any = FakeContext()

        self.assertEqual(
            describe(context),
            {
                'vendor': 'Fake',
                'renderer': 'Fake Renderer',
                'version': '4.6 (Core Profile)',
                'version_code': '460',
                'max_samples': '8',
                'max_texture_size': '4096',
            },
        )

    def test_missing_keys_are_tolerated(self) -> None:
        """Test that an incomplete context still describes itself."""
        context: Any = FakeContext()
        context.info = {}

        self.assertEqual(describe(context)['vendor'], 'unknown')
