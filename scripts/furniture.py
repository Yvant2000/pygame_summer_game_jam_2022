from abc import ABC, abstractmethod

from scripts.display import load_image

from pygame import Surface


class Furniture(ABC):
    @abstractmethod
    def static_surfaces(self) -> list[tuple]:
        ...

    @abstractmethod
    def dynamic_surfaces(self) -> list[tuple]:
        ...


class Test(Furniture):
    def __init__(self):
        self.my_var: float = 0.0

    def static_surfaces(self) -> list[tuple]:
        return [
            (load_image("data", "textures", "furniture", "test.png"),
             -1, 2, 2,
             1, 0, 2)
        ]

    def dynamic_surfaces(self) -> list[tuple]:
        self.my_var += 0.1
        from math import sin
        temp = 2 + sin(self.my_var)
        return [
            (load_image("data", "textures", "furniture", "test.png"),
             0, temp, temp,
             temp, 0, temp),
        ]
