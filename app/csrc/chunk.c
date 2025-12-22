#include <math.h>
#include <stdint.h>

#define SPRITE_W 32
#define SPRITE_H 15
#define PERLIN_GRID 32

static const float gradients[8][2] = {
    { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 },
    { 0.7071f, 0.7071f }, { -0.7071f, 0.7071f },
    { 0.7071f, -0.7071f }, { -0.7071f, -0.7071f }
};

static const float int_order[4][2] = {
    { 0, 0 }, { 1, 0 }, { 0, 1 }, { 1, 1 },
};

static inline uint32_t splitmix32(uint32_t x) {
    x += 0x9e3779b9;
    x = (x ^ (x >> 16)) * 0x85ebca6b;
    x = (x ^ (x >> 13)) * 0xc2b2ae35;
    return x ^ (x >> 16);
}

static inline uint32_t hash2(uint32_t x, uint32_t y, uint32_t seed) {
    uint32_t h = x;
    h ^= splitmix32(y + seed);
    return splitmix32(h);
}

static inline const uint32_t*
get_sprite(const uint32_t* atlas, int id) {
    return atlas + id * SPRITE_W * SPRITE_H;
}

static inline void
blit_sprite(
    uint32_t* dst, int dw, int dh,
    const uint32_t* src,
    int dx, int dy
) {
    for (int y = 0; y < SPRITE_H; y++) {
        int ty = dy + y;
        if ((unsigned)ty >= (unsigned)dh) continue;

        uint32_t* drow = dst + ty * dw;
        const uint32_t* srow = src + y * SPRITE_W;

        for (int x = 0; x < SPRITE_W; x++) {
            int tx = dx + x;
            if ((unsigned)tx >= (unsigned)dw) continue;

            uint32_t p = srow[x];
            if (p >> 24) {
                drow[tx] = p;
            }
        }
    }
}

static inline void
iso_transform(int gx, int gy, int* sx, int* sy) {
    *sx = (gx + gy) * (SPRITE_W / 2);
    *sy = (gx - gy) * (SPRITE_H / 2 + 1);
}

static inline void table_vec2(uint32_t h, float* x, float* y) {
    int i = h & 7;
    *x = gradients[i][0];
    *y = gradients[i][1];
}

static inline float dot2(float gx, float gy, float dx, float dy) {
    return gx * dx + gy * dy;
}

static inline float fade(float t) {
    return t * t * t * (t * (t * 6 - 15) + 10);
}

static inline float lerp(float a, float b, float t) {
    return a + t * (b - a);
}

static inline float perlin2(
    int seed,
    int x, int y,
    float scale
) {
    float fx = x * scale;
    float fy = y * scale;

    int x0 = (int)floorf(fx);
    int y0 = (int)floorf(fy);

    float dx = fx - x0;
    float dy = fy - y0;

    float dots[4];

    for (int i = 0; i < 4; i++) {
        int cx0 = (int)int_order[i][0];
        int cy0 = (int)int_order[i][1];

        uint32_t h = splitmix32(
            (x0 + cx0) * 0x1f123bb5u ^
            (y0 + cy0) * 0x9e3779b9u ^
            seed
        );

        float gxv, gyv;
        table_vec2(h, &gxv, &gyv);

        float ox = dx - cx0;
        float oy = dy - cy0;

        dots[i] = gxv * ox + gyv * oy;
    }

    float u = fade(dx);
    float v = fade(dy);

    float nx0 = lerp(dots[0], dots[1], u);
    float nx1 = lerp(dots[2], dots[3], u);

    return lerp(nx0, nx1, v);
}

static inline float fractal_perlin2(
    int seed,
    int x, int y,
    int octaves,
    float scale,
    float persistence,
    float* out_amplitude
) {
    float value = 0.0f;
    float amplitude = 1.0f;
    float frequency = scale;

    float max_amplitude = 0.0f;

    for (int i = 0; i < octaves; i++) {
        value += perlin2(seed + i * 1013, x, y, frequency) * amplitude;

        max_amplitude += amplitude;
        amplitude *= persistence;
        frequency *= 2.0f;
    }

    if (out_amplitude) {
        *out_amplitude = max_amplitude;
    }

    return value;
}

static inline int
get_block(int seed, int gx, int gy, int cw, int ch, int cx, int cy) {
    int total_x = gx + cx;
    int total_y = gy + cy;

    int grid_x = (total_x % PERLIN_GRID + PERLIN_GRID) % PERLIN_GRID;
    int grid_y = (total_y % PERLIN_GRID + PERLIN_GRID) % PERLIN_GRID;

    int perlin_x = total_x / PERLIN_GRID;
    int perlin_y = total_y / PERLIN_GRID;

    float amp;
    float n = fractal_perlin2(
        seed,
        total_x,
        total_y,
        3,
        0.05f,
        0.5f,
        &amp
    );

    n /= amp;

    int sprite;
    if (n < -0.0f) sprite = 0;
    else           sprite = 2;

    return sprite;
}

__declspec(dllexport)
void generate_chunk(
    uint32_t* chunk,
    int cw, int ch,
    int cx, int cy,
    const uint32_t* atlas,
    int seed,
    int sprite_count,
    int grid_w, int grid_h
) {
    int origin_x = 0;
    int origin_y = ch / 2 - SPRITE_H / 2;

    for (int gy = 0; gy < grid_h; gy++) {
        for (int gx = 0; gx < grid_w; gx++) {
            
            int sprite_id = get_block(seed, gx, gy, cw, ch, cx * grid_w, cy * grid_h);
            const uint32_t* sprite = get_sprite(atlas, sprite_id);

            int sx, sy;
            iso_transform(gx, gy, &sx, &sy);

            blit_sprite(
                chunk, cw, ch,
                sprite,
                origin_x + sx,
                origin_y + sy
            );
        }
    }
}
