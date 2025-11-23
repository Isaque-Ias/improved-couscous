#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;

vec4 mix_rgb(vec4 color_a, vec4 color_b, float t) {
    vec3 rgb = mix(color_a.rgb, color_b.rgb, t);
    return vec4(rgb, color_a.a);
}

void main()
{
    vec4 texColor = texture(u_texture, v_texcoord);
    vec4 defColor = texColor * vec4(v_color, 1.0);
    vec4 dark_color = vec4(10.0 / 255.0, 10.0 / 255.0, 24.0 / 255.0, 1.0);
    FragColor = mix_rgb(defColor, dark_color, 0.0);
}
