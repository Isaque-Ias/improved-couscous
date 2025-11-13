import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
from transformations import Transformation
from entity import EntityManager, Entity
from texture import Texture

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

        glUseProgram(shader)
        u_mvp_loc = glGetUniformLocation(shader, "u_mvp")
        u_tex_loc = glGetUniformLocation(shader, "u_texture")

        glUniform1i(u_tex_loc, 0)

        running = True
        clock = pg.time.Clock()

        FPS = 60

        Texture.set_texture("faca", "facarambit.webp")
        entity = []
        entity.append(Entity((200, 200), Texture.get_texture("faca"), (200, 200), 34, 0))
        entity.append(Entity((300, 200), Texture.get_texture("faca"), (200, 200), 34, 0))
        entity.append(Entity((400, 200), Texture.get_texture("faca"), (200, 200), 34, 0))
        entity.append(Entity((500, 200), Texture.get_texture("faca"), (200, 200), 34, 0))
        EntityManager.create_entity(entity)

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT)

            for entity in EntityManager.get_all_layer_entities():
                mvp = entity.get_mvp()
                glUniformMatrix4fv(u_mvp_loc, 1, GL_FALSE, mvp)
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, entity.get_texture())
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            pg.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    Loop.start()