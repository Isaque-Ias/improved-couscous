from looping import GameLoop
from OpenGL.GL import *
from pygame.locals import *
from inputting import Input
from pathlib import Path
from entity import Entity
from entity import EntityTools as et
from texture import Texture
from vector import Vec, VecN
import pygame as pg
from math import log2

CWD = Path.cwd()
SOURCES = CWD / "app" / "sources"

class Phobos(Entity):
    def __init__(self):
        super().__init__(Vec(0, 0))
        UI()
        
class TabHelper(Entity):
    def __init__(self, details, children={}):
        super().__init__((0, 0))
        self.pos = details.get("pos")
        self.size = details.get("size")
        self.color = details.get("color")
        self.children = children
        for child in self.children:
            self.children[child].parent = self

    def render(self):
        et.draw_image(et.tex("pixel"), (self.pos + self.parent.pos + self.size / 2).unp(), self.size.unp(), color=(self.color/255).unp())

        for child in self.children:
            self.children[child].render()


class UI(Entity):
    def __init__(self):
        super().__init__(Vec(0, 0))
        screen_size = Vec(*et.get_screen_size())

        self.pos = (0, 0)
        self.size = screen_size
        self.structures = {}
        self.structures["math_tab"] = TabHelper(
            {"pos": Vec(0, 0), "size": Vec(300, screen_size[1]), "color": VecN(31, 22, 36)}, {
                "tab1": TabHelper({"pos": Vec(10, 10), "size": Vec(280, 100), "color": VecN(40, 27, 47)}),
                "tab2": TabHelper({"pos": Vec(10, 120), "size": Vec(280, 100), "color": VecN(40, 27, 47)}),
                "tab3": TabHelper({"pos": Vec(10, 230), "size": Vec(280, 100), "color": VecN(40, 27, 47)}),
                "tab4": TabHelper({"pos": Vec(10, 340), "size": Vec(280, 100), "color": VecN(40, 27, 47)}),
             })
        self.structures["math_tab"].parent = self

        self.proj_center = Vec(-self.size.x / 2 + 300 + (self.size.x - 300) / 2, 0)
        self.proj_zoom = 1
        self.proj_scale = 100
        self.target = ""
        self.click_pos = Vec(0, 0)
        self.click_proj_center = Vec(0, 0)

    def tick(self):
        if self.target == "projection":
            mouse_pos = Vec(*pg.mouse.get_pos())
            self.proj_center = mouse_pos - self.click_pos + self.click_proj_center
            if Input.mouse_released(0):
                self.target = ""
        if Input.mouse_scroll_y < 0:
            self.proj_zoom *= 0.9
            self.proj_center += ((Vec(*pg.mouse.get_pos()) - self.size / 2) - self.proj_center) * (1-0.9)
        if Input.mouse_scroll_y > 0:
            self.proj_zoom /= 0.9
            self.proj_center += ((Vec(*pg.mouse.get_pos()) - self.size / 2) - self.proj_center) * (1-1/0.9)
        self.proj_scale = (100 / 2 ** int(log2(self.proj_zoom))) * self.proj_zoom

        if Input.mouse_pressed(0):
            self.target = "projection"
            self.click_pos = Vec(*pg.mouse.get_pos())
            self.click_proj_center = self.proj_center

    def draw(self):
        et.draw_image(et.tex("pixel"), Vec(self.proj_center.x + self.size.x / 2, self.size.y / 2), (1, self.size.y))
        linex = 0
        while self.proj_center.x - self.size.x / 2 + linex < 0:
            et.draw_image(et.tex("pixel"), Vec(self.proj_center.x + self.size.x / 2 + linex, self.size.y / 2), (1, self.size.y), alpha=0.25)
            linex += self.proj_scale
        linex = 0
        while self.proj_center.x + self.size.x / 2 + linex > 0:
            et.draw_image(et.tex("pixel"), Vec(self.proj_center.x + self.size.x / 2 + linex, self.size.y / 2), (1, self.size.y), alpha=0.25)
            linex -= self.proj_scale
        liney = 0
        while self.proj_center.y - self.size.y / 2 + liney < 0:
            et.draw_image(et.tex("pixel"), Vec(self.size.x / 2, self.proj_center.y + self.size.y / 2 + liney), (self.size.x, 1), alpha=0.25)
            liney += self.proj_scale
        liney = 0
        while self.proj_center.y + self.size.y / 2 + liney > 0:
            et.draw_image(et.tex("pixel"), Vec(self.size.x / 2, self.proj_center.y + self.size.y / 2 + liney), (self.size.x, 1), alpha=0.25)
            liney -= self.proj_scale

        et.draw_image(et.tex("pixel"), Vec(self.size.x / 2, self.proj_center.y + self.size.y / 2), (self.size.x, 1))

        for structure in self.structures:
            self.structures[structure].render()

def pre_load_game():
    GameLoop.set_resizable(True)
    GameLoop.set_can_fullscreen(True)
    screen_size = (GameLoop.view_width - 100, GameLoop.view_height - 170)
    GameLoop.set_screen_size(screen_size)
    GameLoop.set_title("Physics")
    GameLoop.setup()
    GameLoop.set_background_color((VecN(21, 16, 23, 255) / 255).unp())

    Input.set_keys(K_SPACE, K_ESCAPE, K_LEFT, K_RIGHT, K_LSHIFT, K_LCTRL, K_v, K_t, K_1, K_2, K_3, K_4)

    Texture.set_texture("pixel", SOURCES / "build" / "pixel.png")
    
if __name__ == "__main__":
    pre_load_game()

    Phobos()

    GameLoop.start()