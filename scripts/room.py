from abc import ABC, abstractmethod

from pygame import Surface

from scripts.player import PLAYER
from scripts.furniture import Furniture, Test, TV, BedRoomWalls, Drawer
from scripts.display import load_image, repeat_texture

from nostalgiaeraycasting import RayCaster


class Room(ABC):

    def __init__(self):
        self.caster: RayCaster = RayCaster()
        self.items: list[Furniture] = []

    def load_static_surfaces(self, caster):
        for item in self.items:
            for surface in item.static_surfaces():
                caster.add_surface(*surface, rm=False)

    def load_dynamic_surfaces(self, caster):
        for item in self.items:
            for surface in item.dynamic_surfaces():
                caster.add_surface(*surface, rm=True)

    @abstractmethod
    def update(self, surface: Surface):
        self.load_dynamic_surfaces(self.caster)
        self.caster.raycasting(
            surface,
            PLAYER.x, PLAYER.y + PLAYER.height, PLAYER.z,
            PLAYER.rot_x, PLAYER.rot_y,
            PLAYER.FOV,
            PLAYER.VIEW_DISTANCE,
        )


class BedRoom(Room):
    def __init__(self):
        super().__init__()
        self.items.append(TV(-0.23, 1., 0.3))
        self.items.append(Drawer(width=0.75, x=-0.3, y=0, z=0.23))
        self.items.append(BedRoomWalls())
        self.load_static_surfaces(self.caster)

    def update(self, surface: Surface):
        super().update(surface)
