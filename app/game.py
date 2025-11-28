from looping import GameLoop
from entity import Entity, EntityManager
from entity import EntityTools as et
from OpenGL.GL import *
from pygame.locals import *
from inputting import Input
from PIL import Image
import pygame as pg
import random
from shaders import ShaderHandler
from transformations import Transformation
from pynput import keyboard
from client import Client
from host import Host
from pathlib import Path
from texture import Texture
from camera import Camera
from testing import Testing

CWD = Path.cwd()
SOURCES = CWD / "app" / "sources"
FONTS = CWD / "app" / "sources" / "fonts"
SHADERS = CWD / "app" / "shaders"

pg.font.init()

class Map(Entity):
    chunks = {}
    def __init__(self):
        super().__init__((0, 0), None)
        self.time = 0
        self.time_cap = 24000
        self.time_vel = 1

        for x in range(-3, 3):
            for y in range(-3, 3):
                chunk_sprites = [random.choice([et.tex("grass0"), et.tex("grass1"), et.tex("sand0")]) for _ in range(64)]
                atlas_tex = self.build_chunk_atlas(chunk_sprites, 32, 15)
                self.chunks[f"{x},{y}"] = ShaderHandler.add_texture(atlas_tex)

        self.shaders = ShaderHandler.get_shader_program("map")

    def tick(self):
        self.time += self.time_vel
        if self.time >= self.time_cap:
            self.time = 0

    def draw(self):
        pass

    def pre_draw(self):
        main_cam = Camera.get_main_camera()
        main_cam_pos = main_cam.get_pos()
        main_cam_scale = main_cam.get_scale()
        
        ShaderHandler.set_shader(self.shaders)

        ShaderHandler.set_uniform_value("u_time", "1i", self.time)
        ShaderHandler.set_uniform_value("u_cam", "2f", main_cam_pos[0], main_cam_pos[1])
        ShaderHandler.set_uniform_value("u_cam_sc", "2f", main_cam_scale[0], main_cam_scale[1])
        ShaderHandler.set_uniform_value("u_time_cap", "1i", self.time_cap)
        ShaderHandler.set_uniform_value("u_screen", "2f", screen_size[0], screen_size[1])
    
        for key in self.chunks.keys():
            chunk_x, chunk_y = map(int, key.split(","))

            hw = 32 * 8 // 2
            hh = 15 * 8 // 2 + .5
            chunk_draw_x = hw * chunk_x + hw * chunk_y
            chunk_draw_y = hh * chunk_x - hh * chunk_y

            et.draw_image(self.chunks[key], (chunk_draw_x, chunk_draw_y), (32 * 8 + 0.1, 15 * 8 + 0.1), 0)

    def pg_surface_to_pil(self, surface):
        data = pg.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()
        return Image.frombytes("RGBA", (width, height), data)

    def build_chunk_atlas(self, tiles, tile_w, tile_h):
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
            atlas.paste(self.pg_surface_to_pil(tile), (x, y), self.pg_surface_to_pil(tile))

        return atlas

