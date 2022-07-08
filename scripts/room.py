from abc import ABC, abstractmethod
from os.path import join as join_path

from pygame import Surface, Rect
from pygame.mixer import Sound

from scripts.player import PLAYER
from scripts.furniture import Furniture
from scripts.display import DISPLAY
from scripts.text import Text

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
        from scripts.furniture import Couch, TV, Drawer, LivingRoomWalls, Plant, Door, Window, Stairs, Corridor
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
        self.items.append(Corridor())
        self.items.append(Door(x=1.8, y=2.0, z=3.99, ))

        # self.items.append(BedRoomWalls())
        self.load_static_surfaces(self.caster)
        self.collisions = [
            Rect(-30, 30, 75, 75),  # TV
            Rect(-200, 100, 400, 10),  # FRONT
            Rect(-200, -300, 450, 10),  # BACK
            Rect(-200, -300, 10, 400),  # LEFT
            Rect(200, 100, 10, 220),  # INNER RIGHT
            Rect(250, -300, 10, 800),  # RIGHT
            Rect(-80, -230, 150, 80),  # COUCH
        ]

    def update(self, surface: Surface):
        super().update(surface)

        if PLAYER.z >= 2.5:
            from scripts.game import GAME
            GAME.CURRENT_ROOM = Corridor()


class Corridor(Room):
    def __init__(self):
        from scripts.furniture import LivingRoomWalls, Door, Stairs, Corridor, BedRoomWalls, ClosetClosed
        super().__init__()
        self.items.append(Stairs(x=1.80, y=0, z=1.0, width=0.8))
        self.items.append(Corridor())
        self.items.append(LivingRoomWalls())
        self.items.append(Door(x=2.49, y=0, z=0., axis_x=False))
        self.items.append(Door(x=2.49, y=0, z=-2., axis_x=False))
        self.items.append(Door(x=1.8, y=2.0, z=3.99, ))
        self.items.append(Door(x=1., y=2.0, z=3.01))
        self.items.append(Door(x=-0.5, y=2.0, z=3.01))
        self.items.append(Door(x=-1.38, y=2.0, z=3.4, axis_x=False))
        self.items.append(BedRoomWalls())
        self.items.append(ClosetClosed(x=-1.4, y=2, z=4.4))

        self.collisions = [
            Rect(200, 100, 10, 220),  # INNER RIGHT
            Rect(250, -300, 10, 800),  # RIGHT
            Rect(-200, 300, 10, 100),  # LEFT
            Rect(-200, 300, 400, 10),  # BACK
            Rect(-200, 400, 450, 10),  # FRONT
        ]

        self.load_static_surfaces(self.caster)

    def update(self, surface: Surface):
        super().update(surface)

        if PLAYER.z < 2.5:
            from scripts.game import GAME
            GAME.CURRENT_ROOM = LivingRoom()
        if PLAYER.x < 1.:
            from scripts.game import GAME
            GAME.CURRENT_ROOM = BedRoom()


class BedRoom(Room):
    def __init__(self):
        from scripts.furniture import Door, Stairs, Corridor, BedRoomWalls, ClosetClosed, Bed
        super().__init__()
        self.items.append(Stairs(x=1.80, y=0, z=1.0, width=0.8))
        self.items.append(Corridor())
        self.items.append(Door(x=1.8, y=2.0, z=3.99, ))
        self.items.append(Door(x=1., y=2.0, z=3.01))
        self.items.append(Door(x=-0.5, y=2.0, z=3.01))
        self.items.append(Door(x=-1.38, y=2.0, z=3.4, axis_x=False))
        self.items.append(BedRoomWalls())
        self.items.append(ClosetClosed(x=-1.4, y=2, z=4.4))
        self.items.append(Bed(x=-1.5, y=2, z=6.))

        self.collisions = [
            Rect(200, 100, 10, 220),  # INNER RIGHT
            Rect(250, -300, 10, 800),  # RIGHT
            Rect(-200, 300, 10, 100),  # LEFT
            Rect(-250, 300, 10, 400),
            Rect(-250, 400, 110, 80),  # CLOSET
            Rect(-250, 700, 300, 10),
            Rect(0, 400, 10, 400),
            Rect(-200, 300, 400, 10),  # BACK
            Rect(-200, 400, 80, 10),  # FRONT
            Rect(-80, 400, 300, 10),  # FRONT
        ]

        self.load_static_surfaces(self.caster)

    def update(self, surface: Surface):
        super().update(surface)
        if PLAYER.x >= 1.:
            from scripts.game import GAME
            GAME.CURRENT_ROOM = Corridor()
        if PLAYER.z > 4.5:
            from scripts.game import GAME
            PLAYER.movements = False
            PLAYER.x = -0.5
            PLAYER.z = 5.5
            PLAYER.y = 2.
            PLAYER.rot_y = 220
            PLAYER.rot_x = 5.
            Sound(join_path("data", "sounds", "door.mp3")).play()
            GAME.CURRENT_ROOM = BedRoomNightmare()


