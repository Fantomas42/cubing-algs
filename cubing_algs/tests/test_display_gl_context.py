"""Tests for the context creation of the GPU rendering backend."""
import importlib
import os
import unittest
from typing import Any
from typing import ClassVar
from unittest import mock

from cubing_algs.display.gl import context
from cubing_algs.display.gl.constants import GLFW_VARIANT_ENVIRONMENT
from cubing_algs.display.gl.constants import GLFW_VARIANT_FALLBACK
from cubing_algs.display.gl.constants import X11_CARDINAL
from cubing_algs.display.gl.constants import X11_FORMAT_32
from cubing_algs.display.gl.constants import X11_PROPERTY_REPLACE
from cubing_algs.display.gl.constants import X11_USER_TIME_ATOM
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import check_glfw_platform
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import deny_focus_on_map
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.context import has_moderngl
from cubing_algs.display.gl.context import select_glfw_variant
from cubing_algs.display.gl.context import transparency_granted
from cubing_algs.display.gl.context import try_context

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
                'cubing_algs.display.gl.context.try_context',
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
                'cubing_algs.display.gl.context.try_context',
                return_value=(expected, ''),
        ):
            self.assertIs(create_standalone_context(), expected)

    def test_every_library_is_reported(self) -> None:
        """Test that a windowed failure lists the tried libraries."""
        with mock.patch(
                'cubing_algs.display.gl.context.has_moderngl',
                return_value=True,
        ), mock.patch(
                'cubing_algs.display.gl.context.try_context',
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
        context, failure = try_context(
            'backend', 'nowhere', {'standalone': True, 'require': 330},
        )

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

    def test_platform_moderngl_can_attach_to(self) -> None:
        """Test that a platform holding a readable context goes through."""
        import glfw

        with mock.patch(
                'glfw.get_platform',
                return_value=glfw.PLATFORM_X11,
        ) as platform:
            # Raising nothing is the whole answer of the check.
            check_glfw_platform()

        self.assertEqual(platform.call_count, 1)

    def test_wayland_platform_is_refused(self) -> None:
        """Test that a glfw locked on Wayland says so, and gives up."""
        import glfw

        with mock.patch('glfw.init', return_value=True), \
                mock.patch(
                    'glfw.get_platform',
                    return_value=glfw.PLATFORM_WAYLAND,
                ), \
                mock.patch('glfw.terminate') as terminate, \
                self.assertRaises(GLContextError) as context:
            create_window((64, 64))

        message = str(context.exception)

        self.assertIn('Wayland', message)
        self.assertIn(GLFW_VARIANT_ENVIRONMENT, message)
        terminate.assert_called_once_with()

    def test_window_cannot_be_created(self) -> None:
        """Test that a refused window shuts glfw down again."""
        import glfw

        with mock.patch('glfw.init', return_value=True), \
                mock.patch(
                    'glfw.get_platform',
                    return_value=glfw.PLATFORM_X11,
                ), \
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

    def test_importing_the_backend_chooses_the_variant(self) -> None:
        """
        Test that importing the backend settles the variant by itself.

        Every module of the backend imports this one, so choosing the
        variant here is what keeps an ``import glfw`` of a viewer, of a
        test or of a caller from locking the Wayland one in first. A
        viewer importing glfw a single line before create_window() had
        its say held a context nobody could attach to.
        """
        environment = {'WAYLAND_DISPLAY': 'wayland-0'}
        original_error = context.GLContextError

        try:
            with mock.patch.dict(os.environ, environment, clear=True):
                importlib.reload(context)

                self.assertEqual(
                    os.environ[GLFW_VARIANT_ENVIRONMENT],
                    GLFW_VARIANT_FALLBACK,
                )
        finally:
            # Reloading builds a new GLContextError class, while every
            # module importing it by name still holds the first one:
            # what the module raises would no longer be what the rest of
            # the suite catches. The module goes back as it was found.
            importlib.reload(context)
            context.GLContextError = original_error  # type: ignore[misc]

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


class TestTransparencyGranted(unittest.TestCase):
    """Tests for reading back what a compositor made of a hint."""

    def test_a_granted_transparency(self) -> None:
        """Test that a window truly letting the desktop through says so."""
        with mock.patch.dict(
                'sys.modules', {'glfw': mock.MagicMock()},
        ) as modules:
            modules['glfw'].get_window_attrib.return_value = 1

            self.assertTrue(transparency_granted(object()))

    def test_a_refused_transparency(self) -> None:
        """Test that an ordinary opaque window says so too."""
        with mock.patch.dict(
                'sys.modules', {'glfw': mock.MagicMock()},
        ) as modules:
            modules['glfw'].get_window_attrib.return_value = 0

            self.assertFalse(transparency_granted(object()))


class TestDenyFocusOnMap(unittest.TestCase):
    """Tests for the window manager side of ``focus_on_show``."""

    def test_a_window_asking_for_the_focus_is_left_alone(self) -> None:
        """Test that a window shown for its own sake writes nothing."""
        with mock.patch('glfw.init', return_value=True), \
                mock.patch('glfw.window_hint'), \
                mock.patch('glfw.create_window', return_value=object()), \
                mock.patch('glfw.make_context_current'), \
                mock.patch(
                    'cubing_algs.display.gl.context.check_glfw_platform',
                ), \
                mock.patch(
                    'cubing_algs.display.gl.context.deny_focus_on_map',
                ) as deny:
            create_window((64, 64))

        self.assertEqual(deny.call_count, 0)

    def test_a_window_refusing_the_focus_says_so_to_the_manager(
            self,
    ) -> None:
        """Test that the hint alone is never the whole of the answer."""
        window = object()

        with mock.patch('glfw.init', return_value=True), \
                mock.patch('glfw.window_hint'), \
                mock.patch('glfw.create_window', return_value=window), \
                mock.patch('glfw.make_context_current'), \
                mock.patch(
                    'cubing_algs.display.gl.context.check_glfw_platform',
                ), \
                mock.patch(
                    'cubing_algs.display.gl.context.deny_focus_on_map',
                ) as deny:
            create_window((64, 64), focus_on_show=False)

        self.assertEqual(deny.call_count, 1)
        self.assertIs(deny.call_args[0][0], window)

    def test_nothing_is_written_off_x11(self) -> None:
        """Test that a platform with no Xlib to reach is left alone."""
        with mock.patch.dict(
                'sys.modules', {'glfw': mock.MagicMock()},
        ) as modules, \
                mock.patch('ctypes.CDLL') as library:
            modules['glfw'].get_platform.return_value = 'cocoa'
            modules['glfw'].PLATFORM_X11 = 'x11'

            deny_focus_on_map(object())

        self.assertEqual(library.call_count, 0)

    def test_a_missing_xlib_costs_the_focus_and_not_the_window(self) -> None:
        """Test that an Xlib nothing can load is not an error."""
        with mock.patch.dict(
                'sys.modules', {'glfw': mock.MagicMock()},
        ) as modules, \
                mock.patch(
                    'ctypes.CDLL', side_effect=OSError,
                ) as library:
            modules['glfw'].get_platform.return_value = 'x11'
            modules['glfw'].PLATFORM_X11 = 'x11'

            # Returning at all is the whole answer: the window opens
            # with the focus wrong rather than not opening.
            deny_focus_on_map(object())

        self.assertEqual(library.call_count, 1)

    def test_the_property_a_manager_reads(self) -> None:
        """Test that the user time is held at zero on the window."""
        xlib = mock.MagicMock()
        xlib.XInternAtom.return_value = 287

        with mock.patch.dict(
                'sys.modules', {'glfw': mock.MagicMock()},
        ) as modules, \
                mock.patch('ctypes.CDLL', return_value=xlib):
            modules['glfw'].get_platform.return_value = 'x11'
            modules['glfw'].PLATFORM_X11 = 'x11'
            modules['glfw'].get_x11_display.return_value = 42
            modules['glfw'].get_x11_window.return_value = 1024

            deny_focus_on_map(object())

        name = xlib.XInternAtom.call_args[0][1]
        self.assertEqual(name, X11_USER_TIME_ATOM)

        arguments = xlib.XChangeProperty.call_args[0]

        self.assertEqual(arguments[1], 1024)
        self.assertEqual(arguments[2], 287)
        self.assertEqual(arguments[3], X11_CARDINAL)
        self.assertEqual(arguments[4], X11_FORMAT_32)
        self.assertEqual(arguments[5], X11_PROPERTY_REPLACE)

        self.assertEqual(xlib.XFlush.call_count, 1)
