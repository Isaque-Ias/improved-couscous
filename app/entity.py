from transformations import Transformation

class Entity:
    def __init__(self, pos, image=None, scale=(0, 0), angle=0, layer=0):
        self.pos = pos
        self.image = image
        self.scale = scale
        self.angle = angle
        self.set_layer(layer)

    def set_layer(self, layer):
        if not self.layer == layer: 
            

            self.layer = layer

    def tick(self):
        pass

    def draw(self):
        pass

    def get_mvp(self):
        return Transformation.affine_transform(self.pos, self.scale, self.angle)

    def get_texture(self):
        return self.image["texture"]

class EntityManager:
    _entities = {}
    _content = []
    _id = 0

    @classmethod
    def get_all_entities(cls):
        return cls._entities

    @classmethod
    def get_content_layers(cls):
        return cls._content

    @classmethod
    def create_entity(cls, entity):
        if type(entity) == list:
            for element in entity:
                cls._entities[cls._id] = element
                cls._id += 1
            return
        
        cls._entities[cls._id] = entity
        cls._id += 1