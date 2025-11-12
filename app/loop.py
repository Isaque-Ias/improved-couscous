import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
import numpy as np
import time
from transformations import Transformation

class Loop:
    _title = "[Default Title]"
    
    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):
        screen_size = (1500, 500)
        Transformation.set_size(screen_size)
        ShaderObject.set_size(screen_size)
        ShaderObject.init_pygame_opengl()
        shader = ShaderObject.create_shader_program()
        VAO, EBO = ShaderObject.setup_textured_quad()

        textures = [
            ShaderObject.load_texture("facarambit.webp")["texture"],
            ShaderObject.load_texture("cachorro.jpg")["texture"],
            ShaderObject.load_texture("cachorro.jpg")["texture"]
        ]
        glUseProgram(shader)
        u_mvp_loc = glGetUniformLocation(shader, "u_mvp")
        u_tex_loc = glGetUniformLocation(shader, "u_texture")

        glUniform1i(u_tex_loc, 0)

        running = True
        clock = pg.time.Clock()
        start_time = time.time()

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT)

            current_time = time.time() - start_time

            transforms = [
                Transformation.affine_transform(( 600, 0), (200, 200), current_time),
                Transformation.affine_transform((  100, 0), (200, 200), -current_time * 0.5),
                Transformation.affine_transform((  400, 150), (100, 100), 0)
            ]
            
            for tex_id, mvp in zip(textures, transforms):
                glUniformMatrix4fv(u_mvp_loc, 1, GL_FALSE, mvp)
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            pg.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    Loop.start()