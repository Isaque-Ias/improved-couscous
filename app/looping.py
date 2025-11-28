import pygame as pg
from pygame.locals import *
from shaders import ShaderHandler
from OpenGL.GL import *
from entity import EntityManager
from inputting import Input
from testing import Testing
from transformations import Transformation

class GameLoop:
    _title = "[Default Title]"
    _screen_size = (800, 600)
    _color = (0, 0, 0, 0)

    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def get_title(cls):
        return cls._title

    @classmethod
    def set_background_color(cls, color):
        glClearColor(color[0], color[1], color[2], color[3])
        cls._color = color

    @classmethod
    def get_background_color(cls):
        return cls._color

    @classmethod
    def set_screen_size(cls, size):
        cls._screen_size = size

    @classmethod
    def get_screen_size(cls):
        return cls._screen_size

    @classmethod
    def setup(cls):
        Transformation.set_size(cls.get_screen_size())
        ShaderHandler.set_size(cls.get_screen_size())
        pg.init()
        ShaderHandler.init_pygame_opengl()
        ShaderHandler.generate_shader_programs()
        ShaderHandler.setup_textured_quad()

    @classmethod
    def start(cls):
        FPS = 60
        clock = pg.time.Clock()
        running = True

        while running:
            Input.update()

            glClear(GL_COLOR_BUFFER_BIT)
            ShaderHandler.set_shader("def")
            ShaderHandler.set_uniform_value("u_texture", "1i", 0)

            entities = EntityManager.get_all_entities()
            content_layers = EntityManager.get_content_layers()
            for layer in content_layers:
                for entity in entities[layer]:
                    entity.tick()

            for layer in content_layers:
                for entity in entities[layer]:
                    entity.pre_draw()

            for layer in content_layers:
                for entity in entities[layer]:
                    entity.draw()

            for layer in content_layers:
                for entity in entities[layer]:
                    entity.draw_gui()
            
            for event in pg.event.get():
                mods = pg.key.get_mods()
                if mods & pg.KMOD_CAPS:
                    Input.set_caps(True)
                else:
                    Input.set_caps(False)
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.WINDOWFOCUSLOST:
                    Input.set_focus(False)

                if event.type == pg.WINDOWFOCUSGAINED:
                    Input.set_focus(True)

            pg.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    GameLoop.start()