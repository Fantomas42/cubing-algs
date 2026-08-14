"""
Renderer of the GPU rendering backend.

Consumes a ``Scene`` and a camera, produces pixels. The mesh of a cubie
is uploaded once, the cubies come as instances, and the whole cube is
drawn in a single instanced call whatever its size.

Nothing here creates a context: the very same renderer draws into the
framebuffer of a window and into an offscreen one, which is the whole
point of the backend. moderngl is imported lazily, as everywhere else in
this sub-module.
"""
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Self
from typing import cast

from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import BACKGROUND_COLOR
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import RENDER_SAMPLES
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.geometry import CUBE_EXTENT
from cubing_algs.display.gl.geometry import VERTEX_ATTRIBUTES
from cubing_algs.display.gl.geometry import VERTEX_FORMAT
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.scene import INSTANCE_ATTRIBUTES
from cubing_algs.display.gl.scene import INSTANCE_FORMAT
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.shaders import FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import SHADOW_FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import SHADOW_VERTEX_SHADER
from cubing_algs.display.gl.shaders import VERTEX_SHADER
from cubing_algs.display.gl.transforms import Vec3

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

# Bytes of an index of the triangle buffer, packed as a 32 bit integer.
INDEX_SIZE = 4

# Number of channels read back from a framebuffer: RGBA, the alpha
# channel keeping the background transparent.
COLOR_CHANNELS = 4

# Height of the ground plane the contact shadow is laid on: the very
# bottom of the cube, which spans [-1, 1] whatever its size.
SHADOW_GROUND = -CUBE_EXTENT

# Corners of the ground quad, drawn as a triangle strip out of the
# vertex index alone, without any buffer to bind.
SHADOW_VERTICES = 4


def uniform(program: 'moderngl.Program', name: str) -> 'moderngl.Uniform':
    """
    Fetch a uniform of a program by name.

    Args:
        program: The program holding the uniform.
        name: Name of the uniform, as the shader declares it.

    Returns:
        The uniform, ready to be written to.

    """
    return cast('moderngl.Uniform', program[name])


@dataclass(slots=True)
class Renderer:
    """
    The GPU side of a cube: one program, one mesh, one instance buffer.

    A renderer is bound to a geometry, hence to a cube size, and can
    draw any scene built on it: changing the state of the cube, its
    palette or its mask only rewrites the instance buffer.
    """

    context: 'moderngl.Context'
    program: 'moderngl.Program'
    vertex_buffer: 'moderngl.Buffer'
    index_buffer: 'moderngl.Buffer'
    instance_buffer: 'moderngl.Buffer'
    vertex_array: 'moderngl.VertexArray'

    @classmethod
    def create(
            cls,
            context: 'moderngl.Context',
            geometry: CubeGeometry,
    ) -> Self:
        """
        Build the renderer of a cube geometry.

        Args:
            context: The context owning the buffers and the program.
            geometry: The mesh of a cubie and the cubies to place it on.

        Returns:
            A renderer ready to draw any scene of that geometry.

        """
        mesh = geometry.mesh

        program = context.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )

        vertex_buffer = context.buffer(mesh.pack_vertices())
        index_buffer = context.buffer(mesh.pack_indices())
        instance_buffer = context.buffer(
            reserve=len(geometry.cubies) * INSTANCE_SIZE,
            dynamic=True,
        )

        vertex_array = context.vertex_array(
            program,
            [
                (vertex_buffer, VERTEX_FORMAT, *VERTEX_ATTRIBUTES),
                (instance_buffer, INSTANCE_FORMAT, *INSTANCE_ATTRIBUTES),
            ],
            index_buffer,
            index_element_size=INDEX_SIZE,
        )

        return cls(
            context=context,
            program=program,
            vertex_buffer=vertex_buffer,
            index_buffer=index_buffer,
            instance_buffer=instance_buffer,
            vertex_array=vertex_array,
        )

    def write_look(self, look: Look) -> None:
        """
        Hand the look of the cube over to the fragment shader.

        Args:
            look: How the light falls on the cube.

        """
        uniform(self.program, 'light_direction').value = Vec3(
            *look.light_direction,
        ).normalized()

        for name in (
                'ambient', 'gamma',
                'groove_occlusion', 'groove_falloff',
                'rim_strength', 'rim_power',
                'specular_strength', 'specular_power',
                'sticker_grain',
        ):
            uniform(self.program, name).value = getattr(look, name)

    def draw(
            self,
            scene: Scene,
            camera: OrbitCamera,
            look: Look = DEFAULT_LOOK,
    ) -> None:
        """
        Draw a scene into the framebuffer currently in use.

        The framebuffer is neither bound nor cleared here: a viewer and
        an offscreen render own theirs, and only they know what to do
        with it once the cube is drawn.

        Args:
            scene: The cube to draw.
            camera: The camera looking at it.
            look: How the light falls on the cube.

        """
        import moderngl

        self.instance_buffer.write(scene.pack_instances())

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'camera_position').value = camera.position
        uniform(self.program, 'plastic_color').value = scene.plastic
        uniform(self.program, 'cubie_half').value = scene.geometry.half

        self.write_look(look)

        self.context.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.vertex_array.render(instances=len(scene.instances))

    def release(self) -> None:
        """Give every GPU resource of the renderer back."""
        self.vertex_array.release()
        self.instance_buffer.release()
        self.index_buffer.release()
        self.vertex_buffer.release()
        self.program.release()