class BedRoomNightmare(Room):
    def __init__(self):
        from scripts.furniture import Door, Corridor, BedRoomWalls, ClosetClosed, Bed
        super().__init__()
        self.items.append(Corridor())
        self.items.append(Door(x=-1.38, y=2.0, z=3.99, ))
        self.items.append(BedRoomWalls())
        self.items.append(ClosetClosed(x=-1.4, y=2, z=4.4))
        self.items.append(Bed(x=-1.5, y=2, z=6.))

        self._anim = 0

        self.collisions = [
            Rect(200, 100, 10, 220),  # INNER RIGHT
            Rect(250, -300, 10, 800),  # RIGHT
            Rect(-200, 300, 10, 100),  # LEFT
            Rect(-250, 300, 10, 400),
            Rect(-250, 400, 110, 80),  # CLOSET
            Rect(-250, 700, 300, 10),
            Rect(0, 400, 10, 400),
            Rect(-200, 300, 400, 10),  # BACK
            Rect(-200, 400, 80, 10),  # FRONT
            Rect(-80, 400, 300, 10),  # FRONT
        ]

        self.load_static_surfaces(self.caster)

    def update(self, surface: Surface):
        super().update(surface)
        from scripts.game import GAME
        from scripts.furniture import Door, Corridor, BedRoomWalls, ClosetOpened, Bed, Eyes
        self._anim += DISPLAY.delta_time
        if self._anim > 400:
            if GAME.VIGNETTE < 7.5:
                GAME.VIGNETTE += DISPLAY.delta_time * 3
        elif self._anim >= 300:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3
            else:
                GAME.VIGNETTE = 1.5
                GAME.TEXT = Text(
                    "Close your eyes. The night has only just begun.",
                    color=(255, 250, 250), sound="mum_text.wav", fade_out=4.,
                    event=(lambda: GAME.__setattr__("CURRENT_ROOM", ...))
                )
                if self._anim > 305:
                    self._anim = 400
        elif self._anim >= 200:
            if self._anim > 205:
                GAME.VIGNETTE += DISPLAY.delta_time * 3
                if GAME.VIGNETTE > 7.5:
                    self._anim = 300
                    self.items.append(Eyes(x=-1.65, y=3., z=4.7))
                    self.caster.clear_surfaces()
                    self.load_static_surfaces(self.caster)
        elif self._anim >= 100:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3
            else:
                GAME.VIGNETTE = 1.5
            if self._anim > 103:
                GAME.TEXT = Text(
                    "Aren't you scared of the monster in the closet ?",
                    color=(255, 250, 250), sound="mum_text.wav", fade_out=2.
                )
                self._anim = 200
        elif self._anim > 2.0:
            GAME.VIGNETTE += DISPLAY.delta_time * 3
            if GAME.VIGNETTE > 7.5:
                self.items: list = []
                self.items.append(Corridor())
                self.items.append(Door(x=-1.38, y=2.0, z=3.99, ))
                self.items.append(BedRoomWalls())
                self.items.append(Bed(x=-1.5, y=2, z=6.))
                self.items.append(ClosetOpened(x=-1.4, y=2, z=4.4))
                self.caster.clear_surfaces()
                self.load_static_surfaces(self.caster)
                self._anim = 100
