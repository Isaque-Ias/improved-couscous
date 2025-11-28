#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec4 u_color;

vec4 mix_rgb(vec4 color_a, vec4 color_b, float t) {
    vec3 rgb = mix(color_a.rgb, color_b.rgb, t);
    return vec4(rgb, color_a.a);
}

void main()
{
    vec4 texColor = texture(u_texture, v_texcoord);
    FragColor = texColor * vec4(v_color, 1.0);
    FragColor = vec4(FragColor.r * u_color.x, FragColor.g * u_color.y, FragColor.b * u_color.z, FragColor.a * u_color.w);
}
