import pygame as pg

class Loop:
    _title = "[Default Title]"

    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):
        window = pg.display.set_mode((400, 300))
        pg.display.set_caption(cls._title)
        running = True

        FPS = 60
        clock = pg.time.Clock()

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            window.fill((127, 127, 127))

            pg.display.flip()
            clock.tick(FPS)