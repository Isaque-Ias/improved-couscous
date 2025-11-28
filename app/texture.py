from shaders import ShaderHandler
import pygame as pg

class Texture:
    _textures = {}
    
    @classmethod
    def set_texture(cls, name, path, pygame_surf=False):
        if not cls._textures.get(path) == None:
            raise KeyError
        
        if pygame_surf:
            cls._textures[name] = pg.image.load(path).convert_alpha()
            return
        
        cls._textures[name] = ShaderHandler.load_texture(path)

    @classmethod
    def get_texture(cls, name):
        return cls._textures[name]