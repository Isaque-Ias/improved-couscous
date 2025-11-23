from entity import Entity
from entity import EntityTools as et
from pygame.locals import *
from inputting import Input

class Map(Entity):
    def __init__(self):
        super().__init__((0, 0), et.tex("grass"))
        map_width = 5
        map_height = 5
        self.blocks = [[0 for _ in range(map_width)] for _ in range(map_height)]
        for line in range(len(self.blocks)):
            for block in range(len(self.blocks[line])):
                y_pos = 250 + 8 * block - 8 * line
                block = Block((16 * block + 16 * line, y_pos), "grass")
                block.set_layer(y_pos)

    def tick(self):
        pass

    def draw(self):
        pass

class Block(Entity):
    def __init__(self, pos, image):
        super().__init__(pos, image, (32.1, 15.1))

    def __str__(self):
        return "f"

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, "player", (16, 16), layer=30)
        self.cam = et.get_cam("main")
        self.z = 0
        self.grv = 0.4
        self.speed = .3
        self.vel_x = 0
        self.vel_y = 0

        vh, vw = et.get_screen_size()
        self.cam_follow_pos = [(self.x - vh / 2), (self.y - vw / 2)]

    def tick(self):
        self.x += self.vel_x
        self.y += self.vel_y

        self.vel_x *= 0.75
        self.vel_y *= 0.75

        if Input.get_press(K_w):
            self.vel_y -= self.speed * 0.5
        if Input.get_press(K_a):
            self.vel_x -= self.speed
        if Input.get_press(K_s):
            self.vel_y += self.speed * 0.5
        if Input.get_press(K_d):
            self.vel_x += self.speed

        self.set_layer(self.y + 24)

        vh, vw = et.get_screen_size()
        self.cam_follow_pos[0] -= ((self.cam_follow_pos[0]) - (self.x - vh / 2)) / 5
        self.cam_follow_pos[1] -= ((self.cam_follow_pos[1]) - (self.y - vw / 2)) / 5
        self.cam.set_pos(self.cam_follow_pos)

class Background(Entity):
    def __init__(self):
        super().__init__((0, 0), "pixel", (1280, 720), has_layer=False)

    def tick(self):
        cam = et.get_cam("main")
        x, y = cam.get_pos()
        self.x = x + self.width / 2
        self.y = y + self.height / 2
        