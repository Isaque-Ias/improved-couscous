#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec4 u_time_color;
uniform vec4 u_color;

void main() {
    vec4 texColor = texture(u_texture, v_texcoord);
    vec4 Original = texColor * vec4(v_color, 1.0);
    FragColor = Original;
    FragColor = vec4(FragColor.r * u_color.x, FragColor.g * u_color.y, FragColor.b * u_color.z, FragColor.a * u_color.w);
}