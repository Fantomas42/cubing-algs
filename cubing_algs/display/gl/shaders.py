"""
GLSL sources of the GPU rendering backend.

One program draws the whole cube: every cubie shares the same mesh and
comes as an instance carrying its model matrix and the six colors of its
sides. A vertex knows which side it belongs to, so the shader only has
to index the colors of its instance.

Shading is deliberately flat and mostly ambient. A sticker must keep the
color its palette gives it, exactly as in the SVG backend; the diffuse
part is only there to tell the visible faces apart. The look itself is
the matter of a later step.
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
uniform vec3 plastic_color;

in vec3 in_position;
in vec3 in_normal;
in int in_face;

in mat4 in_model;
in mat3 in_colors_low;
in mat3 in_colors_high;

flat out vec3 v_color;
flat out vec3 v_normal;

void main()
{{
    vec3 color = plastic_color;

    if (in_face > { GLSL_BODY_FACE }) {{
        color = in_face < { GLSL_COLOR_SPLIT }
            ? in_colors_low[in_face]
            : in_colors_high[in_face - { GLSL_COLOR_SPLIT }];
    }}

    v_color = color;

    // The model matrix is a rotation and a translation, never a scale,
    // so it transforms a normal as it transforms a direction.
    v_normal = mat3(in_model) * in_normal;

    gl_Position = view_projection * in_model * vec4(in_position, 1.0);
}}
"""

FRAGMENT_SHADER = GLSL_VERSION + """

uniform vec3 light_direction;
uniform float ambient;

flat in vec3 v_color;
flat in vec3 v_normal;

out vec4 f_color;

void main()
{
    float diffuse = max(dot(normalize(v_normal), light_direction), 0.0);

    f_color = vec4(v_color * (ambient + (1.0 - ambient) * diffuse), 1.0);
}
"""
