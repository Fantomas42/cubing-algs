"""
Public API of the GPU rendering backend.

Everything the rest of the library, the CLI and the outside world need,
in one place: build a scene, frame it, draw it, encode the result. The
modules underneath stay free of any glue.
"""
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.display.gl.animation import Animation
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import ANIMATION_LOOP
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.encode import has_pillow
from cubing_algs.display.gl.encode import write_frames
from cubing_algs.display.gl.encode import write_gif
from cubing_algs.display.gl.renderer import render_frames
from cubing_algs.display.gl.renderer import render_scene
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.move import Move

if TYPE_CHECKING:  # pragma: no cover
    from cubing_algs.vcube import VCube


def render(  # noqa: PLR0913
        cube: 'VCube',
        *,
        image_size: int = RENDER_SIZE,
        rotation: str = '',
        distance: float = 0.0,
        palette: str = '',
        mode: str = '',
        mask: CubeDisplayMask = '',
        look: Look = DEFAULT_LOOK,
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
        image_size: Width and height of the image, in pixels.
        rotation: Camera rotation string, such as ``y45x-34``. Empty for
            the library default.
        distance: Distance from the camera to the cube. Zero for the
            library default.
        palette: Name of the color palette. Empty for the default one.
        mode: Display preset presetting the mask and the orientation,
            such as ``oll`` or ``f2l``.
        mask: Display mask, one code per facelet. Overrides the mask the
            mode would have set.
        look: How the light falls on the cube, antialiasing included.
            The library default one unless a variant is being tried out.

    Returns:
        The bytes of a PNG image, its background left transparent.

    """
    scene = build_scene(cube, palette, mode=mode, mask=mask)

    pixels = render_scene(
        scene,
        OrbitCamera.from_rotation(
            rotation, distance, scene.geometry.radius,
        ),
        image_size=image_size,
        look=look,
    )

    return encode_png(pixels, (image_size, image_size))


def animate(  # noqa: PLR0913
        cube: 'VCube',
        moves: Iterable[Move | str] | Move | str,
        path: str | Path,
        *,
        image_size: int = RENDER_SIZE,
        rotation: str = '',
        distance: float = 0.0,
        palette: str = '',
        mode: str = '',
        mask: CubeDisplayMask = '',
        look: Look = DEFAULT_LOOK,
        frame_rate: float = FRAME_RATE,
        duration: float = MOVE_DURATION,
        loop: int = ANIMATION_LOOP,
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
    encoder can assemble.

    Args:
        cube: The cube to play the algorithm on.
        moves: The algorithm to play.
        path: Where the animation is written.
        image_size: Width and height of the images, in pixels.
        rotation: Camera rotation string, such as ``y45x-34``. Empty for
            the library default.
        distance: Distance from the camera to the cube. Zero for the
            library default.
        palette: Name of the color palette. Empty for the default one.
        mode: Display preset presetting the mask and the orientation,
            such as ``oll`` or ``f2l``.
        mask: Display mask, one code per facelet. Overrides the mask the
            mode would have set.
        look: How the light falls on the cube, antialiasing included.
        frame_rate: Frames per second the animation plays at.
        duration: How long a single quarter turn lasts, in seconds. A
            half turn is given ``HALF_TURN_FACTOR`` times that.
        loop: How many times the animation plays, zero looping forever.

    Returns:
        The paths written to: the GIF alone, or one per frame.

    """
    animation = Animation(
        cube, moves,
        palette=palette, mode=mode, mask=mask, duration=duration,
    )

    frames = render_frames(
        animation.play(frame_rate),
        OrbitCamera.from_rotation(
            rotation, distance, animation.geometry.radius,
        ),
        image_size=image_size,
        look=look,
    )

    size = (image_size, image_size)

    if not has_pillow():
        return write_frames(path, frames, size)

    return [write_gif(path, frames, size, frame_rate=frame_rate, loop=loop)]
