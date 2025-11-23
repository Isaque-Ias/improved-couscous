#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;

void main()
{
    vec4 texColor = texture(u_texture, v_texcoord);
    FragColor = texColor * vec4(v_color, 1.0);
    vec4 dark_color = vec4(98.0 / 255.0, 164.0 / 255.0, 242.0 / 255.0, 1.0);
    vec4 light_color = vec4(147.0 / 255.0, 205.0 / 255.0, 253.0 / 255.0, 1.0);
    FragColor = mix(light_color, dark_color, gl_FragCoord.y / 768.0);
}