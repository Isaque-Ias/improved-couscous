from linear_alg import Transformation
from shaders import ShaderHandler
from texture import Texture
from camera import Camera
from OpenGL.GL import *

class EntityTools:
    _default_shaders = ShaderHandler.add_shader_file("def")
    _font = None

    @staticmethod
    def get_cam(cam):
        return Camera.get_camera(cam)

    @classmethod
    def get_default_shaders(cls):
        return ShaderHandler.get_shader_program("def")

    @staticmethod
    def get_screen_size():
        return ShaderHandler.get_size()

    @staticmethod
    def tex(tex):
        return Texture.get_texture(tex)

    @staticmethod
    def default_mvp(entity):
        return Transformation.affine_transform((entity.x, entity.y), (entity.width, entity.height), entity.angle, True)

    @staticmethod
    def default_draw(entity):
        ShaderHandler.render(entity.get_mvp(), Texture.get_texture(entity.image))

    @classmethod
    def draw_image(cls, image, pos, scale, angle=0, color=(1, 1, 1), alpha=1, static=False, program=None, unit=GL_TEXTURE0):
        if not program == None:
            ShaderHandler.set_shader(program)

        ShaderHandler.set_uniform_value("u_color", "4f", color[0], color[1], color[2], alpha)
        mvp = Transformation.affine_transform(pos, scale, angle, static)
        ShaderHandler.render(mvp, image, unit)

    @classmethod
    def set_font(cls, font):
        cls._font = font

    @classmethod
    def get_font(cls):
        return cls._font

    @classmethod
    def draw_text(cls, text, pos, scale, color, alpha, static, occupation, align=[0, 0]):
        font_surf = cls.get_font().render(text, True, (255, 255, 255))
        texture = ShaderHandler.add_texture(font_surf, True, occupation)
        width, height = (texture["width"], texture["height"])
        cls.draw_image(texture, (pos[0] + width * align[0] / 2, pos[1] + height * align[1] / 2), (width * scale[0], height * scale[1]), color=color, alpha=alpha, static=static)
        return texture

class Entity:
    def __init__(self, pos, image=None, scale=(0, 0), angle=0, layer=0, has_layer=True):
        self.x = pos[0]
        self.y = pos[1]
        self.image = image
        self.width = scale[0]
        self.height = scale[1]
        self.angle = angle
        self.layer = int(layer)
        if has_layer:
            EntityManager.create_entity(self)
        
    def set_layer(self, layer):
        layer = int(layer)
        if not self.layer == layer:
            EntityManager.agend_layer_change(self, layer)

    def tick(self):
        pass

    def pre_draw(self):
        pass

    def draw(self):
        pass
    
    def draw_gui(self):
        pass

    def get_mvp(self):
        pass

    def get_texture(self):
        return self.image["texture"]
    
    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id
    
    def __str__(self):
        return f"{type(self).__name__} - {self._id}"

class EntityManager:
    _entities = {}
    _content = []
    _layer_changes = {} 
    _id = 0

    @classmethod
    def get_layer_changes(cls):
        return cls._layer_changes

    @classmethod
    def set_layer_change(cls, entity, layer):
        if hasattr(entity, "_id"):
            cls.remove_entity_layer(entity)
        entity.layer = layer
        cls.add_entity_layer(entity)

    @classmethod
    def agend_layer_change(cls, object, layer):
        cls._layer_changes[object._id] = [object, layer]

    @classmethod
    def _ensure_layer(cls, layer):
        if layer not in cls._entities:
            cls._entities[layer] = []
            cls._content.append(layer)
            cls._content.sort()

    @classmethod
    def create_entity(cls, entity):
        if not isinstance(entity, list):
            entity = [entity]

        for obj in entity:
            obj.set_id(cls._id)
            cls._id += 1
            cls.add_entity_layer(obj)

    @classmethod
    def add_entity_layer(cls, entity):
        layer = entity.layer
        cls._ensure_layer(layer)

        cls._entities[layer].append(entity)

    @classmethod
    def remove_entity_layer(cls, entity):
        layer = entity.layer

        if layer not in cls._entities:
            return

        layer_list = cls._entities[layer]

        try:
            layer_list.remove(entity)
        except ValueError:
            return

        if not layer_list:
            cls._content.remove(layer)
            del cls._entities[layer]

    @classmethod
    def get_all_entities(cls):
        return cls._entities

    @classmethod
    def get_content_layers(cls):
        return cls._content

    @classmethod
    def get_background_layers(cls):
        return cls._content
