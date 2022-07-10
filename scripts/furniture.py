from typing import Literal
from abc import ABC, abstractmethod
from math import sin, cos, radians, pi
from random import randint

from pygame import Surface
from pygame import mouse

from scripts.display import load_image, repeat_texture, DISPLAY
from scripts.tv_mini_game import TvGame
from scripts.text import Text


class Furniture(ABC):
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x: float = x
        self.y: float = y
        self.z: float = z

    @abstractmethod
    def static_surfaces(self) -> list[tuple]:
        ...

    @abstractmethod
    def dynamic_surfaces(self) -> list[tuple]:
        ...


class Test(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_var: float = 0.0

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "test.png"),
             self.x-1, self.y+2, self.z+2,
             self.x+1, self.y+0, self.z+2)
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        self.my_var += 0.1
        from math import sin
        temp = 2 + sin(self.my_var)
        return [
            (load_image("data", "textures", "furniture", "test.png"),  # Don't actually load in the dynamic method
             self.x, self.y+temp, self.z+temp,
             self.x+temp, self.y, self.z+temp),
        ]


class Plant(Furniture):
    def __init__(self, height: float = 1.5, width: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height: float = height
        self.width: float = width
        self.texture: Surface = load_image("data", "textures", "furniture", "plant.png")

    def static_surfaces(self) -> list[tuple]:
        return []

    def dynamic_surfaces(self) -> list[tuple]:
        from scripts.player import PLAYER
        return [
            (self.texture,
             self.x - self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2), self.y + self.height, self.z - self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),
             self.x + self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2), self.y, self.z + self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),)
        ]


class TV(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size: float = 0.5
        self.mini_game: TvGame = TvGame()
        self.end_game: bool = False

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "tv", "tv0.png"),
             self.x, self.y + self.size, self.z,
             self.x + self.size, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x, self.y + self.size, self.z + self.size,
             self.x, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x + self.size, self.y + self.size, self.z + self.size,
             self.x + self.size, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x, self.y + self.size, self.z + self.size,
             self.x + self.size, self.y + self.size, self.z,
             self.x, self.y + self.size, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv2.png"),
             self.x, self.y + 2 * self.size, self.z + self.size / 2,
             self.x + self.size, self.y + self.size, self.z + self.size / 2),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        from scripts.player import PLAYER
        if abs(PLAYER.x - self.x) < 1.8 and abs(PLAYER.z - self.z) < 1.8:
            if self.mini_game.update() and not self.end_game:
                from scripts.game import GAME

                GAME.TEXT = Text("It's time to go to bed.",
                                 lambda: (
                                     mouse.get_rel(),
                                     PLAYER.__setattr__("movements", True)
                                 ),
                                 color=(15, 0, 0))
                GAME.VIGNETTE = 1.5
                self.end_game = True
        return [
            (self.mini_game.screen,
             self.x-0.01, self.y + self.size, self.z-0.001,
             self.x + self.size-0.1, self.y, self.z-0.001),
        ]


