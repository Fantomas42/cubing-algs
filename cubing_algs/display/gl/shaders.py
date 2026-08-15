"""
GLSL sources of the GPU rendering backend.

One program draws the whole cube: every cubie shares the same mesh and
comes as an instance carrying its model matrix and the six colors of its
sides. A vertex knows which side it belongs to, so the shader only has to
index the colors of its instance.

A second program draws the ball core, the sphere filling the middle of
the cube. A third, much smaller one draws the three axes of the grid,
which the viewer shows on demand. Both exist apart because the program of
the cube is instanced, lit against the local frame of a cubie and
scaleless: nothing in it can draw a segment, and its groove occlusion
reads the position of a fragment inside a box.

The look is entirely driven by uniforms, so that two variants can be
compared within a single run: every one of them comes from a ``Look``.
Colors never do: a sticker keeps the color its palette gives it, exactly
as in the SVG backend, and the shading only says how the light falls on
it.
"""
from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED

# The version the shaders are written against, taken from the version
# the context is created with, so that both can never drift apart.
GLSL_VERSION = f'#version { GL_VERSION_REQUIRED }'

# Face index of a vertex of the plastic, matching geometry.BODY_FACE.
GLSL_BODY_FACE = -1

# Number of colors held by the first of the two color matrices.
GLSL_COLOR_SPLIT = 3

VERTEX_SHADER = GLSL_VERSION + f"""

uniform mat4 view_projection;
uniform mat4 world;
uniform vec3 plastic_color;
uniform float cubie_half;

in vec3 in_position;
in vec3 in_normal;
in int in_face;

in mat4 in_model;
in mat3 in_colors_low;
in mat3 in_colors_high;

flat out vec3 v_color;
flat out vec3 v_normal;
flat out int v_face;
out vec3 v_local;
out vec3 v_world;

void main()
{{
    vec3 color = plastic_color;

    if (in_face > { GLSL_BODY_FACE }) {{
        color = in_face < { GLSL_COLOR_SPLIT }
            ? in_colors_low[in_face]
            : in_colors_high[in_face - { GLSL_COLOR_SPLIT }];
    }}

    v_color = color;
    v_face = in_face;

    // Where the cubie stands, and where the whole cube stands: the
    // second one is the identity unless something outside holds the
    // cube, a bluetooth sensor reporting how it is being turned.
    mat4 model = world * in_model;

    // The model matrix is a rotation and a translation, never a scale,
    // so it transforms a normal as it transforms a direction.
    v_normal = mat3(model) * in_normal;

    // Where the fragment stands inside its own cubie, from -1 to 1 on
    // each axis: this is what tells how deep in a groove it sits, and
    // it follows the piece when the piece turns.
    v_local = in_position / cubie_half;

    vec4 position = model * vec4(in_position, 1.0);
    v_world = position.xyz;

    gl_Position = view_projection * position;
}}
"""

