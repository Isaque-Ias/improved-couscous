from shaders import ShaderHandler
import pygame as pg

class Texture:
    _textures = {}
    
    @classmethod
    def set_texture(cls, name, path, save_as_py_surf=False):
        if not cls._textures.get(path) == None:
            raise KeyError
            
        if save_as_py_surf:
            surface = pg.image.load(path)
            width, height = surface.get_size()
            cls._textures[name] = {"texture": surface, "width": width, "height": height}
            return

        surface = pg.image.load(path).convert_alpha()
        cls._textures[name] = ShaderHandler.add_texture(surface, True)

    @classmethod
    def get_texture(cls, name):
        return cls._textures[name]