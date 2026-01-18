class Cam:
    def __init__(self, pos, scale, angle, name):
        self.set_name(name)
        self.set_pos(pos)
        self.set_scale(scale)
        self.set_angle(angle)

    def set_pos(self, pos):
        self._pos = pos

    def set_scale(self, scale):
        self._scale = scale

    def set_angle(self, angle):
        self._angle = angle

    def set_name(self, name):
        self._name = name

    def get_pos(self):
        return self._pos

    def get_scale(self):
        return self._scale

    def get_angle(self):
        return self._angle

    def get_name(self):
        return self._name

class Camera:
    _cams = {"main": Cam([0, 0], [1, 1], 0, "main")}
    _main = "main"

    @classmethod
    def create_cam(cls, name):
        if cls._cams.get(name):
            raise KeyError
        
        cam = Cam([0, 0], [0, 0], 0, name)
        cls._cams[name] = cam
        return cam
    
    @classmethod
    def destroy_cam(cls, name):
        cls._cams.pop(name)

    @classmethod
    def set_main_camera(cls, name):
        cls._main = name
    
    @classmethod
    def get_main_camera(cls):
        return cls._cams[cls._main]

    @classmethod
    def get_camera(cls, name):
        return cls._cams[name]