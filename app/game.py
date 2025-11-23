from entity import Entity
from entity import EntityTools as et
from pygame.locals import *
from inputting import Input
from PIL import Image
import pygame as pg
import random
from shaders import ShaderObject
from transformations import Transformation

def pygame_surface_to_pil(surface):
    data = pg.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()
    return Image.frombytes("RGBA", (width, height), data)

def build_chunk_atlas(tiles, tile_w, tile_h):
    cols = 8
    rows = 8
    atlas_w = cols * tile_w
    atlas_h = rows * (tile_h + 1) - 1
    
    atlas = Image.new("RGBA", (atlas_w, atlas_h))

    for i, tile in enumerate(tiles):
        x_grid = (i % cols)
        y_grid = (i // cols)
        hh = (tile_h // 2 + 1)
        hw = tile_w // 2
        x = hw * x_grid + hw * y_grid
        y = hh * x_grid - hh * y_grid + atlas_h // 2 - tile_h // 2
        atlas.paste(pygame_surface_to_pil(tile), (x, y), pygame_surface_to_pil(tile))

    return atlas

class Map(Entity):
    chunks = {}
    def __init__(self):
        super().__init__((0, 0), None, has_layer=False)
        self.time = 0
        self.time_cap = 24000
        
        grass0_surf = pg.image.load(f"app\\sources\\grass0.png").convert_alpha()
        grass1_surf = pg.image.load(f"app\\sources\\grass1.png").convert_alpha()
        sand_surf = pg.image.load(f"app\\sources\\sand.png").convert_alpha()

        for x in range(3):
            for y in range(3):
                chunk_sprites = [random.choice([grass0_surf, grass1_surf]) for _ in range(64)]
                atlas_tex = build_chunk_atlas(chunk_sprites, 32, 15)
                self.chunks[f"{x},{y}"] = ShaderObject.add_texture(atlas_tex)

    def tick(self):
        self.time += 1
        if self.time >= self.time_cap:
            self.time = 0

    def draw(self):
        for key in self.chunks.keys():
            chunk_x, chunk_y = map(int, key.split(","))

            hw = 32 * 8 // 2
            hh = 15 * 8 // 2 + .5
            chunk_draw_x = hw * chunk_x + hw * chunk_y
            chunk_draw_y = hh * chunk_x - hh * chunk_y

            et.draw_image(self.chunks[key], (chunk_draw_x, chunk_draw_y), (32 * 8 + 0.1, 15 * 8 + 0.1), 0)

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, "player", (16, 16), layer=30)
        self.cam = et.get_cam("main")
        self.z = 0
        self.grv = 0.2
        self.speed = .3
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0

        vh, vw = et.get_screen_size()
        self.cam_follow_pos = [(self.x - vh / 2), (self.y - vw / 2)]

    def tick(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.z += self.vel_z

        self.vel_x *= 0.75
        self.vel_y *= 0.75

        if self.z < 0:
            self.z = 0
        else:
            self.vel_z -= self.grv

        if Input.get_press(K_w):
            self.vel_y -= self.speed * 0.5
        if Input.get_press(K_a):
            self.vel_x -= self.speed
        if Input.get_press(K_s):
            self.vel_y += self.speed * 0.5
        if Input.get_press(K_d):
            self.vel_x += self.speed
        if Input.get_press(K_SPACE) and self.z == 0:
            self.vel_z = 2

        self.set_layer(self.y + 24)

        vh, vw = et.get_screen_size()
        self.cam_follow_pos[0] -= ((self.cam_follow_pos[0]) - (self.x - vh / 2)) / 5
        self.cam_follow_pos[1] -= ((self.cam_follow_pos[1]) - (self.y - vw / 2)) / 5
        self.cam.set_pos(self.cam_follow_pos)

    def get_mvp(self):
        return Transformation.affine_transform((self.x, self.y - self.z - 3), (self.width, self.height), self.angle)
    
"""
tree algo:
tree trunk is base. Generate tree like a tree.
root is tree trunk
second layer is thich trunk, with lots of varieties. They include properties and enter inclination, exit inclination, placement point and placeable point and exit thickness and the exiting values (exit inclination and placeable point are meant to be a list for Y shaped trunks.)
last layer is thin trunks for thin exit layers. They have properties such as Must end, enter and exit inclination, placement and placeable points.
Every trunk also has a brach point with branch direction for future branch placement.
The final leaf layer is the tree top, for leaf sprites. They are placed in the leaf nodes of trees.
tree algorithm works as WFC.
"""