import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
from transformations import Transformation
from entity import EntityManager
from texture import Texture
from inputting import Input
from game import Map, Player, Background
from camera import Camera

class Loop:
    _title = "[Default Title]"
    
    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):

        with open("app\\shaders\\graphics.vsh", "r") as file:
            DEF_VERTEX_SHADER = file.read()

        with open("app\\shaders\\graphics.fsh", "r") as file:
            DEF_FRAGMENT_SHADER = file.read()

        with open("app\\shaders\\background.vsh", "r") as file:
            BG_VERTEX_SHADER = file.read()

        with open("app\\shaders\\background.fsh", "r") as file:
            BG_FRAGMENT_SHADER = file.read()

        screen_size = (1280, 720)
        Transformation.set_size(screen_size)
        ShaderObject.set_size(screen_size)
        ShaderObject.init_pygame_opengl()
        default_shader = ShaderObject.create_shader_program(DEF_VERTEX_SHADER, DEF_FRAGMENT_SHADER)
        background_shader = ShaderObject.create_shader_program(BG_VERTEX_SHADER, BG_FRAGMENT_SHADER)
        ShaderObject.setup_textured_quad()

        running = True
        clock = pg.time.Clock()

        FPS = 60

        Texture.set_texture("grass", "app\\sources\\grass.png")
        Texture.set_texture("player", "app\\sources\\player.png")
        Texture.set_texture("pixel", "app\\sources\\pixel.png")

        glUseProgram(background_shader)
        bg_u_mvp_loc = glGetUniformLocation(background_shader, "u_mvp")
        bg_u_tex_loc = glGetUniformLocation(background_shader, "u_texture")
        
        glUseProgram(default_shader)
        def_u_mvp_loc = glGetUniformLocation(default_shader, "u_mvp")
        def_u_tex_loc = glGetUniformLocation(default_shader, "u_texture")
        EntityManager.set_mvp(def_u_mvp_loc)

        cam = Camera.get_main_camera()
        cam.set_scale((4, 4))

        Map()
        Player((0, 0))
        bg = Background()

        Input.set_keys(K_w, K_a, K_s, K_d)

        while running:
            Input.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT)
            glClearColor(0, 0, 0, 0.0)

            ShaderObject.set_shader(background_shader, bg_u_mvp_loc)

            bg.tick()
            bg.draw()

            ShaderObject.set_shader(default_shader, def_u_mvp_loc)

            glUniform1i(def_u_tex_loc, 0)

            entities = EntityManager.get_all_entities()
            for layer in EntityManager.get_content_layers():
                for entity in entities[layer]:
                    entity.tick()

            for layer in EntityManager.get_content_layers():
                for entity in entities[layer]:
                    entity.draw()

            pg.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    Loop.start()