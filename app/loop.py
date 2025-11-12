import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import time
from math import sin, cos

class Loop:
    _title = "[Default Title]"
    
    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):
        size = (1000, 500)
        ShaderObject.set_size(size)
        ShaderObject.init_pygame_opengl()
        shader = ShaderObject.create_shader_program()
        VAO, EBO = ShaderObject.setup_textured_quad()

        image = ShaderObject.load_texture("cachorro.jpg")
        texture = image["texture"]
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

            # 🌀 Compute rotation angle over time
            current_time = time.time() - start_time
            angle = current_time

            c, s = cos(angle), sin(angle)

            rotation_z = np.array([
                [ c, -s, 0, 0],
                [ s,  c, 0, 0],
                [ 0,  0, 1, 0],
                [ 0,  0, 0, 1],
            ], dtype=np.float32)

            scale_x = 1000 / size[0]#image["width"]
            scale_y = 500 / size[1]#image["height"]
            scaling = np.array([
                [2 * scale_x, 0, 0, 0],
                [0, 2 * scale_y, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ], dtype=np.float32)

            mvp = rotation_z @ scaling

            glUniformMatrix4fv(u_mvp_loc, 1, GL_FALSE, mvp)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture)
            glBindVertexArray(VAO)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            pg.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    Loop.start()