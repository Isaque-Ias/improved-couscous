#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec2 u_player;
uniform vec2 u_cam_pos;
uniform vec2 u_cam_scale;
uniform vec2 u_screen;
uniform vec3 u_time_color;
uniform vec4 u_lights[128];
uniform vec3 u_lights_color[128];
uniform int u_count_lights;

void main() {
    vec4 texColor = texture(u_texture, v_texcoord);
    vec4 Original = texColor * vec4(v_color, 1.0);
    
    FragColor = vec4(Original.r * u_time_color.x, Original.g * u_time_color.y, Original.b * u_time_color.z, Original.a);

    for (int i = 0; i < u_count_lights; i ++) {
        float radius = u_lights[i].w * u_cam_scale.x;
        float d = distance(vec2(
            gl_FragCoord.x,
            gl_FragCoord.y * 32 / 15), vec2(
            u_lights[i].x * u_cam_scale.x - (u_cam_pos.x + u_screen.x / 2) * u_cam_scale.x + u_screen.x / 2,
            (-u_lights[i].y * u_cam_scale.y + (u_cam_pos.y + u_screen.y / 2) * u_cam_scale.y + u_screen.y / 2) * 32 / 15
        ));
        float x = clamp(d / radius, 0.0, 1.0);
        float I = exp(-5.0 * x) - exp(-5.0);
        I /= 1.0 - exp(-5.0);
        vec4 light_color = vec4(max(FragColor.r, Original.r * u_lights_color[i].x), max(FragColor.g, Original.g * u_lights_color[i].y), max(FragColor.b, Original.b * u_lights_color[i].z), Original.a);
        FragColor = mix(FragColor, light_color, I);
    }
}