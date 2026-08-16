"""
Renderer of the GPU rendering backend.

Consumes a ``Scene`` and a camera, produces pixels. The mesh of a cubie
is uploaded once, the cubies come as instances, and the whole cube is
drawn in a single instanced call whatever its size. The ball core comes
first, in a call of its own: it is the inside of the cube, hidden by the
pieces until a hole is dug in them.

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
from cubing_algs.display.gl.constants import CORE_COLOR
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import RENDER_SAMPLES
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.geometry import AXES_VERTEX_ATTRIBUTES
from cubing_algs.display.gl.geometry import AXES_VERTEX_FORMAT
from cubing_algs.display.gl.geometry import CORE_VERTEX_ATTRIBUTES
from cubing_algs.display.gl.geometry import CORE_VERTEX_FORMAT
from cubing_algs.display.gl.geometry import VERTEX_ATTRIBUTES
from cubing_algs.display.gl.geometry import VERTEX_FORMAT
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import build_core_mesh
from cubing_algs.display.gl.geometry import core_radius
from cubing_algs.display.gl.geometry import pack_axes
from cubing_algs.display.gl.geometry import pack_core
from cubing_algs.display.gl.presentation import DEFAULT_PRESENTATION
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.scene import INSTANCE_ATTRIBUTES
from cubing_algs.display.gl.scene import INSTANCE_FORMAT
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.shaders import AXES_FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import AXES_VERTEX_SHADER
from cubing_algs.display.gl.shaders import CORE_FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import CORE_VERTEX_SHADER
from cubing_algs.display.gl.shaders import FRAGMENT_SHADER
from cubing_algs.display.gl.shaders import VERTEX_SHADER
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import Quat
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
class CoreRenderer:
    """
    The ball core, the sphere filling the middle of the cube.

    Owned by the ``Renderer`` of the cube rather than held next to it,
    as the axes are: the inside of a cube is not an option one turns on,
    so it must reach every path drawing the cube, the offscreen ones
    included.

    Bound to the radius it was built with, hence to a cube size, exactly
    as a ``Renderer`` is bound to a geometry.
    """

    context: 'moderngl.Context'
    program: 'moderngl.Program'
    vertex_buffer: 'moderngl.Buffer'
    index_buffer: 'moderngl.Buffer'
    vertex_array: 'moderngl.VertexArray'

    @classmethod
    def create(cls, context: 'moderngl.Context', radius: float) -> Self:
        """
        Build the renderer of a ball core.

        Args:
            context: The context owning the buffers and the program.
            radius: Radius of the core, as ``core_radius`` sizes it.

        Returns:
            A renderer ready to draw the core.

        """
        mesh = build_core_mesh(radius)

        program = context.program(
            vertex_shader=CORE_VERTEX_SHADER,
            fragment_shader=CORE_FRAGMENT_SHADER,
        )

        vertex_buffer = context.buffer(pack_core(mesh))
        index_buffer = context.buffer(mesh.pack_indices())

        return cls(
            context=context,
            program=program,
            vertex_buffer=vertex_buffer,
            index_buffer=index_buffer,
            vertex_array=context.vertex_array(
                program,
                [
                    (
                        vertex_buffer,
                        CORE_VERTEX_FORMAT,
                        *CORE_VERTEX_ATTRIBUTES,
                    ),
                ],
                index_buffer,
                index_element_size=INDEX_SIZE,
            ),
        )

    def draw(
            self,
            camera: OrbitCamera,
            look: Look = DEFAULT_LOOK,
            orientation: Quat = IDENTITY,
    ) -> None:
        """
        Draw the core into the framebuffer currently in use.

        Args:
            camera: The camera looking at the cube.
            look: How the light falls on it, the core taking its ambient
                and its gamma from the very same one.
            orientation: How the whole cube is held, which the core
                follows as the piece of it that it is.

        """
        import moderngl

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'world').write(orientation.to_matrix().pack())
        uniform(self.program, 'core_color').value = CORE_COLOR
        uniform(self.program, 'light_direction').value = Vec3(
            *look.light_direction,
        ).normalized()
        uniform(self.program, 'ambient').value = look.ambient
        uniform(self.program, 'gamma').value = look.gamma

        self.context.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.vertex_array.render()

    def release(self) -> None:
        """Give every GPU resource of the core back."""
        self.vertex_array.release()
        self.index_buffer.release()
        self.vertex_buffer.release()
        self.program.release()


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
    core: CoreRenderer

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
            core=CoreRenderer.create(context, core_radius(geometry.size)),
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
            orientation: Quat = IDENTITY,
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
            orientation: How the whole cube is held, on top of what the
                scene already places. The light stays where it is, as a
                lamp does when a cube turns under it.

        """
        import moderngl

        self.core.draw(camera, look, orientation)

        self.instance_buffer.write(scene.pack_instances())

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'world').write(orientation.to_matrix().pack())
        uniform(self.program, 'camera_position').value = camera.position
        uniform(self.program, 'plastic_color').value = scene.plastic
        uniform(self.program, 'cubie_half').value = scene.geometry.half

        self.write_look(look)

        self.context.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.vertex_array.render(instances=len(scene.instances))

    def release(self) -> None:
        """Give every GPU resource of the renderer back."""
        self.core.release()

        self.vertex_array.release()
        self.instance_buffer.release()
        self.index_buffer.release()
        self.vertex_buffer.release()
        self.program.release()