FRAGMENT_SHADER = GLSL_VERSION + f"""

uniform vec3 light_direction;
uniform vec3 camera_position;
uniform float ambient;
uniform float gamma;
uniform float groove_occlusion;
uniform float groove_falloff;
uniform float rim_strength;
uniform float rim_power;
uniform float specular_strength;
uniform float specular_power;
uniform float sticker_grain;

flat in vec3 v_color;
flat in vec3 v_normal;
flat in int v_face;
in vec3 v_local;
in vec3 v_world;

out vec4 f_color;

// Scale the local coordinates are sampled at to draw the grain: fine
// enough to read as a texture, coarse enough to survive downsampling.
const float GRAIN_SCALE = 48.0;

/*
 * How deep in a groove a fragment sits, from 0 in the middle of a face
 * to 1 along an edge or a corner of its cubie.
 *
 * The second largest of the three local coordinates says it: on the
 * surface of a piece one of them is always extremal, and a second one
 * only comes close near an edge. No buffer, no sampling, no second
 * pass: the ambient occlusion of a cube is a matter of geometry.
 */
float groove(vec3 local)
{{
    vec3 reach = abs(local);

    float widest = max(reach.x, max(reach.y, reach.z));
    float narrowest = min(reach.x, min(reach.y, reach.z));

    return clamp(reach.x + reach.y + reach.z - widest - narrowest, 0.0, 1.0);
}}

// Pseudo random value in [0, 1], stable for a point of a cubie.
float hash(vec3 point)
{{
    return fract(
        sin(dot(point, vec3(12.9898, 78.233, 37.719))) * 43758.5453
    );
}}

void main()
{{
    vec3 normal = normalize(v_normal);
    vec3 view = normalize(camera_position - v_world);
    vec3 half_vector = normalize(light_direction + view);

    float diffuse = max(dot(normal, light_direction), 0.0);
    float occlusion = 1.0 - groove_occlusion
        * pow(groove(v_local), groove_falloff);

    float rim = rim_strength
        * pow(1.0 - max(dot(normal, view), 0.0), rim_power);

    vec3 color = pow(v_color, vec3(gamma));
    float gloss = 0.0;

    // A sticker is glossy and printed, the plastic underneath is
    // neither. Letting the highlight reach the body would light the
    // chamfers buried between two pieces, and a lone lit facet in the
    // middle of a groove reads as a defect rather than as gloss.
    if (v_face > { GLSL_BODY_FACE }) {{
        color *= 1.0 + sticker_grain
            * (2.0 * hash(v_local * GRAIN_SCALE + float(v_face)) - 1.0);

        gloss = specular_strength
            * pow(max(dot(normal, half_vector), 0.0), specular_power);
    }}

    vec3 lit = color * (
        (ambient + (1.0 - ambient) * diffuse) * occlusion + rim
    ) + gloss * occlusion * occlusion;

    f_color = vec4(pow(max(lit, 0.0), vec3(1.0 / gamma)), 1.0);
}}
"""

# The second program of the backend: the ball core, the inside of the
# cube. It shades with the same ambient and diffuse terms as the cube, so
# a single light lights them both, but with none of what belongs to a
# piece: no groove occlusion, whose local frame is that of a box, no rim,
# no gloss, no grain. A core is a matte solid seen through a hole.
CORE_VERTEX_SHADER = GLSL_VERSION + """

uniform mat4 view_projection;
uniform mat4 world;

in vec3 in_position;
in vec3 in_normal;

out vec3 v_normal;

void main()
{
    v_normal = mat3(world) * in_normal;

    gl_Position = view_projection * world * vec4(in_position, 1.0);
}
"""

CORE_FRAGMENT_SHADER = GLSL_VERSION + """

uniform vec3 light_direction;
uniform vec3 core_color;
uniform float ambient;
uniform float gamma;

in vec3 v_normal;

out vec4 f_color;

void main()
{
    float diffuse = max(dot(normalize(v_normal), light_direction), 0.0);

    vec3 lit = pow(core_color, vec3(gamma))
        * (ambient + (1.0 - ambient) * diffuse);

    f_color = vec4(pow(max(lit, 0.0), vec3(1.0 / gamma)), 1.0);
}
"""

# The third, and last, program of the backend: the three axes of
# the grid, drawn as segments when the viewer is asked for them. It takes
# no light at all, an axis being a marker and not a solid, and it shares
# the ``world`` uniform of the cube so that the axes follow whatever
# holds it.
AXES_VERTEX_SHADER = GLSL_VERSION + """

uniform mat4 view_projection;
uniform mat4 world;

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;

void main()
{
    v_color = in_color;

    gl_Position = view_projection * world * vec4(in_position, 1.0);
}
"""

AXES_FRAGMENT_SHADER = GLSL_VERSION + """

in vec3 v_color;

out vec4 f_color;

void main()
{
    f_color = vec4(v_color, 1.0);
}
"""
