"""
GPU rendering backend for VCube.

This sub-module is optional: it requires the ``opengl`` extra, which
ships ``moderngl`` for the rendering itself and ``glfw`` for the
interactive window.

Nothing here is imported when ``cubing_algs`` is loaded.
"""
from cubing_algs.display.gl.api import animate
from cubing_algs.display.gl.api import render
from cubing_algs.display.gl.clock import MoveClock
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.presentation import Playback
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.transforms import orientation_basis
from cubing_algs.display.gl.viewer import Stage
from cubing_algs.display.gl.viewer import Viewer

__all__ = [
    'Look',
    'MoveClock',
    'OrientationTracker',
    'Playback',
    'Presentation',
    'Quat',
    'Stage',
    'Viewer',
    'animate',
    'orientation_basis',
    'render',
]
