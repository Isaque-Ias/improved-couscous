from entity import Entity
from entity import EntityTools as et
from pygame.locals import *
from inputting import Input
from PIL import Image
import pygame as pg
import random
from shaders import ShaderObject
from transformations import Transformation
from pynput import keyboard
from server import Host, Client

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
        self.time_vel = 1
        
        grass0_surf = pg.image.load(f"app\\sources\\grass0.png").convert_alpha()
        grass1_surf = pg.image.load(f"app\\sources\\grass1.png").convert_alpha()
        sand_surf = pg.image.load(f"app\\sources\\sand.png").convert_alpha()

        for x in range(-3, 3):
            for y in range(-3, 3):
                chunk_sprites = [random.choice([grass0_surf, grass1_surf, sand_surf]) for _ in range(64)]
                atlas_tex = build_chunk_atlas(chunk_sprites, 32, 15)
                self.chunks[f"{x},{y}"] = ShaderObject.add_texture(atlas_tex)

    def tick(self):
        self.time += self.time_vel
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
    def __init__(self, pos, name):
        super().__init__(pos, "player", (16, 16), layer=30)
        self.cam = et.get_cam("main")
        self.z = 0
        self.grv = 0.2
        self.speed = .3
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.jump_power = 2
        self.nickname = name

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

        if Input.get_press(K_t) and not Commander.showing_chat:
            listener = keyboard.Listener(on_press=Commander.on_press, on_release=Commander.on_release)
            listener.start()
            Commander.set_chatting(True)
            Commander.set_using(self)

        if not Commander.showing_chat:
            if Input.get_press(K_w):
                self.vel_y -= self.speed * 15 / 32
            if Input.get_press(K_a):
                self.vel_x -= self.speed
            if Input.get_press(K_s):
                self.vel_y += self.speed * 15 / 32
            if Input.get_press(K_d):
                self.vel_x += self.speed
            if Input.get_press(K_SPACE) and self.z == 0:
                self.vel_z = self.jump_power

        self.set_layer(self.y + 24)

        vh, vw = et.get_screen_size()
        self.cam_follow_pos[0] -= ((self.cam_follow_pos[0]) - (self.x - vh / 2)) / 5
        self.cam_follow_pos[1] -= ((self.cam_follow_pos[1]) - (self.y - vw / 2)) / 5
        self.cam.set_pos(self.cam_follow_pos)

    def get_mvp(self):
        return Transformation.affine_transform((self.x, self.y - self.z - 3), (self.width, self.height), self.angle)

