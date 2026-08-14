"""
Public API of the GPU rendering backend.

Everything the rest of the library, the CLI and the outside world need,
in one place: build a scene, frame it, draw it, encode the result. The
modules underneath stay free of any glue.
"""
from typing import TYPE_CHECKING

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.renderer import render_scene
from cubing_algs.display.gl.scene import build_scene

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
) -> bytes:
    """
    Render a cube on the GPU, without any window.

    The framing is the one of the SVG backend: same rotation string,
    same distance, same palette, same modes and masks, so that both
    renderings of a cube can be compared side by side.

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

    Returns:
        The bytes of a PNG image, its background left transparent.

    """
    pixels = render_scene(
        build_scene(cube, palette, mode=mode, mask=mask),
        OrbitCamera.from_rotation(rotation, distance),
        image_size=image_size,
    )

    return encode_png(pixels, (image_size, image_size))
