import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
from transformations import Transformation
from entity import EntityManager
from texture import Texture
from inputting import Input
from game import Map, Player
from camera import Camera

class Loop:
    _title = "[Default Title]"
    
    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):
        screen_size = (500, 500)
        Transformation.set_size(screen_size)
        ShaderObject.set_size(screen_size)
        ShaderObject.init_pygame_opengl()
        shader = ShaderObject.create_shader_program()
        ShaderObject.setup_textured_quad()
        
        glUseProgram(shader)
        global u_mvp_loc, u_tex_loc
        u_mvp_loc = glGetUniformLocation(shader, "u_mvp")
        u_tex_loc = glGetUniformLocation(shader, "u_texture")
        ShaderObject.set_mvp(u_mvp_loc)

        glUniform1i(u_tex_loc, 0)

        running = True
        clock = pg.time.Clock()

        FPS = 60

        Texture.set_texture("faca", "facarambit.webp")
        Texture.set_texture("hitler", "cachorro.jpg")
        Texture.set_texture("grass", "app\\sources\\grass.png")
        Texture.set_texture("player", "app\\sources\\player.png")

        EntityManager.set_mvp(u_mvp_loc)

        cam = Camera.get_main_camera()
        cam.set_scale((1500, 500))
        ang = 0

        entity = [Map(), Player((200, 200))]

        EntityManager.create_entity(entity)

        Input.set_keys(K_w, K_a, K_s, K_d)

        while running:
            Input.update()

            if Input.get_press(K_w):
                cam.set_angle(ang)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT)

            entities = EntityManager.get_all_entities()
            for layer in EntityManager.get_content_layers():
                for entity in entities[layer]:
                    entity.tick()
                    entity.draw()

            pg.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    Loop.start()