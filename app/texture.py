from shaders import ShaderObject

class Texture:
    _textures = {}
    
    @classmethod
    def set_texture(cls, name, path):
        if not cls._textures.get(path) == None:
            raise KeyError
        
        cls._textures[name] = ShaderObject.load_texture(path)

    @classmethod
    def get_texture(cls, name):
        return cls._textures[name]