class Couch(Furniture):
    def __init__(self, width: float = 1, height: float = 1, length: float = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height: float = height
        self.width: float = width
        self.length: float = length

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # back
                self.x, self.y + self.height * 0.4, self.z,
                self.x + self.length, self.y, self.z),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # front
                self.x, self.y + self.height * 0.4, self.z - self.width,
                self.x + self.length, self.y, self.z - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # top
                self.x, self.y + self.height * 0.4, self.z,
                self.x + self.length, self.y + self.height * 0.4, self.z - self.width,
                self.x, self.y + self.height * 0.4, self.z - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # left
                self.x, self.y + self.height * 0.4, self.z,
                self.x, self.y, self.z - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # right
                self.x + self.length, self.y + self.height * 0.4, self.z,
                self.x + self.length, self.y, self.z - self.width),

            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # back
             self.x, self.y + self.height, self.z - self.width - self.width * 0.2,
             self.x + self.length, self.y, self.z - self.width,
             self.x, self.y, self.z - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # front
             self.x, self.y + self.height, self.z + self.width * 0.2 - self.width,
             self.x + self.length, self.y, self.z + self.width * 0.4 - self.width,
             self.x, self.y, self.z + self.width * 0.4 - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_texture.png"),  # top
             self.x, self.y + self.height, self.z - self.width - self.width * 0.2,
             self.x + self.length, self.y + self.height, self.z + self.width * 0.2 - self.width,
             self.x, self.y + self.height, self.z + self.width * 0.2 - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_side.png"),  # left
             self.x, self.y + self.height, self.z - self.width - self.width * 0.2,
             self.x, self.y, self.z + self.width * 0.4 - self.width),
            (load_image("data", "textures", "furniture", "couch", "couch_side.png"),  # right
             self.x + self.length, self.y + self.height, self.z - self.width - self.width * 0.2,
             self.x + self.length, self.y, self.z + self.width * 0.4 - self.width),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Drawer(Furniture):
    def __init__(self, width: float = 1, height: float = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height: float = height
        self.width: float = width

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "drawer", "drawer0.png"),
             self.x, self.y + self.height, self.z,
             self.x + self.width, self.y, self.z),
            (load_image("data", "textures", "furniture", "drawer", "drawer1.png"),
             self.x + 0.05 * self.width, self.y + self.height, self.z+self.width,
             self.x + 0.05 * self.width, self.y, self.z),
            (load_image("data", "textures", "furniture", "drawer", "drawer1.png"),
             self.x + self.width - 0.05 * self.width, self.y + self.height, self.z + self.width,
             self.x + self.width - 0.05 * self.width, self.y, self.z),
            (load_image("data", "textures", "furniture", "drawer", "drawer2.png"),
             self.x, self.y + self.height, self.z,
             self.x + self.width, self.y + self.height, self.z + self.width,
             self.x, self.y + self.height, self.z + self.width),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class LivingRoomWalls(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        left = self.x-2.
        right = self.x + 2.5
        top = self.y + 4
        bottom = self.y
        front = self.z + 1.
        back = self.z - 3.
        return [
            (repeat_texture(load_image("data", "textures", "wall", "woodfine.png"), 2, 2),
             left-0.1, bottom, front+0.1,
             right+0.1, bottom, back-0.1,
             left-0.1, bottom, back-0.1),
            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 2, 2),
             left-0.1, top, front+0.1,
             right+0.1, top, back-0.1,
             left-0.1, top, back-0.1),
            (load_image("data", "textures", "wall", "living_left_wall.png"),
             left, top, front,
             right, bottom, front,),
            (load_image("data", "textures", "wall", "living_left_wall.png"),
             left, top, back-0.01,
             left, bottom, front,),
            (repeat_texture(load_image("data", "textures", "wall", "livingwall.png"), 2, 2),
             right, top, back,
             left, bottom, back,),
            (repeat_texture(load_image("data", "textures", "wall", "livingwall.png"), 2, 2),
             right, top, front,
             right, bottom, back,),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Door(Furniture):
    def __init__(self, axis_x: bool = True, width: float = 0.6, height: float = 2., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_x: bool = axis_x
        self.height: float = height
        self.width: float = width

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "door.png"),
             self.x, self.y+self.height, self.z,
             self.x + (self.width if self.axis_x else 0), self.y, self.z + (0 if self.axis_x else self.width)),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Window(Furniture):
    def __init__(self, axis_x: bool = True, width: float = 0.4, height: float = 0.8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_x: bool = axis_x
        self.height: float = height
        self.width: float = width

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "window.png"),
             self.x, self.y+self.height, self.z,
             self.x + (self.width if self.axis_x else 0), self.y, self.z + (0 if self.axis_x else self.width)),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Stairs(Furniture):
    def __init__(self, length: float = 2., height: float = 2., width: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length: float = length
        self.height: float = height
        self.width: float = width

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "stairs.png"),
             self.x, self.y + self.height, self.z + self.length,
             self.x + self.width, self.y, self.z,
             self.x, self.y, self.z),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        from scripts.player import PLAYER
        if self.z < PLAYER.z < self.z + self.length and self.x < PLAYER.x < self.x + self.width:
            PLAYER.y = self.height * ((PLAYER.z - self.z) / self.length)
        return []


