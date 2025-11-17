from transformations import Transformation
from tools import Tools
from shaders import ShaderObject
from texture import Texture

class EntityTools:
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
        tex = EntityTools.tex(image)
        ShaderObject.render(mvp, tex)

class Entity:
    def __init__(self, pos, image=None, scale=(0, 0), angle=0, layer=0):
        self.x = pos[0]
        self.y = pos[1]
        self.image = image
        self.width = scale[0]
        self.height = scale[1]
        self.angle = angle
        self.layer = layer

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