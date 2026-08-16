"""
What a picture of a cube is made of, gathered in one object.

Framing, palette, mode, mask, image size, lighting and the way the cube
is held all describe the same thing: the picture to make. They used to
travel as seven arguments in a row, which is how the way a bluetooth
sensor holds a cube could reach ``Renderer.draw()`` and go no further.

The object is threaded whole through the pipeline, each layer reading
the fields that concern it: the pure layer takes the palette, the mode
and the mask, the camera takes the rotation and the distance, the GPU
layer takes the size, the look and the orientation. One vocabulary from
the CLI down to the draw call, and no function re-deriving what another
has already settled.

``Playback`` is the other half, and deliberately not the same object: it
says how an animation runs, not what a frame of it looks like.

Pure Python, no external dependency.
"""
from dataclasses import dataclass

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import ANIMATION_LOOP
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import Quat


@dataclass(frozen=True, slots=True)
class Presentation:
    """
    How a cube is turned into a picture.

    Every field has the default the library renders with, so that
    ``Presentation()`` is the plain picture and a variant is one
    ``dataclasses.replace()`` away.
    """

    palette: str = ''
    mode: str = ''
    mask: CubeDisplayMask = ''
    rotation: str = ''
    distance: float = 0.0
    image_size: int = RENDER_SIZE
    look: Look = DEFAULT_LOOK
    orientation: Quat = IDENTITY

    @property
    def size(self) -> tuple[int, int]:
        """
        Give the size of the image, the way moderngl asks for it.

        Returns:
            Width and height, in pixels.

        """
        return (self.image_size, self.image_size)

    def camera(self, radius: float, aspect: float = 1.0) -> OrbitCamera:
        """
        Build the camera framing a cube of a given size.

        The radius is the one of the geometry actually built, not the
        one of the box it is laid out in: the gap and the chamfer make a
        cube smaller than its box, by a share depending on its size.

        Args:
            radius: Radius of the bounding sphere of the scene.
            aspect: Width over height ratio of the viewport.

        Returns:
            A camera looking at the origin, framing the sphere exactly.

        """
        return OrbitCamera.from_rotation(
            self.rotation, self.distance, radius, aspect,
        )


@dataclass(frozen=True, slots=True)
class Playback:
    """
    How an animation runs, once every frame of it is known.

    Kept apart from ``Presentation``: a frame rate and a loop count say
    nothing about what a frame looks like, and a still image has no use
    for either.
    """

    frame_rate: float = FRAME_RATE
    duration: float = MOVE_DURATION
    loop: int = ANIMATION_LOOP


# The picture the library draws when it is asked for nothing in
# particular, and the pace it plays an animation at.
DEFAULT_PRESENTATION = Presentation()
DEFAULT_PLAYBACK = Playback()
