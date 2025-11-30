#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec2 u_player;
uniform vec2 u_cam_scale;
uniform vec2 u_screen;
uniform vec4 u_time_color;
uniform vec4 u_lights[128];
uniform vec3 u_lights_color[128];
uniform int u_count_lights;

vec4 mix_rgb(vec4 color_a, vec4 color_b, float t) {
    vec3 rgb = mix(color_a.rgb, color_b.rgb, t);
    return vec4(rgb, color_a.a);
}

vec4 interp(vec4 color_a, vec4 color_b, float t, float min_v, float max_v) {
    return mix_rgb(color_a, color_b, max(min_v, min(max_v, t)));
}

void main() {
    vec4 texColor = texture(u_texture, v_texcoord);
    vec4 Original = texColor * vec4(v_color, 1.0);
    FragColor = interp(Original, vec4(u_time_color.x, u_time_color.y, u_time_color.z, 1.0), u_time_color.w, 0.0, 1.0);
    for (int i = 0; i < u_count_lights; i ++) {
        float radius = u_lights[i].w * u_cam_scale.x;
        float d = distance(vec2(
            gl_FragCoord.x,
            gl_FragCoord.y * 32 / 15), vec2(
            u_lights[i].x * u_cam_scale.x - (u_player.x + u_screen.x / 2) * u_cam_scale.x + u_screen.x / 2,
            (-u_lights[i].y * u_cam_scale.y + (u_player.y + u_screen.y / 2) * u_cam_scale.y + u_screen.y / 2) * 32 / 15
        ));
        float x = clamp(d / radius, 0.0, 1.0);
        float I = exp(-5.0 * x) - exp(-5.0);
        I /= 1.0 - exp(-5.0);
        vec4 light_color = vec4(max(FragColor.r, Original.r * u_lights_color[i].x), max(FragColor.g, Original.g * u_lights_color[i].y), max(FragColor.b, Original.b * u_lights_color[i].z), Original.a);
        FragColor = mix(FragColor, light_color, I);
    }
}