import pygame as pg

class Input:
    _keys = {}
    _input = False

    @classmethod
    def set_caps(cls, value):
        cls._caps = value

    @classmethod
    def get_caps(cls):
        return cls._caps

    @classmethod
    def set_keys(cls, *keys):
        for key in keys:
            cls._keys[key] = [False] * 3

    @classmethod
    def update(cls):
        keys = pg.key.get_pressed()
        for inp in cls._keys:
            cls._keys[inp][0] = False
            cls._keys[inp][1] = False
            
            if keys[inp]:
                if not cls._keys[inp][2]:
                    cls._keys[inp][0] = True

                cls._keys[inp][2] = True
            else:
                if cls._keys[inp][2]:
                    cls._keys[inp][1] = True

                cls._keys[inp][2] = False

    @classmethod
    def get_keys(cls):
        return cls._keys
    
    @classmethod
    def get_pressed(cls, key):
        return cls._keys[key][0]
        
    @classmethod
    def get_released(cls, key):
        return cls._keys[key][1]

    @classmethod
    def get_press(cls, key):
        return cls._keys[key][2]