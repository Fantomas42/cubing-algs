"""
Public API of the GPU rendering backend.

Everything the rest of the library, the CLI and the outside world need,
in one place: build a scene, frame it, draw it, encode the result. The
modules underneath stay free of any glue.
"""
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from cubing_algs.display.gl.animation import Animation
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.encode import has_pillow
from cubing_algs.display.gl.encode import write_frames
from cubing_algs.display.gl.encode import write_gif
from cubing_algs.display.gl.presentation import DEFAULT_PLAYBACK
from cubing_algs.display.gl.presentation import DEFAULT_PRESENTATION
from cubing_algs.display.gl.presentation import Playback
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.renderer import render_frames
from cubing_algs.display.gl.renderer import render_scene
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.move import Move

if TYPE_CHECKING:  # pragma: no cover
    from cubing_algs.vcube import VCube


def render(
        cube: 'VCube',
        presentation: Presentation = DEFAULT_PRESENTATION,
) -> bytes:
    """
    Render a cube on the GPU, without any window.

    The framing is the one of the SVG backend: same rotation string,
    same distance, same palette, same modes and masks, so that both
    renderings of a cube can be compared side by side. It is fitted to
    the sphere the cube actually fills, which the gap and the chamfer
    make slightly smaller than the box it is laid out in: every size
    comes out at the same apparent size, whatever the cube.

    Args:
        cube: The cube to draw.
        presentation: How the picture is made: framing, palette, mode,
            mask, image size, look, and the way the cube is held. The
            library default picture when left out.

    Returns:
        The bytes of a PNG image, its background left transparent.

    """
    scene = build_scene(
        cube,
        presentation.palette,
        mode=presentation.mode,
        mask=presentation.mask,
    )

    pixels = render_scene(
        scene,
        presentation.camera(scene.geometry.radius),
        presentation,
    )

    return encode_png(pixels, presentation.size)


def animate(
        cube: 'VCube',
        moves: Iterable[Move | str] | Move | str,
        path: str | Path,
        presentation: Presentation = DEFAULT_PRESENTATION,
        playback: Playback = DEFAULT_PLAYBACK,
) -> list[Path]:
    """
    Play an algorithm on a cube and write it as an animation.

    The framing, the palette and the modes are the ones of ``render()``:
    an animation is the same picture, several times, the layers of the
    move under way turned part of the way round. The cube given is left
    untouched, and the state it ends on is the one applying the whole
    algorithm to it would give.

    A GIF is written when Pillow is around. It is not required: without
    it the frames are written as numbered PNG files instead, which any
    encoder can assemble. A series of frames carries no timing, so the
    pace of the playback, the holds on the first and the last frame
    included, only reaches the GIF: what a PNG frame lasts is for the
    encoder assembling them to say.

    Args:
        cube: The cube to play the algorithm on.
        moves: The algorithm to play.
        path: Where the animation is written.
        presentation: How each frame is made: framing, palette, mode,
            mask, image size, look, and the way the cube is held.
        playback: How the animation runs: frame rate, how long a move
            lasts, how long the states it starts from and ends on are
            held, and how many times it plays.

    Returns:
        The paths written to: the GIF alone, or one per frame.

    """
    animation = Animation(
        cube, moves, presentation, duration=playback.duration,
    )

    frames = render_frames(
        animation.play(playback.frame_rate),
        presentation.camera(animation.geometry.radius),
        presentation,
    )

    if not has_pillow():
        return write_frames(path, frames, presentation.size)

    return [
        write_gif(path, frames, presentation.size, playback=playback),
    ]
