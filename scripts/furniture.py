from abc import ABC, abstractmethod

from scripts.display import load_image

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
        return []
