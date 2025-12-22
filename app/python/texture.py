from shaders import ShaderHandler
import pygame as pg
from PIL import Image

class Texture:
    _textures = {}
    
    @classmethod
    def set_texture(cls, name, path, save_type=None):
        if not cls._textures.get(path) == None:
            raise KeyError
            
        if save_type == "pygame":
            surface = pg.image.load(path)
            width, height = surface.get_size()
            cls._textures[name] = {"texture": surface, "width": width, "height": height}
            return
        if save_type == "pil":
            surface = Image.open(path).convert("RGBA")
            cls._textures[name] = {"texture": surface, "width": surface.width, "height": surface.height}
            return
            

        surface = pg.image.load(path).convert_alpha()
        cls._textures[name] = ShaderHandler.add_texture(surface, True)

    @classmethod
    def get_texture(cls, name):
        return cls._textures[name]