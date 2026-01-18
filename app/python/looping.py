import pygame as pg
from pygame.locals import *
from shaders import ShaderHandler
from OpenGL.GL import *
from entity import EntityManager
from inputting import Input
from linear_alg import Transformation
import os
from testing import Testing

class GameLoop:
    pg.init()
    _title = "[Default Title]"
    _screen_size = (10, 10)
    _non_full_screen_size = (10, 10)
    _color = (0, 0, 0, 0)
    fps = 60
    _info = pg.display.Info()
    view_width = _info.current_w
    view_height = _info.current_h
    _fullscreen = False
    _resizable = False
    _fullscreenable = False
    _flags = None
    debug = False
    debug_time = False

    @classmethod
    def set_can_fullscreen(cls, value):
        cls._fullscreenable = value

    @classmethod
    def get_can_fullscreen(cls):
        return cls._fullscreenable

    @classmethod
    def get_fullscreen(cls):
        return cls._fullscreen

    @classmethod
    def set_fullscreen(cls, value):
        cls._fullscreen = value

    @classmethod
    def set_resizable(cls, value):
        cls._resizable = value

        cls._flags = DOUBLEBUF | OPENGL
        if cls._resizable:
            cls._flags = DOUBLEBUF | OPENGL | pg.RESIZABLE

    @classmethod
    def get_resizable(cls):
        return cls._resizable
    
    @classmethod
    def get_flags(cls):
        return cls._flags

    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def set_fps(cls, fps):
        cls._fps = fps

    @classmethod
    def get_fps(cls):
        return cls._fps

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
        if not cls.get_fullscreen():
            cls._screen_size = size
        if size == (cls.view_width, cls.view_height):
            cls.set_fullscreen(True)

    @classmethod
    def get_screen_size(cls):
        return cls._screen_size

    @classmethod
    def update_screen_size(cls, size):
        cls.set_screen_size(size)
        Transformation.set_size(size)
        ShaderHandler.set_size(size)

    @classmethod
    def setup(cls):
        Transformation.set_size(cls.get_screen_size())
        ShaderHandler.set_size(cls.get_screen_size())
        
        ShaderHandler.init_pygame_opengl(cls.get_flags())
        ShaderHandler.generate_shader_programs()
        ShaderHandler.setup_textured_quad()

    @classmethod
    def end(cls):
        cls._running = False

    @classmethod
    def start(cls):
        global maped
        cls._fps = 60
        clock = pg.time.Clock()
        maped = {}
        cls._running = True
        while cls._running:
            Input.update()

            glClear(GL_COLOR_BUFFER_BIT)
            ShaderHandler.set_shader("def")
            ShaderHandler.set_uniform_value("u_texture", "1i", 0)

            if cls.debug:
                Testing.cummulation_start()
                
            entities = EntityManager.get_all_entities()
            content_layers = EntityManager.get_content_layers()
            if Input.get_pressed(K_y) or not cls.debug_time:
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

            layer_changes = EntityManager.get_layer_changes()
            for key in layer_changes:
                EntityManager.set_layer_change(*layer_changes[key])
        
            Input.mouse_scroll_x = 0
            Input.mouse_scroll_y = 0
            for event in pg.event.get():
                mods = pg.key.get_mods()
                if mods & pg.KMOD_CAPS:
                    Input.set_caps(True)
                else:
                    Input.set_caps(False)
                if event.type == pg.QUIT:
                    cls._running = False
                    # print("{\n" + str(maped).replace(", ", ",\n")[1:-1] + "\n}")
                    # liste = ""
                    # for key in maped.keys():
                    #     liste = liste + str(key) + ", "
                    # print(liste[:-2])
                    # :
                if event.type == pg.MOUSEWHEEL:
                    Input.mouse_scroll_x = event.x
                    Input.mouse_scroll_y = event.y

                if event.type == pg.WINDOWFOCUSLOST:
                    Input.set_focus(False)

                if event.type == pg.WINDOWFOCUSGAINED:
                    Input.set_focus(True)

                # if event.type == pg.KEYDOWN:
                #     if maped.get(str(event.key)) == None:
                #         maped[str(event.key)] = time
                #         time += 1
                #         print(time)

                if cls.get_resizable():
                    if event.type == pg.VIDEORESIZE:
                        GameLoop.update_screen_size((event.w, event.h))

                if cls.get_can_fullscreen():
                    if event.type == pg.KEYDOWN and event.key == pg.K_F11:
                        cls.set_fullscreen(not cls.get_fullscreen())

                        if not cls.get_fullscreen():
                            max_value = (cls.view_width, cls.view_height)
                            screen_value = cls.get_screen_size()
                            screen_value = (min(screen_value[0], max_value[0] - 30), min(screen_value[1], max_value[1] - 80))
                            os.environ['SDL_VIDEO_CENTERED'] = "1"
                            pg.display.set_mode(max_value, cls.get_flags())
                            pg.display.set_mode(screen_value, cls.get_flags())
                            cls.update_screen_size(screen_value)
                        else:
                            screen_value = (cls.view_width, cls.view_height)
                            pg.display.set_mode(screen_value, pg.FULLSCREEN | cls.get_flags())
                            cls.update_screen_size(screen_value)

            if cls.debug:
                Testing.cummulation_end()

            pg.display.flip()
            clock.tick(cls.get_fps())

if __name__ == "__main__":
    GameLoop.start()