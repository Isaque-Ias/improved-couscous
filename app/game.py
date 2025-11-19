from entity import Entity
from entity import EntityTools as et
from pygame.locals import *
from inputting import Input

class Map(Entity):
    def __init__(self):
        super().__init__((0, 0), et.tex("grass"))
        self.blocks = [[0 for _ in range(2)] for _ in range(2)]
        for line in range(len(self.blocks)):
            for block in range(len(self.blocks[line])):
                y_pos = 250 + 8 * block - 8 * line
                block = Block((200 + 16 * block + 16 * line, y_pos), "grass")
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
        super().__init__(pos, "player", (32, 32), layer=30)
        self.cam = et.get_cam("main")
        self.z = 0
        self.grv = 0.4

    def tick(self):
        if Input.get_press(K_w):
            self.y -= 5 * 0.5
        if Input.get_press(K_a):
            self.x -= 5
        if Input.get_press(K_s):
            self.y += 5 * 0.5
        if Input.get_press(K_d):
            self.x += 5

        self.set_layer(self.y)

        vh, vw = et.get_screen_size()
        self.cam.set_pos((self.x - vh / 2, self.y - vw / 2))