class Corridor(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "wall", "corridor_wall.png"),  # INNER
             self.x + 1.8, self.y + 5.5, self.z + 1.0,
             self.x + 1.8, self.y, self.z + 3.0,),
            (load_image("data", "textures", "wall", "corridor_wall.png"),  # RIGHT
             self.x + 2.5, self.y + 5.5, self.z + 1.0,
             self.x + 2.5, self.y, self.z + 4.0,),

            (load_image("data", "textures", "wall", "corridor_wall.png"),  # LEFT
             self.x - 2.0, self.y + 5.5, self.z + 3.0,
             self.x - 2.0, self.y + 1.9, self.z + 4.0,),

            (repeat_texture(load_image("data", "textures", "wall", "corridor_wall.png"), 2),  # BACK
             self.x - 2.0, self.y + 5.5, self.z + 3.0,
             self.x + 1.8, self.y + 1.9, self.z + 3.0,),

            (load_image("data", "textures", "wall", "corridor_wall_front.png"),  # FRONT
             self.x - 2.0, self.y + 5.5, self.z + 4.0,
             self.x + 2.5, self.y + 1.9, self.z + 4.0,),

            (load_image("data", "textures", "wall", "corridor_wall.png"),
             self.x + 1.8, self.y + 5., self.z + 3.,
             self.x + 2.5, self.y + 3., self.z + 1.,
             self.x + 1.8, self.y + 3., self.z + 1.,),

            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 2),
             self.x - 2, self.y + 5., self.z + 4.,
             self.x + 2.5, self.y + 4.99, self.z + 3.0,
             self.x - 2, self.y + 4.99, self.z + 3.0,),

            (repeat_texture(load_image("data", "textures", "wall", "light_wood.png"), 2),
             self.x - 2, self.y + 2., self.z + 4.,
             self.x + 2.5, self.y + 1.99, self.z + 3.0,
             self.x - 2, self.y + 1.99, self.z + 3.0,),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class BedRoomWalls(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        return [
            (repeat_texture(load_image("data", "textures", "wall", "light_wood.png"), 2, 2),
             self.x-2.5, self.y + 2., self.z+7.,
             self.x, self.y + 1.99, self.z+3.99,
             self.x-2.5, self.y + 1.99, self.z+3.99,),
            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 2, 2),
             self.x-2.5, self.y + 5., self.z+7.,
             self.x, self.y + 5., self.z+4.,
             self.x-2.5, self.y + 5., self.z+4.,),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png")),  # LEFT
             self.x - 2.5, self.y + 5.1, self.z + 4.,
             self.x - 2.5, self.y + 1.9, self.z + 7.),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png")),  # RIGHT
             self.x, self.y + 5.1, self.z + 7.,
             self.x, self.y + 1.9, self.z + 4.01),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png")),  # BACK
             self.x - 2.5, self.y + 5.1, self.z + 7.,
             self.x, self.y + 1.9, self.z + 7.),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png")),  # FRONT
             self.x - 4., self.y + 5.1, self.z + 4.,
             self.x - 2.0, self.y + 1.9, self.z + 4.),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class ClosetClosed(Furniture):
    def __init__(self, width: float = 0.8, length: float = 0.4, height: float = 1.8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.length = length
        self.height = height

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "closet", "closet.png"),
                self.x, self.y + self.height, self.z,
                self.x - self.width, self.y, self.z + self.length,),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width * 0.1, self.y + self.height, self.z + self.length * 0.1,
             self.x - self.width * 0.3, self.y, self.z - self.length,),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width + self.width * 0.05, self.y + self.height, self.z + self.length - self.length * 0.05,
             self.x - self.width - self.width * 0.2, self.y, self.z, - self.length * 0.1),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width * 0.3, self.y + self.height, self.z - self.length,
             self.x - self.width - self.width * 0.2, self.y, self.z, - self.length * 0.1),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class ClosetOpened(Furniture):
    def __init__(self, width: float = 0.8, length: float = 0.4, height: float = 1.8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.length = length
        self.height = height

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "closet", "open.png"),
                self.x, self.y + self.height, self.z,
                self.x - self.width, self.y, self.z + self.length,),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width * 0.1, self.y + self.height, self.z + self.length * 0.1,
             self.x - self.width * 0.3, self.y, self.z - self.length,),

            (load_image("data", "textures", "furniture", "closet", "door.png"),
             self.x - self.width * 0.06, self.y + self.height * 0.95, self.z + self.length * 0.1,
             self.x + self.width * 0.05, self.y + self.height * 0.06, self.z + self.length * 0.9,),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width + self.width * 0.05, self.y + self.height, self.z + self.length - self.length * 0.05,
             self.x - self.width - self.width * 0.2, self.y, self.z, - self.length * 0.1),

            (load_image("data", "textures", "furniture", "closet", "closet_side.png"),
             self.x - self.width * 0.3, self.y + self.height, self.z - self.length,
             self.x - self.width - self.width * 0.2, self.y, self.z, - self.length * 0.1),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Bed(Furniture):
    def __init__(self, width: float = 1.2, length: float = 1.6, height: float = 0.6, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.length = length
        self.height = height

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "bed", "bed_side.png"),  # back
             self.x, self.y + self.height, self.z,
             self.x + self.length, self.y, self.z),
            (load_image("data", "textures", "furniture", "bed", "bed_side.png"),  # front
             self.x, self.y + self.height, self.z - self.width,
             self.x + self.length, self.y, self.z - self.width),
            (load_image("data", "textures", "furniture", "bed", "bed_top.png"),  # top
             self.x, self.y + self.height, self.z,
             self.x + self.length, self.y + self.height, self.z - self.width,
             self.x, self.y + self.height, self.z - self.width),
            (load_image("data", "textures", "furniture", "bed", "bed_bottom.png"),  # left
             self.x, self.y + self.height, self.z,
             self.x, self.y, self.z - self.width),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class Eyes(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        return [
            (
                load_image("data", "textures", "furniture", "eyes.png"),
                self.x, self.y + 0.15, self.z,
                self.x + 0.15, self.y, self.z - 0.15,
            )
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class LongCorridorWalls(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "wall", "corridor_wall_front.png"),
             self.x, self.y + 3, self.z + 6,
             self.x, self.y, self.z),
            (repeat_texture(load_image("data", "textures", "wall", "corridor_wall.png"), 2),
             self.x + 1, self.y + 3, self.z + 6,
             self.x + 1, self.y, self.z),
            (load_image("data", "textures", "wall", "corridor_wall_front.png"),
             self.x + 1, self.y + 3, self.z + 12,
             self.x + 1, self.y, self.z + 6),
            (repeat_texture(load_image("data", "textures", "wall", "corridor_wall.png"), 2),
             self.x, self.y + 3, self.z + 12,
             self.x, self.y, self.z + 6),

            (repeat_texture(load_image("data", "textures", "wall", "light_wood.png"), 4),
             self.x - 0.1, self.y, self.z,
             self.x + 1.1, self.y, self.z + 12,
             self.x + 1.1, self.y, self.z),

            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 4),
             self.x - 0.1, self.y + 3, self.z,
             self.x + 1.1, self.y + 3, self.z + 12,
             self.x + 1.1, self.y + 3, self.z),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class FloatingEye(Furniture):
    def __init__(self, texture: Literal[1, 2, 3] = 1, width: float = 0.2, height: float = 0.15, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eye0: Surface = load_image("data", "textures", "furniture", "eyes", f"oeil{texture}0.png")
        self.eye1: Surface = load_image("data", "textures", "furniture", "eyes", f"oeil{texture}1.png")
        self.eye2: Surface = load_image("data", "textures", "furniture", "eyes", f"oeil{texture}2.png")
        self.width = width
        self.height = height
        self._anim: float = 0.
        self.blink: float = 0

    def static_surfaces(self) -> list[tuple]:
        return []

    def dynamic_surfaces(self) -> list[tuple]:
        from scripts.player import PLAYER

        if not randint(0, 200):
            self.blink = 6.

        if self.blink > 0:
            self.blink -= DISPLAY.delta_time * 6
        else:
            self.blink = 0

        temp = round(self.blink)

        surf = self.eye0
        match temp:
            case 3 | 1:
                surf = self.eye1
            case 2:
                surf = self.eye2
            case _: ...

        return [
            (surf,
             self.x - self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2),
             self.y + self.height / 2 * sin(radians(PLAYER.rot_x) + pi/2),
             self.z - self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),

             self.x + self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2),
             self.y - self.height / 2 * sin(radians(PLAYER.rot_x) + pi/2),
             self.z + self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),)
        ]