class Player(Entity):
    def __init__(self, pos, name, controllable):
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
        self.controllable = controllable
        self.interp_time = 0
        self.server_update_step = 60 / 20

        vh, vw = et.get_screen_size()
        self.cam_follow_pos = [(self.x - vh / 2), (self.y - vw / 2)]

    def interp_pos(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        # self.goal_x = pos[0]
        # self.goal_y = pos[1]
        # self.start_x = self.x
        # self.start_y = self.y
        # self.interp_time = self.server_update_step

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

        # if self.interp_time > 0:
        #     t = self.interp_time / self.server_update_step
        #     self.x = self.goal_x * t + self.start_x * (1 - t)
        #     self.y = self.goal_y * t + self.start_y * (1 - t)
        #     self.interp_time -= 1

        if self.controllable:
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

            vh, vw = et.get_screen_size()
            self.cam_follow_pos[0] -= ((self.cam_follow_pos[0]) - (self.x - vh / 2)) / 5
            self.cam_follow_pos[1] -= ((self.cam_follow_pos[1]) - (self.y - vw / 2)) / 5
            self.cam.set_pos(self.cam_follow_pos)


    def get_mvp(self):
        return Transformation.affine_transform((self.x, self.y - self.z - 3), (self.width, self.height), self.angle)

class Commander(Entity):
    _context = {}
    showing_chat = False
    chat_text = ""
    _using = None
    feed = []
    max_messages = 8
    scroll_index = 0
    caps = False
    players = {}
    chat_font = pg.font.Font(FONTS / "game_font.ttf", 18)
    player_name = True
    game_started = False

    IGNORED_COMBOS = {
        ("ctrl", "j"),
        ("ctrl", "k"),
        ("ctrl", "l"),
    }

    pressed_modifiers = set()

    def __init__(self):
        super().__init__((0, 0), None)

    @classmethod
    def tick(cls):
        if not cls.player_name and not cls.game_started:
            game_start(cls.chat_text)
            cls.chat_text = ""
            cls.game_started = True

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
        mods = cls.get_modifiers()
        is_ctrl = "ctrl" in mods
        is_shift = "shift" in mods
        is_alt = "alt" in mods
        if isinstance(key, keyboard.Key):
            if key == keyboard.Key.space:
                cls.chat_text += " "
                return

            if key == keyboard.Key.backspace:
                if len(cls.chat_text) > 0:
                    if is_ctrl:
                        idx = cls.chat_text.rstrip().rfind(" ")
                        if idx == -1:
                            cls.chat_text = ""
                        else:
                            cls.chat_text = cls.chat_text[:idx+1]
                    else:
                            cls.chat_text = cls.chat_text[:-1]

                return

            cls.pressed_modifiers.add(key)
            return

        char = key.char
        if char is None:
            return
        char = char.lower()
        combo = tuple(mods + [char])


        if combo in cls.IGNORED_COMBOS:
            return

        caps = Input.get_caps()
        caps_case = not caps if is_shift else caps
        cls.chat_text += key.char.upper() if caps_case else key.char

    @classmethod
    def on_release(cls, key):
        if key in cls.pressed_modifiers:
            cls.pressed_modifiers.remove(key)

        if key == keyboard.Key.esc and not cls.player_name:
            return False
        
        if key == keyboard.Key.enter:
            if cls.player_name:
                if len(cls.chat_text) > 0:
                    cls.set_chatting(False)
                    cls.player_name = False

                return False
            
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
                    cls._context["player"] = caller
                    Host.start_server(int(tokens[1]), cls)
                    return {"text": f"Hosting at: {tokens[1]}", "type": "success"}

                elif tokens[0] == "connect":
                    cls._context["player"] = caller
                    Client.join_server(int(tokens[1]), cls)
                    return {"text": f"Connected successfully at: {tokens[1]}", "type": "success"}
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
        return {"game_time": map_obj.time,
                "game_time_speed": map_obj.time_vel, 
                "players": [{"pos": [cls.players[player].x, cls.players[player].y], "name": cls.players[player].nickname} for player in cls.players]}

    @classmethod
    def update_server(cls, data):
        map_obj = cls._context["map"]
        map_obj.time = data["game_time"]
        map_obj.time_vel = data["game_time_speed"]
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
    def ask_player_name(cls):
        listener = keyboard.Listener(on_press=cls.on_press, on_release=cls.on_release)
        listener.start()
        cls.set_chatting(True)

    @classmethod
    def set_chatting(cls, val):
        cls.showing_chat = val

    @classmethod
    def draw_gui(cls):
        screen_shader = ShaderHandler.get_shader_program("screen")
        screen_u_mvp_loc = glGetUniformLocation(screen_shader, "u_mvp")        
        ShaderHandler.set_shader(screen_shader)

        screen_size = et.get_screen_size()
        if cls.showing_chat:
            font_surf = cls.chat_font.render(cls.chat_text, True, (255, 255, 255))
            texture = ShaderHandler.add_texture(font_surf, True)
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
            texture = ShaderHandler.add_texture(font_surf, True)
            et.draw_cam(et.tex("pixel"), (-screen_size[0] / 2 + texture["width"] / 2 + 10, screen_size[1] / 2 - 48 - 32 * idx), (texture["width"] + 20, 32), color=(0, 0, 0), alpha=0.5 * show_opacity)
            et.draw_cam(texture, (-screen_size[0] / 2 + texture["width"] / 2 + 10, screen_size[1] / 2 - 48 - 32 * idx), (texture["width"], texture["height"]), color=text_color, alpha=1 * show_opacity)

def game_start(player_name):
    player = Player((0, 0), player_name, True)
    game_map = Map()
    Commander.set_context({
        "map": game_map
    })
    Commander.players[player.nickname] = player

def pre_load_game():
    ShaderHandler.add_shader_file("map")
    ShaderHandler.add_shader_file("screen")

    global screen_size
    screen_size = (1200, 600)
    GameLoop.set_screen_size(screen_size)
    GameLoop.set_title("Jogão")
    GameLoop.setup()

    Texture.set_texture("player", SOURCES / "player.png")
    Texture.set_texture("pixel", SOURCES / "pixel.png")

    Texture.set_texture("grass0", SOURCES / "grass0.png", True)
    Texture.set_texture("grass1", SOURCES / "grass1.png", True)
    Texture.set_texture("sand0", SOURCES / "sand.png", True)

    cam = Camera.get_main_camera()
    cam.set_scale((5, 5))

    Input.set_keys(K_w, K_a, K_s, K_d, K_SPACE, K_t,K_LCTRL, K_UP, K_DOWN)

    Testing.set_def_cap(1000)

    GameLoop.set_background_color((98 / 255, 168 / 255, 242 / 255, 0.0))

if __name__ == "__main__":
    pre_load_game()

    Commander()
    Commander.ask_player_name()

    GameLoop.start()

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