import numpy as np
from math import sin, cos
from camera import Camera

class Transformation:
    _window_size = (0, 0)

    @classmethod
    def set_size(cls, size):
        cls._window_size = size

    @classmethod
    def affine_transform(cls, pos, scale, angle, static):
        c, s = cos(angle), sin(angle)

        tx = pos[0] * 2 / cls._window_size[0]
        ty = pos[1] * 2 / cls._window_size[1]

        if not static:
            main_cam = Camera.get_main_camera()
            cam_pos = main_cam.get_pos()
            cam_scale = main_cam.get_scale()
            cam_angle = main_cam.get_angle()
            cam_c, cam_s = cos(cam_angle), sin(cam_angle)
            tx = (pos[0] - cam_pos[0]) * 2 / cls._window_size[0]
            ty = (pos[1] - cam_pos[1]) * 2 / cls._window_size[1]

            cam_rotation_z = np.array([
                [ cam_c, -cam_s * (cls._window_size[0] / cls._window_size[1]), 0, 0],
                [ cam_s,  cam_c * (cls._window_size[0] / cls._window_size[1]), 0, 0],
                [ 0,  0, 1, 0],
                [ 0,  0, 0, 1]
            ], dtype=np.float32)

            cam_scaling = np.array([
                [cam_scale[1], 0, 0, 0],
                [0, cam_scale[0] * cls._window_size[1] / cls._window_size[0], 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ], dtype=np.float32)

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

        translation = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [tx - 1, 1 - ty, 0, 1]
        ], dtype=np.float32)

        if static:
            return scaling @ rotation_z @ translation

        return scaling @ rotation_z @ translation @ cam_scaling @ cam_rotation_z