class Monster(Furniture):
    def __init__(self, speed: float = 1., goal: tuple[float, float, float] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.goal = goal
        self.width = 1.0
        self.height = 1.9
        self.texture = load_image("data", "textures", "furniture", "monstre.png")
        self.speed = speed

    def static_surfaces(self) -> list[tuple]:
        return []

    def dynamic_surfaces(self) -> list[tuple]:
        from scripts.player import PLAYER
        d = self.speed * DISPLAY.delta_time
        test: bool = True
        if abs(self.x - self.goal[0]) > d:
            test = False
            self.x += d * ((-1) ** (self.goal[0] < self.x))
        if abs(self.y - self.goal[1]) > d:
            test = False
            self.y += d * ((-1) ** (self.goal[1] < self.y))
        if abs(self.z - self.goal[2]) > d:
            test = False
            self.z += d * ((-1) ** (self.goal[2] < self.z))
        if test:
            return []
        return [
            (self.texture,
             self.x + self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2), self.y + self.height, self.z - self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),
             self.x - self.width / 2 * cos(radians(PLAYER.rot_y) + pi/2), self.y, self.z + self.width / 2 * sin(radians(PLAYER.rot_y) + pi/2),)
        ]


class EndTV(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size: float = 0.5
        self.mini_game: TvGame = TvGame(True)

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "tv", "tv0.png"),
             self.x, self.y + self.size, self.z,
             self.x + self.size, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x, self.y + self.size, self.z + self.size,
             self.x, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x + self.size, self.y + self.size, self.z + self.size,
             self.x + self.size, self.y, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv1.png"),
             self.x, self.y + self.size, self.z + self.size,
             self.x + self.size, self.y + self.size, self.z,
             self.x, self.y + self.size, self.z),
            (load_image("data", "textures", "furniture", "tv", "tv2.png"),
             self.x, self.y + 2 * self.size, self.z + self.size / 2,
             self.x + self.size, self.y + self.size, self.z + self.size / 2),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        if self.mini_game.update():
            from scripts.player import PLAYER
            from scripts.game import GAME
            # TODO
            # GAME.TEXT = Text("It's time to go to bed.",
            #                  lambda: (
            #                      mouse.get_rel(),
            #                      PLAYER.__setattr__("movements", True)
            #                  ),
            #                  color=(15, 0, 0),
            #                  sound="mum_text.wav")
            # GAME.VIGNETTE = 1.5
        return [
            (self.mini_game.screen,
             self.x-0.01, self.y + self.size, self.z-0.001,
             self.x + self.size-0.1, self.y, self.z-0.001),
        ]