@dataclass(slots=True)
class ShadowPlane:
    """
    The contact shadow of the cube, laid on the ground before it.

    A single quad, built by its own vertex shader out of the index of
    each corner: it owns a program and nothing else, no buffer at all.
    """

    context: 'moderngl.Context'
    program: 'moderngl.Program'
    vertex_array: 'moderngl.VertexArray'

    @classmethod
    def create(cls, context: 'moderngl.Context') -> Self:
        """
        Build the shadow plane.

        Args:
            context: The context owning the program.

        Returns:
            A shadow plane ready to be drawn.

        """
        program = context.program(
            vertex_shader=SHADOW_VERTEX_SHADER,
            fragment_shader=SHADOW_FRAGMENT_SHADER,
        )

        return cls(
            context=context,
            program=program,
            vertex_array=context.vertex_array(program, []),
        )

    def draw(self, camera: OrbitCamera, look: Look = DEFAULT_LOOK) -> None:
        """
        Lay the shadow on the ground.

        Drawn first, without any depth test: the cube is opaque and
        covers whatever part of the shadow it stands on.

        Args:
            camera: The camera looking at the cube.
            look: How dark and how soft the shadow is.

        """
        import moderngl

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'ground').value = SHADOW_GROUND
        uniform(self.program, 'extent').value = look.shadow_extent
        uniform(self.program, 'opacity').value = look.shadow_opacity
        uniform(self.program, 'inner').value = look.shadow_inner
        uniform(self.program, 'softness').value = look.shadow_softness

        self.context.enable_only(moderngl.BLEND)

        self.vertex_array.render(
            moderngl.TRIANGLE_STRIP,
            vertices=SHADOW_VERTICES,
        )

    def release(self) -> None:
        """Give every GPU resource of the shadow back."""
        self.vertex_array.release()
        self.program.release()


@dataclass(slots=True)
class OffscreenTarget:
    """
    A framebuffer rendered to without any window.

    Multisampling cannot be read back directly, so a second, plain
    framebuffer is kept to resolve the samples into before reading.
    """

    framebuffer: 'moderngl.Framebuffer'
    resolved: 'moderngl.Framebuffer'
    size: tuple[int, int]

    @classmethod
    def create(
            cls,
            context: 'moderngl.Context',
            size: tuple[int, int],
            samples: int = RENDER_SAMPLES,
    ) -> Self:
        """
        Build an offscreen framebuffer of a given size.

        Args:
            context: The context owning the framebuffers.
            size: Width and height of the image, in pixels.
            samples: Samples of the multisampled framebuffer, clamped to
                what the context supports. Zero disables antialiasing.

        Returns:
            A target ready to be drawn into.

        """
        resolved = context.simple_framebuffer(size, COLOR_CHANNELS)
        samples = min(samples, context.max_samples)

        if not samples:
            return cls(framebuffer=resolved, resolved=resolved, size=size)

        return cls(
            framebuffer=context.framebuffer(
                context.renderbuffer(size, COLOR_CHANNELS, samples=samples),
                context.depth_renderbuffer(size, samples=samples),
            ),
            resolved=resolved,
            size=size,
        )

    def use(
            self,
            background: tuple[float, float, float, float] = BACKGROUND_COLOR,
    ) -> None:
        """
        Make the target current and clear it.

        Args:
            background: Color the framebuffer is cleared with, alpha
                included.

        """
        self.framebuffer.use()
        self.framebuffer.clear(color=background)

    def read(self) -> bytes:
        """
        Read the pixels of the target back.

        Returns:
            The rows of RGBA pixels, the first one being the bottom of
            the image, as OpenGL stores them.

        """
        if self.framebuffer is not self.resolved:
            self.framebuffer.ctx.copy_framebuffer(
                self.resolved,
                self.framebuffer,
            )

        return self.resolved.read(components=COLOR_CHANNELS)

    def release(self) -> None:
        """Give every GPU resource of the target back."""
        if self.framebuffer is not self.resolved:
            self.framebuffer.release()

        self.resolved.release()


