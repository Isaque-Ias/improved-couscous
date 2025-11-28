#version 330 core

in vec3 v_color;
in vec2 v_texcoord;

out vec4 FragColor;

uniform sampler2D u_texture;
uniform vec2 u_cam;
uniform vec2 u_cam_scale;
uniform vec2 u_screen;
uniform int u_time;
uniform int u_time_cap;

vec4 mix_rgb(vec4 color_a, vec4 color_b, float t) {
    vec3 rgb = mix(color_a.rgb, color_b.rgb, t);
    return vec4(rgb, color_a.a);
}

float f_pi = 3.1415;

const int total_times = 7;

const vec4 times[total_times] = vec4[total_times](
    vec4(0.0, 0.0, 0.0, 0.95),
    vec4(0.0, 0.0, 0.0, 0.9),
    vec4(45.0 / 255.0, 90.0 / 255.0, 150.0 / 255.0, 0.2),
    vec4(1.0, 1.0, 1.0, 0.0),
    vec4(1.0, 1.0, 1.0, 0.0),
    vec4(250.0 / 255.0, 165.0 / 255.0, 45.0 / 255.0, 0.2),
    vec4(0.0, 0.0, 0.0, 0.9)
);

vec4 interp(vec4 color_a, vec4 color_b, float t, float min_v, float max_v) {
    return mix_rgb(color_a, color_b, max(min_v, min(max_v, t)));
}

float smoothstep(float t) {
    return t;
    //3.0 * t * t - 2.0 * t * t * t;
}

vec4 time_lerp(int time) {
    float t = float(time);

    int idx = int(floor(t * total_times / u_time_cap)) % total_times;
    vec4 a = times[idx];

    int next_idx = (idx + 1) % total_times;
    vec4 b = times[next_idx];

    float seg_t = (t * total_times / u_time_cap) - float(idx);

    seg_t = smoothstep(seg_t);

    return mix(a, b, seg_t);
}

void main()
{
    vec4 texColor = texture(u_texture, v_texcoord);
    FragColor = texColor * vec4(v_color, 1.0);
    vec4 color_lerp = time_lerp(u_time);
    FragColor = interp(FragColor, vec4(color_lerp.x, color_lerp.y, color_lerp.z, 1.0), color_lerp.w, 0.0, 1.0);
}