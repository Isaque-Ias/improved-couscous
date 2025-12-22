from looping import GameLoop
from entity import Entity, EntityManager
from entity import EntityTools as et
from OpenGL.GL import *
from pygame.locals import *
from inputting import Input, InputListener
from PIL import Image
import pygame as pg
import random
from shaders import ShaderHandler
from client import Client
from host import Host
from pathlib import Path
from texture import Texture
from camera import Camera
from testing import Testing
import math
from math import cos
import numpy as np
import bisect
from game.chunk_generation import Chunk

CWD = Path.cwd()
SOURCES = CWD / "app" / "sources"
FONTS = CWD / "app" / "sources" / "fonts"
SHADERS = CWD / "app" / "shaders"

pg.font.init()

class Map(Entity):
    def __init__(self):
        super().__init__((0, 0), None)
        self.time = 7000
        self.time_cap = 24000
        self.time_vel = 1

        self._block_cache = {}
        self._perlin_cache = {}

        self.chunks = {}
        self.chunk_buffer = {}
        self.chunk_radius = 2
        self.chunk_size = 8
        self.t_x, self.t_y = 0, 0
        self.prune_job, self.chunk_job = None, None
        self.old_cam_size = 0

        self.times_r = [
            (0, .03, 0),
            (0.15, .03, 0),
            (0.24, 0.21, 2),
            (0.4, 0.8, 3),
            (0.66, 0.8, -3),
            (0.8, .18, -2),
            (0.9, .03, 0),
            (1, .03, 0),
        ]
        self.times_g = [
            (0, .03, 0),
            (0.15, .03, 0),
            (0.24, 0.4, 2),
            (0.4, 0.85, 3),
            (0.66, 0.7, -3),
            (0.8, .1, -2),
            (0.9, .03, 0),
            (1, .03, 0),
        ]
        self.times_b = [
            (0, .03, 0),
            (0.15, .03, 0),
            (0.24, 0.6, 2),
            (0.4, 0.9, 3),
            (0.66, 0.6, -3),
            (0.8, .05, -2),
            (0.9, .03, 0),
            (1, .03, 0),
        ]
        self.time_color = (1,1,1)

        self.seed = int(random.random() * 10000)

        self.shaders = ShaderHandler.get_shader_program("map")

    def get_chunk_coords(self, coords):
        w = 16
        h = 8
        t_x = coords[0] / w - ((coords[0] * h / w - coords[1]) / (2 * h))
        t_y = (coords[0] * h / w - coords[1]) / (2 * h)
        t_x = int((t_x - self.chunk_size // 2) // self.chunk_size) + 1
        t_y = int((t_y - self.chunk_size // 2) // self.chunk_size) + 1
        return t_x, t_y

    def tick(self):
        self.time += self.time_vel
        if self.time >= self.time_cap:
            self.time = 0
        self.time_color = self.time_spline(self.time)

        t_x, t_y = self.get_chunk_coords((player.x, player.y))

        self.update_chunks(t_x, t_y)

        self.t_x = t_x
        self.t_y = t_y
        
        cam_size = Camera.get_main_camera().get_scale()[0]
        if cam_size != self.old_cam_size:
            self.chunk_job = None
            self.prune_job = None
            self.chunk_buffer = {}
            self._block_cache = {}
        self.old_cam_size = cam_size

        self.chunk_size = 2
        while self.chunk_size <= 16 // cam_size:
            self.chunk_size *= 2
        self.chunk_radius = int(64 / (cam_size * self.chunk_size))

    def prune_chunks(self, t_x, t_y):
        remove = []
        for key in self.chunk_buffer.keys():
            key_x, key_y = key
            dif_x = abs(key_x - t_x)
            dif_y = abs(key_y - t_y)
            if dif_x > self.chunk_radius or dif_y > self.chunk_radius:
                remove.append(key)
        for key in remove:
            self.chunk_buffer.pop(key)

            ShaderHandler.remove_texture(key)
            yield

    def generate_chunk(self, t_x, t_y):
        diameter = (2 * self.chunk_radius + 1)

        screen_size = et.get_screen_size()
        cam = Camera.get_main_camera()
        cam_wid, cam_hei = cam.get_scale()
        view_wid, view_hei = (screen_size[0], screen_size[1])
        hw = 32 * self.chunk_size // 2
        hh = (15 + 1) * self.chunk_size // 2
        for idx in range(int(diameter ** 2)):
            x = (idx % diameter) - self.chunk_radius
            y = idx // diameter - self.chunk_radius
            key = (t_x + x, t_y + y)
            if key in self.chunk_buffer:
                continue

            chunk_x, chunk_y = t_x + x, t_y + y

            chunk_draw_x = hw * chunk_x + hw * chunk_y
            chunk_draw_y = hh * chunk_x - hh * chunk_y
            if abs(chunk_draw_x - player.x) > view_wid / cam_wid + hw or abs(chunk_draw_y - player.y) > view_hei / cam_hei + hh:
                continue

            atlas_tex = Chunk.generate_chunk(self.seed, chunk_x, chunk_y, self.chunk_size)
            chunk_tex = ShaderHandler.add_texture(
                        atlas_tex,
                        occupation=key
                    )
            self.chunk_buffer[key] = chunk_tex
            yield

    def update_chunks(self, t_x, t_y):
        if self.prune_job is None:
            self.prune_job = self.prune_chunks(t_x, t_y)
        if self.chunk_job is None:
            self.chunk_job = self.generate_chunk(t_x, t_y)

        try:
            next(self.prune_job)
        except StopIteration:
            self.prune_job = None

        try:
            next(self.chunk_job)
        except StopIteration:
            self.chunk_job = None
            
    def draw(self):
        pass

    def get_time_coefficients(self, interval, l):
        p_x, p_y, p_m = l[interval]
        p_x2, p_y2, p_m2 = l[interval + 1]
        h = p_x2 - p_x

        a = p_y
        b = p_m
        c = 3 * (p_y2 - p_y) / h ** 2 - (2 * p_m + p_m2) / h
        d = 2 * (p_y - p_y2) / h ** 3 + (p_m + p_m2) / h ** 2
        
        return (a, b, c, d)

    def time_spline(self, time):
        t = time / self.time_cap
        color = [0, 0, 0]
        lists = (self.times_r, self.times_g, self.times_b)
        for i in range(3):
            pair = bisect.bisect_left(lists[i], t, key=lambda x: x[0]) - 1
            c = self.get_time_coefficients(pair, lists[i])
            offset = t - lists[i][pair][0]
            color[i] = c[0] + c[1] * (offset) + c[2] * (offset) ** 2 + c[3] * (offset) ** 3
        return tuple(color)

    def pre_draw(self):
        screen_size = et.get_screen_size()

        main_cam = Camera.get_main_camera()
        main_cam_pos = main_cam.get_pos()
        main_cam_scale = main_cam.get_scale()

        lights_pos = [(light.x, light.y, light.z, light.strength) for light in lights]
        flat_pos = np.array(lights_pos, dtype=np.float32).flatten()
        lights_color = [(light.r, light.g, light.b) for light in lights]
        flat_color = np.array(lights_color, dtype=np.float32).flatten()

        ShaderHandler.set_shader("map")
        ShaderHandler.set_uniform_value("u_time_color", "3f", *self.time_color)
        ShaderHandler.set_uniform_value("u_player", "2f", player.x, player.y)
        ShaderHandler.set_uniform_value("u_cam_pos", "2f", main_cam_pos[0], main_cam_pos[1])
        ShaderHandler.set_uniform_value("u_cam_scale", "2f", main_cam_scale[0], main_cam_scale[1])
        ShaderHandler.set_uniform_value("u_screen", "2f", screen_size[0], screen_size[1])
        ShaderHandler.set_uniform_value("u_lights", "4fv", *(len(lights_pos), flat_pos))
        ShaderHandler.set_uniform_value("u_lights_color", "3fv", *(len(lights_color), flat_color))
        ShaderHandler.set_uniform_value("u_count_lights", "1i", len(lights_pos))

        hw = 32 * self.chunk_size // 2
        hh = (15 + 1) * self.chunk_size // 2
        cam = Camera.get_main_camera()

        for key in self.chunk_buffer.keys():
            chunk_x, chunk_y = key

            chunk_draw_x = hw * chunk_x + hw * chunk_y
            chunk_draw_y = hh * chunk_x - hh * chunk_y

            et.draw_image(self.chunk_buffer[key], (chunk_draw_x, chunk_draw_y), (32 * self.chunk_size + 0.1, (15 + 1) * self.chunk_size - 1 + 0.1), 0)

    def build_chunk_atlas(self, tiles, tile_w, tile_h):
        factor = min(max(1, 2 // Camera.get_main_camera().get_scale()[0]), 8)
        tile_w = int(tile_w / factor)
        tile_h = int(tile_h / factor)
        cols = int(self.chunk_size)
        rows = int(self.chunk_size)
        atlas_w = cols * tile_w
        atlas_h = rows * (tile_h + 1) - 1
        atlas = Image.new("RGBA", (int(atlas_w), int(atlas_h)))

        for i, tile in enumerate(tiles):
            x_grid = i % cols
            y_grid = i // cols
            hh = (tile_h // 2 + 1)
            hw = tile_w // 2
            x = hw * x_grid + hw * y_grid
            y = hh * x_grid - hh * y_grid + atlas_h // 2 - tile_h // 2

            final_tile = self._block_cache.get(str(tile))
            if final_tile is None:
                for tile_tex in tile:
                    texture = et.tex(tile_tex[0])["texture"]
                    tile_v = texture
                    alpha = tile_tex[1]
                    if factor > 1:
                        tile_v = texture.resize((max(1, tile_w), max(1, tile_h)), Image.NEAREST)
                    if alpha < 1.0:
                        tile_v = tile_v.copy()
                        tile_v.putalpha(tile_v.getchannel("A").point(lambda a: int(a * alpha)))

                    if final_tile is None:
                        final_tile = tile_v
                    else:
                        final_tile.paste(tile_v, (0, 0), tile_v)
                        
                self._block_cache[str(tile)] = final_tile

            atlas.paste(final_tile, (x, y), final_tile)

        return atlas

class Player(Entity):
    def __init__(self, pos, name, controllable):
        super().__init__(pos, "player", (16, 16), layer=30)
        self.cam = et.get_cam("main")
        self.z = 0
        self.grv = 0.2
        self.speed = 1
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.jump_power = 2
        self.nickname = name
        self.controllable = controllable
        self.interp_time = 0
        self.server_update_step = GameLoop.get_fps() / 20#server.UPDATES

        vh, vw = et.get_screen_size()
        self.cam_follow_pos = [(self.x - vh / 2), (self.y - vw / 2)]

    def interp_pos(self, pos):
        self.goal_x = pos[0]
        self.goal_y = pos[1]
        self.start_x = self.x
        self.start_y = self.y
        self.interp_time = self.server_update_step

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

        self.set_layer(self.y + 24)

        if self.interp_time > 0:
            t = 1 - (self.interp_time / self.server_update_step)
            self.x = self.goal_x * t + self.start_x * (1 - t)
            self.y = self.goal_y * t + self.start_y * (1 - t)
            self.interp_time -= 1

        if self.controllable:
            if Input.get_pressed(K_ESCAPE) and not Commander.showing_chat:
                GameLoop.end()

            if Input.get_press(K_t) and not Commander.showing_chat:
                Commander.start_chat(self)

            if not Commander.showing_chat:
                if Input.get_press(K_w):
                    self.vel_y -= self.speed / 10
                if Input.get_press(K_a):
                    self.vel_x -= self.speed / 5
                if Input.get_press(K_s):
                    self.vel_y += self.speed / 10
                if Input.get_press(K_d):
                    self.vel_x += self.speed / 5
                if Input.get_press(K_SPACE) and self.z == 0:
                    self.vel_z = self.jump_power

            vh, vw = et.get_screen_size()
            self.cam_follow_pos[0] -= ((self.cam_follow_pos[0]) - (self.x - vh / 2)) / 5
            self.cam_follow_pos[1] -= ((self.cam_follow_pos[1]) - (self.y - vw / 2)) / 5
            self.cam.set_pos(self.cam_follow_pos)

    def draw(self):
        color = game_map.time_color
        ShaderHandler.set_shader("def_map")
        ShaderHandler.set_uniform_value("u_time_color", "3f", *color)

        for light in lights:
            d = ((self.x - light.x) ** 2 + (self.y - light.y) ** 2) ** 0.5
            exp_v = np.clip(d / light.strength, 0, 1)
            I = 2.7 ** (-5 * exp_v) - 2.7 ** -5
            I /= 1 - 2.7**-5
            light_color = (max(color[0], light.r), max(color[1], light.g), max(color[1], light.b), 1)
            color = (color[0] * (1 - I) + light_color[0] * I, color[1] * (1 - I) + light_color[1] * I, color[2] * (1 - I) + light_color[2] * I)
    
        et.draw_image(et.tex(self.image), (self.x, self.y - self.z - 3), (self.width, self.height), color=color)

class Slime(Entity):
    def __init__(self, pos, color, size=1):
        super().__init__(pos, "slime5", (32 * size, 32 * size))
        self.color = color
        self.size = size
        self.z = 0
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.grv = 0.2
        self.speed = 0.025
        self.time_to_jump = 200
        self.target = None
        self.target_move = [0, 0]
        self.air = False
        self.fall_time = 0

    def tick(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.z += self.vel_z

        if self.z <= 0:
            self.vel_x *= 0.75
            self.vel_y *= 0.75
            self.z = 0
            if self.air:
                self.fall_time = self.time_to_jump
                self.air = False
        else:
            self.vel_z -= self.grv

        self.set_layer(self.y + 24)

        player_dist = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

        if player_dist < 100:
            self.target = (player.x, player.y)
            if self.time_to_jump > -40:
                self.time_to_jump = max(-40, self.time_to_jump - 10)

        if self.time_to_jump > -40:
            self.time_to_jump = max(-40, self.time_to_jump - 5)

        if self.time_to_jump < 100:
            sprite_index = int(np.clip(10 - self.time_to_jump / 20, 0, 10))
            self.image = f"slime{sprite_index}"
        else:
            t = (self.fall_time - self.time_to_jump) / 50
            sprite_index = int(np.clip(5 + 3 * (1 - cos(t)) * 0.9 ** t, 5, 10))
            self.image = f"slime{sprite_index}"

        if self.time_to_jump <= -40:
            sprite_index = int(np.clip(6 - (-self.time_to_jump - 40), 0, 10))
            self.image = f"slime{sprite_index}"
            self.time_to_jump -= 1
            if self.time_to_jump < -45:
                if player_dist < 100:
                    self.target = (player.x, player.y)
                else:
                    self.target = (self.x + random.random() * 60 - 30, self.y + random.random() * 60 - 30)

                target_dist = ((self.target[0] - self.x) ** 2 + (self.target[1] - self.y) ** 2) ** 0.5
                self.vel_z = np.clip(target_dist / 10, 2.5, 3.6)
                self.target_move[0] = min((self.target[0] - self.x) * self.speed, 1.4)
                self.target_move[1] = min((self.target[1] - self.y) * self.speed, 1.4)

                self.air = True

                self.time_to_jump = 1200 + random.random() * 500

        if self.z > 0:
            sprite_index = int(np.clip(5 - abs(self.vel_z * 2), 0, 5))
            self.image = f"slime{sprite_index}"
            self.vel_x = self.target_move[0]
            self.vel_y = self.target_move[1]

    def draw(self):
        color = game_map.time_color
        ShaderHandler.set_shader("def_map")
        ShaderHandler.set_uniform_value("u_time_color", "3f", *color)

        for light in lights:
            d = ((self.x - light.x) ** 2 + (self.y - light.y) ** 2) ** 0.5
            exp_v = np.clip(d / light.strength, 0, 1)
            I = 2.7 ** (-5 * exp_v) - 2.7 ** -5
            I /= 1 - 2.7**-5
            light_color = (max(color[0], light.r), max(color[1], light.g), max(color[1], light.b), 1)
            color = (color[0] * (1 - I) + light_color[0] * I, color[1] * (1 - I) + light_color[1] * I, color[2] * (1 - I) + light_color[2] * I)

        color = (color[0] * self.color[0], color[1] * self.color[1], color[2] * self.color[2])

        et.draw_image(et.tex(self.image), (self.x, self.y - self.z - 3), (self.width, self.height), color=color)

class Light(Entity):
    def __init__(self, pos, strength, color=(255, 255, 255)):
        super().__init__(pos)
        self.strength = strength
        self.z = pos[2]
        self.r = color[0] / 255
        self.g = color[1] / 255
        self.b = color[2] / 255

class Commander(Entity):
    _context = {}
    showing_chat = False
    chat_text = ""
    chat_text_pointer = 0
    chat_text_selection = 0
    _using = None
    feed = []
    typed_feed = []
    max_messages = 128
    scroll_index = 0
    caps = False
    players = {}
    chat_font = pg.font.Font(FONTS / "game_font.ttf", 18)
    input_listener = None

    def __init__(self):
        super().__init__((0, 0), None)

    @classmethod
    def esc_logic(cls, message):
        cls.chat_text = ""
        cls.set_chatting(False)
        return False

    @classmethod
    def enter_logic(cls, message):
        if message == "":
            cls.set_chatting(False)

            return False
        
        output = cls.process(message, cls._using)
        if not output == None:
            cls.feed.insert(0, output)
            if len(cls.feed) > cls.max_messages:
                cls.feed.pop(-1)

        cls.typed_feed.insert(0, message)
        cls.chat_text = ""
        cls.set_chatting(False)
        return False

    @classmethod
    def start_chat(cls, entity):
        cls.input_listener = InputListener({
            ("ctrl", "j"),
            ("ctrl", "k"),
            ("ctrl", "l")
        }, cls.typed_feed, esc_logic=cls.esc_logic, enter_logic=cls.enter_logic)
        Commander.set_chatting(True)
        Commander.set_using(entity)

    @classmethod
    def tick(cls):
        if not cls.input_listener == None:
            if cls.input_listener.listener.is_alive():
                cls.chat_text = cls.input_listener.message
                cls.chat_text_pointer = cls.input_listener.pointer
                cls.chat_text_selection = cls.input_listener.select_pointer

    def draw(self):
        pass

    @classmethod
    def set_caps(cls, cap):
        cls.caps = cap

    @classmethod
    def set_using(cls, entity):
        cls._using = entity
        
    @classmethod
    def set_font(cls, font):
        cls.chat_font = font

    @classmethod
    def set_context(cls, context):
        cls._context = context

    @staticmethod
    def convert_to_time(time, time_cap):
        hours = (int(time)) // (1/24 * time_cap)
        if hours >= 13: hours -= 12
        hours = str(int(hours))
        minutes = str(int(int(time) % (1/24 * time_cap) * 60 // (1/24 * time_cap)))
        if int(minutes) < 10: minutes = "0" + minutes

        return hours, minutes

    @classmethod
    def process(cls, command, caller):
        try:
            if command[0:2] == ">>":
                tokens = command[2:].split()

                if tokens[0] == "time":
                    if tokens[1] == "set":
                        if int(tokens[2]) < 0 or int(tokens[2]) > game_map.time_cap:
                            return {"text": f"time must range from 0 to {game_map.time_cap}", "type": "error"}    
                        game_map.time = int(tokens[2])
                        
                        hours, minutes = cls.convert_to_time(tokens[2], game_map.time_cap)

                        return {"text": f"Time set to {hours}:{minutes} {'p' if int(tokens[2]) >= 13/24 * game_map.time_cap else 'a'}.m.", "type": "success"}

                    elif tokens[1] == "set_speed":
                        game_map.time_vel = int(tokens[2])
                        return {"text": f"Time passing speed altered to {tokens[2]} times the original rate.", "type": "success"}

                    elif tokens[1] == "get":
                        hours, minutes = cls.convert_to_time(game_map.time, game_map.time_cap)
                        return {"text": f"{hours}:{minutes} {'p' if int(game_map.time) >= 13/24 * game_map.time_cap else 'a'}.m.", "type": "success"}
                    
                    else:
                        raise TypeError(f"Unknown time command \"{tokens[1]}\"")

                elif tokens[0] == "set_attribute":
                    selected = cls.selector_process(tokens[1], caller)
                    if tokens[2][0] == "_":
                        return {"text": "fail", "type": "error"}
                    if tokens[3] == "int":
                        for entity in selected:
                            setattr(entity, tokens[2], int(tokens[4]))
                    elif tokens[3] == "float":
                        for entity in selected:
                            setattr(entity, tokens[2], float(tokens[4]))

                elif tokens[0] == "host":
                    cls._context["player"] = caller
                    Host.start_server(tokens[1], cls)
                    return {"text": f"Hosting at: {tokens[1]}", "type": "success"}

                elif tokens[0] == "connect":
                    cls._context["player"] = caller
                    Client.join_server(tokens[1], cls)
                    return {"text": f"Connected successfully at: {tokens[1]}", "type": "success"}
                
                elif tokens[0] == "create":
                    if tokens[1] == "Light":
                        lights.append(Light((caller.x, caller.y, caller.z), 20))
                    elif tokens[1] == "Slime":
                        slimes.append(Slime((caller.x, caller.y), (random.random(), random.random(), random.random()), random.random()*0.3 + 0.5))
                    else:
                        raise TypeError(f"Unknown entity \"{tokens[1]}\"")

                    return {"text": f"{tokens[1]} created at: {caller.x:.1f}, {caller.y:.1f}", "type": "success"}
                elif tokens[0] == "cam":
                    if tokens[1] == "size":
                        if tokens[2] == "int":
                            cam = Camera.get_main_camera()
                            cam.set_scale((int(tokens[3]), int(tokens[4])))
                        if tokens[2] == "float":
                            cam = Camera.get_main_camera()
                            cam.set_scale((float(tokens[3]), float(tokens[4])))
                    elif tokens[1] == "angle":
                        if tokens[2] == "int":
                            cam = Camera.get_main_camera()
                            cam.set_angle((int(tokens[3]) * math.pi / 180))
                        if tokens[2] == "float":
                            cam = Camera.get_main_camera()
                            cam.set_angle((float(tokens[3]) * math.pi / 180))
                    
                else:
                    raise TypeError(f"Unknown command \"{tokens[0]}\"")

            else:
                return {"text": command, "type": "global", "user": caller.nickname}
        except Exception as e:
            return {"text": f"fail: {e}", "type": "error"}
        
        return None

    @classmethod
    def selector_process(cls, selection, caller):
        if selection == "self":
            return [caller]
        if selection[:2] == "@e":
            passed_entities = []
            filters = []
            if len(selection) > 2:
                if selection[2] == "[":
                    filtering = selection[3:-1].split(",")
                    for token in filtering:
                        base, value = token.split("=")
                        if base == "type":
                            filters.append(lambda x: str(x.__class__)[str(x.__class__).rfind(".")+1:-2] == value)

            all_entities = EntityManager.get_all_entities()
            for key in all_entities:
                for entity in all_entities[key]:
                    passed = True
                    for filter_func in filters:
                        if not filter_func(entity):
                            passed = False
                            break
                    if passed:
                        passed_entities.append(entity)
            
            return passed_entities

    @classmethod
    def get_server_data(cls):
        return {"game_time": game_map.time,
                "game_time_speed": game_map.time_vel, 
                "players": [{"pos": [cls.players[player].x, cls.players[player].y], "name": cls.players[player].nickname} for player in cls.players]}

    @classmethod
    def update_server(cls, data):
        game_map.time = data["game_time"]
        game_map.time_vel = data["game_time_speed"]
        for player in data["players"]:
            if cls.players.get(player["name"]) == None:
                cls.players[player["name"]] = Player(player["pos"], player["name"], False)
            else:
                if cls.players[player["name"]].controllable == False:
                    cls.players[player["name"]].interp_pos((player["pos"][0], player["pos"][1]))

    @classmethod
    def set_player(cls, data):
        if cls.players.get(data["name"]) == None:
            cls.players[data["name"]] = Player(data["pos"], data["name"], False)
            return
        if cls.players[data["name"]].controllable == False:
            cls.players[data["name"]].interp_pos((data["pos"][0], data["pos"][1]))

    @classmethod
    def set_chatting(cls, val):
        cls.showing_chat = val

    @classmethod
    def draw_gui(cls):    
        ShaderHandler.set_shader("screen")

        screen_size = et.get_screen_size()
        if cls.showing_chat:
            if cls.chat_text_selection < cls.chat_text_pointer:
                side = -1
                shift_section = cls.chat_text[cls.chat_text_selection:cls.chat_text_pointer]
            else:
                side = 1
                shift_section = cls.chat_text[cls.chat_text_pointer:cls.chat_text_selection]

            font_surf = cls.chat_font.render(cls.chat_text, True, (255, 255, 255))
            texture = ShaderHandler.add_texture(font_surf, True, "chat")

            width = cls.chat_font.size(cls.chat_text[:cls.chat_text_pointer])[0]

            et.draw_image(et.tex("pixel"), (screen_size[0] / 2, screen_size[1] - 16), (screen_size[0], 32), color=(0, 0, 0), alpha=0.5, static=True)


            et.draw_image(texture, (texture["width"] / 2 + 10, screen_size[1] - 16), (texture["width"], texture["height"]), color=(255, 255, 255), alpha=1, static=True)

            if not shift_section == "":
                sec_font_surf = cls.chat_font.render(shift_section, True, (0, 0, 0))
                sec_texture = ShaderHandler.add_texture(sec_font_surf, True, "chat_hover")
                sec_width, sec_height = cls.chat_font.size(shift_section)
                et.draw_image(et.tex("pixel"), (width + side * sec_width / 2 + 10, screen_size[1] - 16), (sec_width, sec_height), color=(255, 255, 255), alpha=.75, static=True)
                et.draw_image(sec_texture, (width + side * sec_width / 2 + 10, screen_size[1] - 16), (sec_texture["width"], sec_texture["height"]), color=(0, 0, 0), alpha=1, static=True)
                et.draw_image(et.tex("pixel"), (width + 10, screen_size[1] - 16), (3, 16), color=(0, 0, 0), static=True)
            else:
                et.draw_image(et.tex("pixel"), (width + 10, screen_size[1] - 16), (3, 16), color=(255, 255, 255), static=True)

        for idx, message in enumerate(cls.feed):
            if idx >= 8: break
            if message.get("time") == None:
                message["time"] = 400

            message["time"] = max(0, message["time"] - 1)
            show_opacity = 1 if cls.showing_chat else min(message["time"], 100) / 100
            feed_text = message["text"]
            if message["type"] == "global":
                feed_text = f'<{message["user"]}> {message["text"]}'
            
            text_color = (1, 1, 1)
            if message["type"] == "error":
                text_color = (1, 0.5, 0.5)
            if message["type"] == "success":
                text_color = (0.75, 0.75, 0.75)

            font_surf = cls.chat_font.render(feed_text, True, (255, 255, 255))
            texture = ShaderHandler.add_texture(font_surf, True, f"chat_{idx}")
            et.draw_image(et.tex("pixel"), (texture["width"] / 2 + 10, screen_size[1] - 48 - 32 * idx), (texture["width"] + 20, 32), color=(0, 0, 0), alpha=0.5 * show_opacity, static=True)
            et.draw_image(texture, (texture["width"] / 2 + 10, screen_size[1] - 48 - 32 * idx), (texture["width"], texture["height"]), color=text_color, alpha=1 * show_opacity, static=True)
            
class MenuManager(Entity):
    def __init__(self):
        super().__init__((0, 0))
        self.chat_font = pg.font.Font(FONTS / "game_font.ttf", 32)
        self.player_name = ""
        self.player_name_text_pointer = 0
        self.ask_player_name()
        random.seed(1)

    @staticmethod
    def valid_username(message):
        allowed = {"_", "!", "."}
        for ch in message:
            if ch.isalnum():
                continue
            if ch in allowed:
                continue
            return False
        return True

    @classmethod
    def enter_logic(cls, message):
        if len(message) > 0:
            if cls.valid_username(message):
                return False

    @classmethod
    def ask_player_name(cls):
        cls.input_listener = InputListener({
            ("ctrl", "j"),
            ("ctrl", "k"),
            ("ctrl", "l"),
        }, esc_logic=lambda a: GameLoop.end(), enter_logic=cls.enter_logic, shift_operations=False)

    def tick(self):
        if self.input_listener.listener.is_alive():
            self.player_name = self.input_listener.message
            self.player_name_text_pointer = self.input_listener.pointer
        else:
            self.game_start(self.player_name)
            EntityManager.remove_entity_layer(self)

    def draw_gui(self):
        screen_size = et.get_screen_size()
        ShaderHandler.set_shader("screen")
        et.set_font(self.chat_font)
        et.draw_text("Nome do usuario:", (screen_size[0] / 2, screen_size[1] / 2), (1, 1), color=(255, 255, 255), alpha=1, static=True, occupation="username_text", align=[0, -1])
        text_surf = et.draw_text(self.player_name, (screen_size[0] / 2, screen_size[1] / 2), (1, 1), color=(255, 255, 255), alpha=1, static=True, occupation="username", align=[0, 1])

        width, height = self.chat_font.size(self.player_name[:self.player_name_text_pointer])
        et.draw_image(et.tex("pixel"), (screen_size[0] / 2 - text_surf["width"] / 2 + width, screen_size[1] / 2 + height / 2), (3, 32), color=(255, 255, 255), alpha=1, static=True)
        
    @staticmethod
    def game_start(player_name):
        GameLoop.set_background_color((98 / 255, 168 / 255, 242 / 255, 0.0))
        global player, game_map, commander, slimes, lights
        commander = Commander()
        player = Player((0, 0), player_name, True)
        slimes = []
        game_map = Map()
        lights = []
        Commander.players[player.nickname] = player

def pre_load_game():
    ShaderHandler.add_shader_file("map")
    ShaderHandler.add_shader_file("screen")
    ShaderHandler.add_shader_file("def_map")

    GameLoop.set_resizable(True)
    GameLoop.set_can_fullscreen(True)
    screen_size = (GameLoop.view_width, GameLoop.view_height)
    GameLoop.set_screen_size(screen_size)
    GameLoop.set_title("Jogão")
    GameLoop.setup()

    Texture.set_texture("player", SOURCES / "player.png")
    Texture.set_texture("pixel", SOURCES / "pixel.png")

    Texture.set_texture("slime0", SOURCES / "entities" / "slime" / "slime0.png")
    Texture.set_texture("slime1", SOURCES / "entities" / "slime" / "slime1.png")
    Texture.set_texture("slime2", SOURCES / "entities" / "slime" / "slime2.png")
    Texture.set_texture("slime3", SOURCES / "entities" / "slime" / "slime3.png")
    Texture.set_texture("slime4", SOURCES / "entities" / "slime" / "slime4.png")
    Texture.set_texture("slime5", SOURCES / "entities" / "slime" / "slime5.png")
    Texture.set_texture("slime6", SOURCES / "entities" / "slime" / "slime6.png")
    Texture.set_texture("slime7", SOURCES / "entities" / "slime" / "slime7.png")
    Texture.set_texture("slime8", SOURCES / "entities" / "slime" / "slime8.png")
    Texture.set_texture("slime9", SOURCES / "entities" / "slime" / "slime9.png")
    Texture.set_texture("slime10", SOURCES / "entities" / "slime" / "slime10.png")

    cam = Camera.get_main_camera()
    cam.set_scale((1, 1))

    Input.set_keys(K_w, K_a, K_s, K_d, K_SPACE, K_t,K_LCTRL, K_UP, K_DOWN, K_ESCAPE, K_y, K_u)

    GameLoop.debug = True
    Testing.set_def_cap(1000)

    GameLoop.set_background_color((0.0, 0.0, 0.0, 0.0))

if __name__ == "__main__":
    pre_load_game()

    MenuManager()

    GameLoop.start()

    print(Testing.get_relatory())
    
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