@dataclass(slots=True)
class ScenePainter:
    """
    Everything drawing a cube takes, held between two frames.

    A program, its buffers and the shadow plane: building them is worth
    several frames of drawing, so an animation builds them once and a
    single image pays for them once too.
    """

    renderer: Renderer
    shadow: ShadowPlane | None

    @classmethod
    def create(
            cls,
            context: 'moderngl.Context',
            geometry: CubeGeometry,
            look: Look = DEFAULT_LOOK,
    ) -> Self:
        """
        Build everything a series of frames of one cube needs.

        Args:
            context: The context owning the programs and the buffers.
            geometry: The mesh of a cubie and the cubies to place it on.
            look: How the light falls on the cube. Only whether it casts
                a shadow at all is read here.

        Returns:
            A painter ready to draw any scene of that geometry.

        """
        return cls(
            renderer=Renderer.create(context, geometry),
            shadow=ShadowPlane.create(context) if look.shadow_opacity else None,
        )

    def draw(
            self,
            scene: Scene,
            camera: OrbitCamera,
            look: Look = DEFAULT_LOOK,
    ) -> None:
        """
        Draw a whole frame into the framebuffer currently in use.

        The shadow first, on a ground the cube then hides most of, and
        the cube over it.

        Args:
            scene: The cube to draw.
            camera: The camera looking at it.
            look: How the light falls on the cube.

        """
        if self.shadow is not None:
            self.shadow.draw(camera, look)

        self.renderer.draw(scene, camera, look)

    def release(self) -> None:
        """Give every GPU resource of the painter back."""
        if self.shadow is not None:
            self.shadow.release()

        self.renderer.release()


def render_frames(
        scenes: Iterable[Scene],
        camera: OrbitCamera,
        *,
        image_size: int = RENDER_SIZE,
        look: Look = DEFAULT_LOOK,
        context: 'moderngl.Context | None' = None,
) -> list[bytes]:
    """
    Render a series of scenes offscreen, and read the pixels back.

    Every scene shares one context, one framebuffer and one program: a
    headless context alone costs more than the whole animation it would
    otherwise be created for.

    Args:
        scenes: The cubes to draw, all of the same geometry.
        camera: The camera looking at them.
        image_size: Width and height of the images, in pixels.
        look: How the light falls on the cube, antialiasing included.
        context: A context to draw with. A headless one is created, and
            released, when left out.

    Returns:
        One frame per scene, as rows of RGBA pixels, bottom row first.

    """
    ordered = list(scenes)
    if not ordered:
        return []

    owned = context is None
    used = context or create_standalone_context()

    target = OffscreenTarget.create(
        used,
        (image_size, image_size),
        look.samples,
    )
    painter = ScenePainter.create(used, ordered[0].geometry, look)

    try:
        frames: list[bytes] = []

        for scene in ordered:
            target.use()
            painter.draw(scene, camera, look)
            frames.append(target.read())

        return frames
    finally:
        painter.release()
        target.release()

        if owned:
            used.release()


def render_scene(
        scene: Scene,
        camera: OrbitCamera,
        *,
        image_size: int = RENDER_SIZE,
        look: Look = DEFAULT_LOOK,
        context: 'moderngl.Context | None' = None,
) -> bytes:
    """
    Render a scene offscreen, and read the pixels back.

    Args:
        scene: The cube to draw.
        camera: The camera looking at it.
        image_size: Width and height of the image, in pixels.
        look: How the light falls on the cube, antialiasing included.
        context: A context to draw with. A headless one is created, and
            released, when left out.

    Returns:
        The rows of RGBA pixels, bottom row first.

    """
    return render_frames(
        [scene],
        camera,
        image_size=image_size,
        look=look,
        context=context,
    )[0]
