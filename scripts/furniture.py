from abc import ABC, abstractmethod

from scripts.display import load_image, repeat_texture
from scripts.tv_mini_game import TvGame

from pygame import Surface


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
            (load_image("data", "textures", "furniture", "test.png"),
             self.x, self.y+temp, self.z+temp,
             self.x+temp, self.y, self.z+temp),
        ]


class TV(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size: float = 0.5
        self.mini_game: TvGame = TvGame()

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
            ...
        return [
            (self.mini_game.screen,
             self.x-0.01, self.y + self.size, self.z-0.001,
             self.x + self.size-0.1, self.y, self.z-0.001),
        ]


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


class BedRoomWalls(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static_surfaces(self) -> list[tuple]:
        return [
            (repeat_texture(load_image("data", "textures", "wall", "light_wood.png"), 2, 2),
             self.x-2.01, self.y, self.z+1.01,
             self.x + 2.51, self.y, self.z-2.01,
             self.x-2.01, self.y, self.z-2.01,),
            (repeat_texture(load_image("data", "textures", "wall", "ceiling.png"), 2, 2),
             self.x-2.01, self.y + 3, self.z+1.01,
             self.x + 2.51, self.y + 3, self.z - 2.01,
             self.x - 2.01, self.y + 3, self.z - 2.01,),
            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
             self.x-2, self.y+3, self.z+1,
             self.x + 2.5, self.y, self.z+1,),
            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x-2, self.y+3, self.z-2,
                self.x-2, self.y, self.z+1,),
            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
                self.x+2.5, self.y+3, self.z-2,
                self.x-2, self.y, self.z-2,),
            (repeat_texture(load_image("data", "textures", "wall", "flower_wall.png"), 2, 2),
             self.x + 2.5, self.y + 3, self.z + 1,
             self.x + 2.5, self.y, self.z - 2,),
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        return []