@dataclass(slots=True)
class AxesRenderer:
    """
    The three axes of the grid, drawn as colored segments.

    A marker rather than a solid: no light, no instance, no depth of its
    own. Bound to the length it was built with, hence to a cube size,
    exactly as a ``Renderer`` is bound to a geometry.
    """

    context: 'moderngl.Context'
    program: 'moderngl.Program'
    vertex_buffer: 'moderngl.Buffer'
    vertex_array: 'moderngl.VertexArray'

    @classmethod
    def create(cls, context: 'moderngl.Context', length: float) -> Self:
        """
        Build the renderer of the axes.

        Args:
            context: The context owning the buffer and the program.
            length: How far an axis reaches from the center of the cube,
                in world units.

        Returns:
            A renderer ready to draw the axes.

        """
        program = context.program(
            vertex_shader=AXES_VERTEX_SHADER,
            fragment_shader=AXES_FRAGMENT_SHADER,
        )

        vertex_buffer = context.buffer(pack_axes(length))

        return cls(
            context=context,
            program=program,
            vertex_buffer=vertex_buffer,
            vertex_array=context.vertex_array(
                program,
                [
                    (
                        vertex_buffer,
                        AXES_VERTEX_FORMAT,
                        *AXES_VERTEX_ATTRIBUTES,
                    ),
                ],
            ),
        )

    def draw(
            self,
            camera: OrbitCamera,
            orientation: Quat = IDENTITY,
    ) -> None:
        """
        Draw the axes into the framebuffer currently in use.

        The depth test is kept on, so that the half of an axis running
        inside the cube stays hidden by it: that is what tells which way
        an axis points rather than merely where it lies.

        Args:
            camera: The camera looking at them.
            orientation: How the whole cube is held, the axes being the
                ones of the cube and not the ones of the world.

        """
        import moderngl

        uniform(self.program, 'view_projection').write(
            camera.view_projection().pack(),
        )
        uniform(self.program, 'world').write(orientation.to_matrix().pack())

        self.context.enable_only(moderngl.DEPTH_TEST)

        self.vertex_array.render(moderngl.LINES)

    def release(self) -> None:
        """Give every GPU resource of the renderer back."""
        self.vertex_array.release()
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


def render_frames(
        scenes: Iterable[Scene],
        camera: OrbitCamera,
        presentation: Presentation = DEFAULT_PRESENTATION,
        *,
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
        presentation: The picture to make. Only the image size, the look
            and the orientation are read here: the palette, the mode and
            the mask were spent building the scenes.
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

    look = presentation.look

    target = OffscreenTarget.create(used, presentation.size, look.samples)
    renderer = Renderer.create(used, ordered[0].geometry)

    try:
        frames: list[bytes] = []

        for scene in ordered:
            target.use()
            renderer.draw(scene, camera, look, presentation.orientation)
            frames.append(target.read())

        return frames
    finally:
        renderer.release()
        target.release()

        if owned:
            used.release()


def render_scene(
        scene: Scene,
        camera: OrbitCamera,
        presentation: Presentation = DEFAULT_PRESENTATION,
        *,
        context: 'moderngl.Context | None' = None,
) -> bytes:
    """
    Render a scene offscreen, and read the pixels back.

    Args:
        scene: The cube to draw.
        camera: The camera looking at it.
        presentation: The picture to make, of which the image size, the
            look and the orientation are read.
        context: A context to draw with. A headless one is created, and
            released, when left out.

    Returns:
        The rows of RGBA pixels, bottom row first.

    """
    return render_frames(
        [scene],
        camera,
        presentation,
        context=context,
    )[0]
