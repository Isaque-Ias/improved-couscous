#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec2 u_player;
uniform vec2 u_cam;
uniform vec2 u_cam_scale;
uniform vec2 u_screen;
uniform int u_time;

vec4 mix_rgb(vec4 color_a, vec4 color_b, float t) {
    vec3 rgb = mix(color_a.rgb, color_b.rgb, t);
    return vec4(rgb, color_a.a);
}

void main()
{
    vec4 texColor = texture(u_texture, v_texcoord);
    FragColor = texColor * vec4(v_color, 1.0);
    if (distance(vec2(round(gl_FragCoord.x / 5.0) * 5.0, round(gl_FragCoord.y * 2.0 / 5.0) * 5.0), vec2(((u_player.x - u_cam.x) - u_screen.x / 2.0) * u_cam_scale.x + u_screen.x / 2.0, ((u_player.y - u_cam.y) - u_screen.y / 2.0) * -u_cam_scale.y * 2 + u_screen.y / 2.0 * 2)) <= 8 * u_cam_scale.x) {
        FragColor = mix_rgb(FragColor, vec4(0.0,0.0,0.0,1.0), 0.3);
    }
}