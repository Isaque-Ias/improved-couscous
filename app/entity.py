from transformations import Transformation
from tools import Tools
from shaders import ShaderObject
from texture import Texture
from camera import Camera
from OpenGL.GL import *

class EntityTools:
    _color_loc = 0
    
    @staticmethod
    def get_cam(cam):
        return Camera.get_camera(cam)

    @staticmethod
    def get_screen_size():
        return ShaderObject.get_size()

    @staticmethod
    def tex(tex):
        return Texture.get_texture(tex)

    @staticmethod
    def default_mvp(entity):
        return Transformation.affine_transform((entity.x, entity.y), (entity.width, entity.height), entity.angle)

    @staticmethod
    def default_draw(entity):
        ShaderObject.render(entity.get_mvp(), Texture.get_texture(entity.image))

    @staticmethod
    def draw_image(image, pos, scale, angle):
        mvp = Transformation.affine_transform(pos, scale, angle)
        ShaderObject.render(mvp, image)

    @classmethod
    def set_color_loc(cls, color):
        cls._color_loc = color

    @classmethod
    def draw_cam(cls, image, pos, scale, color=(1, 1, 1), alpha=1):
        glUniform4f(cls._color_loc, color[0], color[1], color[2], alpha)
        main_cam = Camera.get_main_camera()
        cam_pos = main_cam.get_pos()
        cam_scale = main_cam.get_scale()
        screen_size = EntityTools.get_screen_size()
        mvp = Transformation.affine_transform((cam_pos[0] + pos[0] / cam_scale[0] + screen_size[0] / 2, cam_pos[1] + pos[1] / cam_scale[1] + screen_size[1] / 2), (scale[0] / cam_scale[0], scale[1] / cam_scale[1]), 0)
        ShaderObject.render(mvp, image)

class Entity:
    def __init__(self, pos, image=None, scale=(0, 0), angle=0, layer=0, has_layer=True):
        self.x = pos[0]
        self.y = pos[1]
        self.image = image
        self.width = scale[0]
        self.height = scale[1]
        self.angle = angle
        self.layer = layer
        if has_layer:
            EntityManager.create_entity(self)
        
    def set_layer(self, layer):
        if not self.layer == layer:
            EntityManager.remove_entity_layer(self)
            self.layer = layer
            EntityManager.add_entity_layer(self)

    def tick(self):
        pass

    def draw(self):
        EntityTools.default_draw(self)

    def get_mvp(self):
        return EntityTools.default_mvp(self)

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
    _id = 0

    @classmethod
    def set_mvp(cls, mvp):
        cls._mvp = mvp

    @classmethod
    def remove_entity_layer(cls, entity):
        layer = cls._entities[entity.layer]
        index = Tools.binary_search(entity.get_id(), layer, len(layer), lambda x: x.get_id())
        cls._entities[entity.layer].pop(index)

        if len(cls._entities[entity.layer]) == 0:
            index = Tools.binary_search(entity.layer, cls._content, len(cls._content))
            cls._content.pop(index)
            cls._entities.pop(entity.layer)

    @classmethod
    def add_entity_layer(cls, entity):
        if cls._entities.get(entity.layer) == None:
            cls._entities[entity.layer] = [entity]
            index = Tools.binary_search(entity.layer, cls._content, len(cls._content))
            cls._content.insert(index, entity.layer)
        else:
            index = Tools.binary_search(entity.get_id(), cls._entities[entity.layer], len(cls._entities[entity.layer]), lambda x: x.get_id())
            cls._entities[entity.layer].insert(index, entity)

    @classmethod
    def get_all_entities(cls):
        return cls._entities

    @classmethod
    def get_content_layers(cls):
        return cls._content

    @classmethod
    def create_entity(cls, entity):
        if not type(entity) == list:
            entity = [entity]

        for element in entity:
            element.mvp = cls._mvp
            element.set_id(cls._id)
            
            cls.add_entity_layer(element)

            cls._id += 1