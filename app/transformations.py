import numpy as np
from math import sin, cos

class Transformation:
    _window_size = (0, 0)
    @classmethod
    def set_size(cls, size):
        cls._window_size = size

    @classmethod
    def affine_transform(cls, pos, scale, angle):
        c, s = cos(angle), sin(angle)

        rotation_z = np.array([
            [ c, -s * (cls._window_size[0] / cls._window_size[1]), 0, 0],
            [ s,  c * (cls._window_size[0] / cls._window_size[1]), 0, 0],
            [ 0,  0, 1, 0],
            [ 0,  0, 0, 1]
        ], dtype=np.float32)

        scaling = np.array([
            [scale[0] * 2 / cls._window_size[0], 0, 0, 0],
            [0, scale[1] * 2 / cls._window_size[0], 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        tx = pos[0] * 2 / cls._window_size[0]
        ty = pos[1] * 2 / cls._window_size[1]
        translation = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [tx - 1, 1 - ty, 0, 1]
        ], dtype=np.float32)
        
        return scaling @ rotation_z @ translation