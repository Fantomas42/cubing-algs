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
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Self
from typing import cast

from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import AMBIENT_LIGHT
from cubing_algs.display.gl.constants import BACKGROUND_COLOR
from cubing_algs.display.gl.constants import LIGHT_DIRECTION
from cubing_algs.display.gl.constants import RENDER_SAMPLES
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.geometry import VERTEX_ATTRIBUTES
from cubing_algs.display.gl.geometry import VERTEX_FORMAT
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.scene import INSTANCE_ATTRIBUTES
from cubing_algs.display.gl.scene import INSTANCE_FORMAT
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.shaders import FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import VERTEX_SHADER
from cubing_algs.display.gl.transforms import Vec3

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

# Bytes of an index of the triangle buffer, packed as a 32 bit integer.
INDEX_SIZE = 4

# Number of channels read back from a framebuffer: RGBA, the alpha
# channel keeping the background transparent.
COLOR_CHANNELS = 4


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

    def draw(self, scene: Scene, camera: OrbitCamera) -> None:
        """
        Draw a scene into the framebuffer currently in use.

        The framebuffer is neither bound nor cleared here: a viewer and
        an offscreen render own theirs, and only they know what to do
        with it once the cube is drawn.

        Args:
            scene: The cube to draw.
            camera: The camera looking at it.

        """
        import moderngl

        self.instance_buffer.write(scene.pack_instances())

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'plastic_color').value = scene.plastic
        uniform(self.program, 'light_direction').value = Vec3(
            *LIGHT_DIRECTION,
        ).normalized()
        uniform(self.program, 'ambient').value = AMBIENT_LIGHT

        self.context.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.vertex_array.render(instances=len(scene.instances))

    def release(self) -> None:
        """Give every GPU resource of the renderer back."""
        self.vertex_array.release()
        self.instance_buffer.release()
        self.index_buffer.release()
        self.vertex_buffer.release()
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


def render_scene(
        scene: Scene,
        camera: OrbitCamera,
        *,
        image_size: int = RENDER_SIZE,
        samples: int = RENDER_SAMPLES,
        context: 'moderngl.Context | None' = None,
) -> bytes:
    """
    Render a scene offscreen, and read the pixels back.

    Args:
        scene: The cube to draw.
        camera: The camera looking at it.
        image_size: Width and height of the image, in pixels.
        samples: Samples of the multisampled framebuffer, zero to render
            without antialiasing.
        context: A context to draw with. A headless one is created, and
            released, when left out.

    Returns:
        The rows of RGBA pixels, bottom row first.

    """
    owned = context is None
    used = context or create_standalone_context()

    size = (image_size, image_size)
    target = OffscreenTarget.create(used, size, samples)
    renderer = Renderer.create(used, scene.geometry)

    try:
        target.use()
        renderer.draw(scene, camera)

        return target.read()
    finally:
        renderer.release()
        target.release()

        if owned:
            used.release()
