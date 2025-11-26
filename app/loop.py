import pygame as pg
from pygame.locals import *
from shaders import ShaderObject
from OpenGL.GL import *
from transformations import Transformation
from entity import EntityManager, EntityTools
from texture import Texture
from inputting import Input
from game import Map, Player, Commander
from camera import Camera
from testing import Testing

class Loop:
    _title = "[Default Title]"
    
    @classmethod
    def set_title(cls, t):
        cls._title = t

    @classmethod
    def start(cls):

        with open("app\\shaders\\def.vsh", "r") as file:
            DEF_VERTEX_SHADER = file.read()
        with open("app\\shaders\\def.fsh", "r") as file:
            DEF_FRAGMENT_SHADER = file.read()

        with open("app\\shaders\\map.vsh", "r") as file:
            MAP_VERTEX_SHADER = file.read()
        with open("app\\shaders\\map.fsh", "r") as file:
            MAP_FRAGMENT_SHADER = file.read()

        with open("app\\shaders\\screen.vsh", "r") as file:
            SCREEN_VERTEX_SHADER = file.read()
        with open("app\\shaders\\screen.fsh", "r") as file:
            SCREEN_FRAGMENT_SHADER = file.read()

        screen_size = (1200, 600)
        Transformation.set_size(screen_size)
        ShaderObject.set_size(screen_size)
        ShaderObject.init_pygame_opengl()
        default_shader = ShaderObject.create_shader_program(DEF_VERTEX_SHADER, DEF_FRAGMENT_SHADER)
        map_shader = ShaderObject.create_shader_program(MAP_VERTEX_SHADER, MAP_FRAGMENT_SHADER)
        screen_shader = ShaderObject.create_shader_program(SCREEN_VERTEX_SHADER, SCREEN_FRAGMENT_SHADER)
        ShaderObject.setup_textured_quad()

        running = True
        clock = pg.time.Clock()

        FPS = 60

        Texture.set_texture("player", "app\\sources\\player.png")
        Texture.set_texture("pixel", "app\\sources\\pixel.png")

        glUseProgram(default_shader)

        map_u_mvp_loc = glGetUniformLocation(map_shader, "u_mvp")
        map_u_player_loc = glGetUniformLocation(map_shader, "u_player")
        map_u_cam_loc = glGetUniformLocation(map_shader, "u_cam")
        map_u_cam_scale_loc = glGetUniformLocation(map_shader, "u_cam_scale")
        map_u_screen_loc = glGetUniformLocation(map_shader, "u_screen")
        map_u_time_loc = glGetUniformLocation(map_shader, "u_time")
        map_u_time_cap_loc = glGetUniformLocation(map_shader, "u_time_cap")
        
        def_u_mvp_loc = glGetUniformLocation(default_shader, "u_mvp")
        def_u_tex_loc = glGetUniformLocation(default_shader, "u_texture")
        def_u_tex_loc = glGetUniformLocation(default_shader, "u_texture")

        screen_u_mvp_loc = glGetUniformLocation(screen_shader, "u_mvp")
        screen_u_color_loc = glGetUniformLocation(screen_shader, "u_color")

        EntityManager.set_mvp(def_u_mvp_loc)

        cam = Camera.get_main_camera()
        cam.set_scale((5, 5))

        player = Player((0, 0), "russo")
        game_map = Map()

        Input.set_keys(K_w, K_a, K_s, K_d, K_SPACE, K_t,K_LCTRL, K_UP, K_DOWN)

        Testing.set_def_cap(1000)

        Commander.set_context({
            "map": game_map
        })
        Commander.set_font(pg.font.Font("app\\sources\\fonts\\game_font.ttf", 18))

        EntityTools.set_color_loc(screen_u_color_loc)


        while running:
            Input.update()

            glClear(GL_COLOR_BUFFER_BIT)
            glClearColor(98 / 255, 168 / 255, 242 / 255, 0.0)

            ShaderObject.set_shader(map_shader, map_u_mvp_loc)
            glUniform1i(map_u_time_loc, game_map.time)
            glUniform2f(map_u_player_loc, player.x, player.y)
            
            main_cam_x, main_cam_y = Camera.get_main_camera().get_pos()
            main_cam_sc_x, main_cam_sc_y = Camera.get_main_camera().get_scale()
            
            glUniform2f(map_u_cam_loc, main_cam_x, main_cam_y)
            glUniform2f(map_u_cam_scale_loc, main_cam_sc_x, main_cam_sc_y)

            glUniform1i(map_u_time_loc, game_map.time)
            glUniform1i(map_u_time_cap_loc, game_map.time_cap)

            glUniform2f(map_u_screen_loc, screen_size[0], screen_size[1])

            game_map.tick()
            game_map.draw()

            ShaderObject.set_shader(default_shader, def_u_mvp_loc)
            glUniform1i(def_u_tex_loc, 0)

            entities = EntityManager.get_all_entities()
            for layer in EntityManager.get_content_layers():
                for entity in entities[layer]:
                    entity.tick()

            for layer in EntityManager.get_content_layers():
                for entity in entities[layer]:
                    entity.draw()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    print(Testing.get_relatory())

            ShaderObject.set_shader(screen_shader, screen_u_mvp_loc)
            Commander.draw()

            pg.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    Loop.start()