class Commander:
    _context = {}
    showing_chat = False
    chat_text = ""
    _using = None
    feed = []
    max_messages = 8
    scroll_index = 0
    caps = False

    IGNORED_COMBOS = {
        ("ctrl", "j"),
        ("ctrl", "k"),
        ("ctrl", "l"),
    }

    pressed_modifiers = set()

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
    def get_modifiers(cls):
        mods = []
        if any(m in cls.pressed_modifiers for m in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)):
            mods.append("ctrl")
        if any(m in cls.pressed_modifiers for m in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)):
            mods.append("shift")
        if any(m in cls.pressed_modifiers for m in (keyboard.Key.alt_l, keyboard.Key.alt_r)):
            mods.append("alt")
        return mods

    @classmethod
    def on_press(cls, key):
        if isinstance(key, keyboard.Key):
            if key == keyboard.Key.space:
                cls.chat_text += " "
                return

            if key == keyboard.Key.backspace:
                cls.chat_text = cls.chat_text[:-1]
                return

            cls.pressed_modifiers.add(key)
            return

        char = key.char.lower()
        mods = cls.get_modifiers()
        combo = tuple(mods + [char])

        if combo[0] == "shift":
            cls.chat_text += combo[1].upper() if not cls.caps else combo[1]
            return
        
        if combo in cls.IGNORED_COMBOS:
            return

        if not mods:
            cls.chat_text += key.char.upper() if cls.caps else key.char

        # if key.name == "space":
        #     cls.chat_text += " "
        # elif key.name == "backspace":
        #     if len(cls.chat_text) > 0:
        #         if Input.get_press(K_LCTRL):
        #             idx = cls.chat_text.rfind(" ")
        #             if idx == -1:
        #                 cls.chat_text = ""
        #             else:
        #                 cls.chat_text = cls.chat_text[:idx+1]
        #         else:
        #             if cls.chat_text[-1] == ">":
        #                 idx = cls.chat_text.rfind("<")
        #                 cls.chat_text = cls.chat_text[:idx] 
        #             else:
        #                 cls.chat_text = cls.chat_text[:-1]
        # # else:
        #     # if key.name == "ctrl_l":
        #         # cls.chat_text += f"<{key.name}>"


    @classmethod
    def on_release(cls, key):
        if key in cls.pressed_modifiers:
            cls.pressed_modifiers.remove(key)

        if key == keyboard.Key.esc:
            return False
        
        if key == keyboard.Key.enter:
            if cls.chat_text == "":
                cls.set_chatting(False)

                return False
            
            output = cls.process(cls.chat_text, cls._using)
            if not output == None:
                cls.feed.insert(0, output)
                if len(cls.feed) > cls.max_messages:
                    cls.feed.pop(-1)

            cls.chat_text = ""
            cls.set_chatting(False)

            return False

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
        map_obj = cls._context["map"]
        try:
            if command[0:2] == ">>":
                tokens = command[2:].split()
        
                if tokens[0] == "time":
                    if tokens[1] == "set":
                        if int(tokens[2]) < 0 or int(tokens[2]) > map_obj.time_cap:
                            return {"text": f"time must range from 0 to {map_obj.time_cap}", "type": "error"}    
                        map_obj.time = int(tokens[2])
                        
                        hours, minutes = cls.convert_to_time(tokens[2], map_obj.time_cap)

                        return {"text": f"Time set to {hours}:{minutes} {'p' if int(tokens[2]) >= 13/24 * map_obj.time_cap else 'a'}.m.", "type": "success"}

                    elif tokens[1] == "set_speed":
                        map_obj.time_vel = int(tokens[2])
                        return {"text": f"Time passing speed altered to {tokens[2]} times the original rate.", "type": "success"}

                    elif tokens[1] == "get":
                        hours, minutes = cls.convert_to_time(map_obj.time, map_obj.time_cap)
                        return {"text": f"{hours}:{minutes} {'p' if int(map_obj.time) >= 13/24 * map_obj.time_cap else 'a'}.m.", "type": "success"}

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
                    Host.start_server(int(tokens[1]), cls)

                elif tokens[0] == "connect":
                    Client.join_server(int(tokens[1]), cls)
            else:
                return {"text": command, "type": "global", "user": caller.nickname}
        except Exception as e:
            return {"text": f"fail: {e}", "type": "error"}
        
        return None

    @classmethod
    def selector_process(cls, selection, caller):
        if selection == "self":
            return [caller]
    
    @classmethod
    def get_server_data(cls):
        map_obj = cls._context["map"]
        return {"game_time": map_obj.time, "game_time_speed": map_obj.time_vel}

    @classmethod
    def update_server(cls, data):
        map_obj = cls._context["map"]
        map_obj.time = data["game_time"]
        map_obj.time_vel = data["game_time_speed"]

    @classmethod
    def set_chatting(cls, val):
        cls.showing_chat = val

    @classmethod
    def draw(cls):
        screen_size = et.get_screen_size()
        if cls.showing_chat:
            font_surf = cls.chat_font.render(cls.chat_text, True, (255, 255, 255))
            texture = ShaderObject.add_texture(font_surf, True)
            et.draw_cam(et.tex("pixel"), (0, screen_size[1] / 2 - 16), (screen_size[0], 32), color=(0, 0, 0), alpha=0.5)
            et.draw_cam(texture, (-screen_size[0] / 2 + texture["width"] / 2 + 10, screen_size[1] / 2 - 16), (texture["width"], texture["height"]), color=(255, 255, 255), alpha=1)

        for idx, message in enumerate(cls.feed):
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
            texture = ShaderObject.add_texture(font_surf, True)
            et.draw_cam(et.tex("pixel"), (-screen_size[0] / 2 + texture["width"] / 2 + 10, screen_size[1] / 2 - 48 - 32 * idx), (texture["width"] + 20, 32), color=(0, 0, 0), alpha=0.5 * show_opacity)
            et.draw_cam(texture, (-screen_size[0] / 2 + texture["width"] / 2 + 10, screen_size[1] / 2 - 48 - 32 * idx), (texture["width"], texture["height"]), color=text_color, alpha=1 * show_opacity)

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