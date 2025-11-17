from entity import Entity
from entity import EntityTools as et

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
        ]

    def tick(self):
        pass

    def draw(self):
        for line in range(len(self.blocks)):
            for block in range(len(self.blocks[line])):
                self.blocks[line][block]
                et.draw_image("grass", (500 + 32 * block + 32 * line, 250 + 16 * block - 16 * line), (64, 30), 0)