class Frame(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height: float = 0.4
        self.width = 0.2

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "frame.png"),
             self.x, self.y + self.height, self.z,
             self.x, self.y, self.z + self.width),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []


class InfiniteRoomWalls(Furniture):
    def __init__(self, mode: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.width = 2.0
        self.height = 2.0
        self.texture = repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2)

    def static_surfaces(self) -> list[tuple]:
        return [
            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x, self.y + self.height, self.z,
                self.x + self.width, self.y, self.z),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x + self.width, self.y + self.height, self.z,
                self.x + self.width, self.y, self.z + self.width),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x + self.width, self.y + self.height, self.z + self.width,
                self.x, self.y, self.z + self.width),

            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x, self.y + self.height, self.z + self.width,
                self.x, self.y, self.z),

            (repeat_texture(load_image("data", "textures", "wall", "woodfine.png"), 2, 2),
             self.x-0.1, self.y, self.z-0.1,
             self.x + self.width + 0.1, self.y, self.z + self.width + 0.1,
             self.x-0.1, self.y, self.z + self.width + 0.1),

            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 2, 2),
             self.x - 0.1, self.y + 2, self.z - 0.1,
             self.x + self.width + 0.1, self.y + 1.99, self.z + self.width + 0.1,
             self.x - 0.1, self.y + 1.99, self.z + self.width + 0.1),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        match self.mode:
            case 0:
                return [(self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.75,
                         self.x + self.width // 2, self.y, self.z,)]
            case 1 | 2:
                return [(self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.75,
                         self.x + self.width // 2, self.y, self.z + self.width * 0.25,)]
            case 3 | 4:
                return [(self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.75,
                         self.x + self.width // 2, self.y, self.z + self.width * 0.5,),
                        (self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.5,
                         self.x + self.width // 2, self.y, self.z + self.width * 0.25,),

                        (self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.5,
                         self.x + self.width * 0.75, self.y, self.z + self.width * 0.5,)]
            case 5 | 6:
                return [(self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.75,
                         self.x + self.width // 2, self.y, self.z + self.width * 0.5,),

                        (self.texture,
                         self.x + self.width // 2, self.y + self.height, self.z + self.width * 0.5,
                         self.x + self.width * 0.75, self.y, self.z + self.width * 0.5,),
                        (self.texture,
                         self.x, self.y + self.height, self.z + self.width * 0.5,
                         self.x + self.width // 2, self.y, self.z + self.width * 0.5,),
                        ]

