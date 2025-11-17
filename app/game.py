from entity import Entity
from entity import EntityTools as et
from pygame.locals import *
from inputting import Input

class Map(Entity):
    def __init__(self):
        super().__init__((0, 0), et.tex("grass"))
        self.blocks = [
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0],
        ]

    def tick(self):
        pass

    def draw(self):
        screen_size = et.get_screen_size()

        for line in range(len(self.blocks)):
            for block in range(len(self.blocks[line])):        
                et.draw_image("grass", (200 + 32 * block + 32 * line, 250 + 16 * block - 16 * line), (64, 30), 0)

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, "player", (32, 32), layer=30)

    def tick(self):
        if Input.get_press(K_w):
            self.y -= 5
        if Input.get_press(K_a):
            self.x -= 5
        if Input.get_press(K_s):
            self.y += 5
        if Input.get_press(K_d):
            self.x += 5