from abc import ABC, abstractmethod

from pygame import Surface, Rect

from scripts.player import PLAYER
from scripts.furniture import Furniture
from scripts.display import load_image, repeat_texture

from nostalgiaeraycasting import RayCaster


class Room(ABC):

    def __init__(self):
        self.caster: RayCaster = RayCaster()
        self.items: list[Furniture] = []
        self.collisions: list[Rect] = []

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


class LivingRoom(Room):
    def __init__(self):
        from scripts.furniture import Couch, TV, Drawer, LivingRoomWalls, Plant, Door, Window, Stairs
        super().__init__()
        self.items.append(TV(-0.23, 1., 0.3))
        self.items.append(Drawer(width=0.75, x=-0.3, y=0, z=0.23))
        self.items.append(Couch(width=0.8, height=1.2, length=1.5, x=-0.8, y=0, z=-1.5))
        self.items.append(LivingRoomWalls())
        self.items.append(Plant(x=2., y=0, z=-2.3))
        self.items.append(Door(x=-1.99, y=0, z=0.4, axis_x=False))
        self.items.append(Door(x=2.49, y=0, z=0., axis_x=False))
        self.items.append(Door(x=2.49, y=0, z=-2., axis_x=False))
        self.items.append(Window(x=-1., y=0.8, z=-2.99))
        self.items.append(Window(x=1., y=0.8, z=-2.99))
        self.items.append(Stairs(x=1.80, y=0, z=1.0, width=0.8))
        # self.items.append(BedRoomWalls())
        self.load_static_surfaces(self.caster)
        self.collisions = [
            Rect(-30, 30, 75, 75),  # TV
            Rect(-200, 100, 400, 10),  # FRONT
            Rect(-200, -300, 450, 10),  # BACK
            Rect(-200, -300, 10, 350),  # LEFT
            Rect(200, 100, 10, 300),  # INNER RIGHT
            Rect(250, -300, 10, 800),  # RIGHT
            Rect(-80, -230, 150, 80),  # COUCH
        ]

    def update(self, surface: Surface):
        super().update(surface)

