import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

class ShaderObject:
    screen_size = (800, 600)

    @classmethod
    def set_size(cls, size):
        cls.screen_size = size

    @classmethod
    def get_size(cls):
        return cls.screen_size

    @staticmethod
    def create_shader_program(vertex, fragment):
        shader = compileProgram(
            compileShader(vertex, GL_VERTEX_SHADER),
            compileShader(fragment, GL_FRAGMENT_SHADER)
        )
        return shader

    @classmethod
    def init_pygame_opengl(cls):
        pg.init()
        display = cls.screen_size

        pg.display.gl_set_attribute(pg.GL_MULTISAMPLEBUFFERS, 0)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, 0)

        pg.display.gl_set_attribute(pg.GL_ALPHA_SIZE, 8)
        pg.display.set_mode(display, DOUBLEBUF | OPENGL)
        pg.display.set_caption("test")

        glViewport(0, 0, display[0], display[1])
        glDisable(GL_MULTISAMPLE)
        
        glClearColor(0.0, 0.0, 0.0, 0.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    @classmethod
    def set_mvp(cls, mvp):
        cls.u_mvp_loc = mvp

    @classmethod
    def set_shader(cls, shader, mvp):
        glUseProgram(shader)
        cls.set_mvp(mvp)

    @staticmethod
    def load_texture(path):
        surface = pg.image.load(path)
        image = pg.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, image)

        glBindTexture(GL_TEXTURE_2D, 0)
        return {"texture": tex_id, "width": width, "height": height}
    
    @staticmethod
    def add_texture(texture):
        image = texture.tobytes("raw", "RGBA", 0, -1)
        width, height = texture.size

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, image)

        glBindTexture(GL_TEXTURE_2D, 0)
        return {"texture": tex_id, "width": width, "height": height}
    
    @staticmethod
    def setup_textured_quad():
        vertices = np.array([
            -0.5, -0.5, 0.0,   1, 1, 1,    0, 0,
            0.5, -0.5, 0.0,   1, 1, 1,    1, 0,
            0.5,  0.5, 0.0,   1, 1, 1,    1, 1,
            -0.5,  0.5, 0.0,   1, 1, 1,    0, 1,
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)

        glBindVertexArray(VAO)

        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 8 * vertices.itemsize
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        return VAO, EBO
    
    @classmethod
    def render(cls, mvp, texture):
        glUniformMatrix4fv(cls.u_mvp_loc, 1, GL_FALSE, mvp)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture["texture"])
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)