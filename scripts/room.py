from abc import ABC, abstractmethod
from os.path import join as join_path
from math import sin, cos, radians, pi
from random import uniform, choice

from pygame import Surface, Rect
from pygame.mixer import Sound
from pygame import mouse

from scripts.player import PLAYER
from scripts.furniture import Furniture
from scripts.display import DISPLAY, load_image
from scripts.text import Text

from nostalgiaeraycasting import RayCaster
from nostalgiaefilters import distortion


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
        from scripts.furniture import TV, Couch, Drawer, LivingRoomWalls, Plant, Door, Window, Stairs, CorridorWalls, Frame
        super().__init__()
        self.items.append(TV(-0.23, 1., 0.3))

        self.init: bool = PLAYER.movements
        if PLAYER.movements:
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
            self.items.append(CorridorWalls())
            self.items.append(Door(x=1.8, y=2.0, z=3.99, ))
            self.items.append(Frame(x=-1.99, y=1.7, z=-2))

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
        from scripts.furniture import Couch, Drawer, LivingRoomWalls, Plant, Door, Window, Stairs, CorridorWalls, Frame
        super().update(surface)
        if PLAYER.movements and not self.init:
            self.init = True
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
            self.items.append(CorridorWalls())
            self.items.append(Door(x=1.8, y=2.0, z=3.99, ))
            self.items.append(Frame(x=-1.99, y=1.7, z=-2))
            self.load_static_surfaces(self.caster)

        if PLAYER.z >= 2.5:
            from scripts.game import GAME
            self.caster.clear_surfaces()
            GAME.CURRENT_ROOM = Corridor()


class Corridor(Room):
    def __init__(self):
        from scripts.furniture import LivingRoomWalls, Door, Stairs, CorridorWalls, BedRoomWalls, ClosetClosed
        super().__init__()
        self.items.append(Stairs(x=1.80, y=0, z=1.0, width=0.8))
        self.items.append(CorridorWalls())
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
            self.caster.clear_surfaces()
            GAME.CURRENT_ROOM = LivingRoom()
        if PLAYER.x < 1.:
            from scripts.game import GAME
            self.caster.clear_surfaces()
            GAME.CURRENT_ROOM = BedRoom()


class BedRoom(Room):
    def __init__(self):
        from scripts.furniture import Door, Stairs, CorridorWalls, BedRoomWalls, ClosetClosed, Bed, Drawer
        super().__init__()
        self.items.append(Stairs(x=1.80, y=0, z=1.0, width=0.8))
        self.items.append(CorridorWalls())
        self.items.append(Door(x=1.8, y=2.0, z=3.99, ))
        self.items.append(Door(x=1., y=2.0, z=3.01))
        self.items.append(Door(x=-0.5, y=2.0, z=3.01))
        self.items.append(Door(x=-1.38, y=2.0, z=3.4, axis_x=False))
        self.items.append(BedRoomWalls())
        self.items.append(ClosetClosed(x=-1.4, y=2, z=4.4))
        self.items.append(Bed(x=-1.5, y=2, z=6.))
        self.items.append(Drawer(width=1.2, x=-2., y=2, z=6.))

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
            self.caster.clear_surfaces()
            GAME.CURRENT_ROOM = Corridor()
        if PLAYER.z > 5.0:
            from scripts.game import GAME
            PLAYER.movements = False
            PLAYER.x = -0.5
            PLAYER.z = 5.5
            PLAYER.y = 2.
            PLAYER.rot_y = 220
            PLAYER.rot_x = 5.
            Sound(join_path("data", "sounds", "door.mp3")).play()
            self.caster.clear_surfaces()
            GAME.CURRENT_ROOM = BedRoomNightmare()


class BedRoomNightmare(Room):
    def __init__(self):
        from scripts.furniture import Door, CorridorWalls, BedRoomWalls, ClosetClosed, Bed
        super().__init__()
        self.items.append(CorridorWalls())
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
        from scripts.furniture import Door, CorridorWalls, BedRoomWalls, ClosetOpened, Bed, Eyes
        self._anim += DISPLAY.delta_time
        if self._anim >= 205:
            temp = Surface(GAME.SURFACE.get_size())
            distortion(GAME.SURFACE, temp, True, True, GAME.SURFACE.get_width() / 200, 0.1, 0.01)
            temp.set_alpha(30)
            GAME.SURFACE.blit(temp, (0, 0))

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
                    color=(255, 250, 250), fade_out=4.,
                    event=(lambda: (
                        GAME.set_room(LongCorridor()),
                        mouse.get_rel(),
                        PLAYER.__setattr__("movements", True),
                        PLAYER.__setattr__("x", 0),
                        PLAYER.__setattr__("z", 0),
                        PLAYER.__setattr__("y", 0),
                        PLAYER.__setattr__("rot_x", 0),
                        PLAYER.__setattr__("rot_y", 90),
                    ))
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
                    Sound(join_path("data", "sounds", "breath.wav")).play()
        elif self._anim >= 100:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3
            else:
                GAME.VIGNETTE = 1.5
            if self._anim > 103:
                GAME.TEXT = Text(
                    "Aren't you scared of the monster in the closet ?",
                    color=(255, 250, 250), fade_out=2.
                )
                self._anim = 200
        elif self._anim > 2.0:
            GAME.VIGNETTE += DISPLAY.delta_time * 3
            if GAME.VIGNETTE > 7.5:
                self.items: list = []
                self.items.append(CorridorWalls())
                self.items.append(Door(x=-1.38, y=2.0, z=3.99, ))
                self.items.append(BedRoomWalls())
                self.items.append(Bed(x=-1.5, y=2, z=6.))
                self.items.append(ClosetOpened(x=-1.4, y=2, z=4.4))
                self.caster.clear_surfaces()
                self.load_static_surfaces(self.caster)
                self._anim = 100


class LongCorridor(Room):
    def __init__(self):
        from scripts.furniture import LongCorridorWalls, Door, FloatingEye
        super().__init__()
        self.collisions = [
            Rect(-50, -50, 10, 3000),
            Rect(50, -50, 10, 3000),
            Rect(-50, -50, 100, 10),
        ]
        self.items.append(LongCorridorWalls(x=-0.5, z=-0.5))
        self.items.append(LongCorridorWalls(x=-0.5, z=11.5))
        self.items.append(LongCorridorWalls(x=-0.5, z=23.5))
        self.items.append(Door(x=-0.30, z=-0.5))
        self.items.append(Door(x=-0.49, z=1., axis_x=False))
        self.items.append(Door(x=0.49, z=3., axis_x=False))
        self.items.append(Door(x=-0.49, z=7., axis_x=False))
        self.items.append(Door(x=-0.49, z=10., axis_x=False))
        self.items.append(Door(x=0.49, z=15., axis_x=False))
        self.items.append(FloatingEye(x=-0.61, y=1.6, z=5))
        self.items.append(FloatingEye(x=0.7, y=1.4, z=11, texture=2))
        self.items.append(FloatingEye(x=-0.65, y=0.9, z=17, texture=3))

        self.load_static_surfaces(self.caster)
        self.rec_surf: Surface = Surface((150, 150))
        self.monster: bool = False

    def update(self, surface: Surface):
        from scripts.game import GAME
        z = 35.5
        # self.caster.add_surface(self.rec_surf.copy(), -0.49, 2.0, z, -0.49, 0, z + 1.0, rm=True)
        self.rec_surf.fill((0, 0, 0))
        self.caster.raycasting(
            self.rec_surf,
            PLAYER.x, PLAYER.height, 0,
            0, 90,
            PLAYER.FOV, PLAYER.VIEW_DISTANCE,
        )
        self.caster.add_surface(
            self.rec_surf.copy().convert_alpha(), -1.30 + PLAYER.x, 3.1, z, 1.30 + PLAYER.x, -0.1, z, rm=True
                                                  )

        super().update(surface)
        if not self.monster:
            if PLAYER.z > 20:
                from scripts.furniture import Monster
                self.items.append(Monster(speed=6, x=1.2, y=0, z=20, goal=(1.2, 0, 30)))
                self.monster = True
                Sound(join_path("data", "sounds", "door.mp3")).play()

        if PLAYER.z > 25:
            GAME.VIGNETTE += DISPLAY.delta_time * 3
            if GAME.VIGNETTE > 7.5:
                PLAYER.x = PLAYER.y = PLAYER.z = PLAYER.rot_x = 0
                PLAYER.rot_y = 90
                mouse.get_rel()
                self.caster.clear_surfaces()
                GAME.CURRENT_ROOM = InfiniteRoom()
                GAME.TEXT = Text("You can't trust what you see in the dark.")
        else:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3
            else:
                GAME.VIGNETTE = 1.5


class TheEnd(Room):
    def __init__(self):
        super().__init__()
        self.collisions = [
            Rect(-200, -50, 10, 400),
            Rect(200, -50, 10, 400),
            Rect(-200, -50, 400, 10),
            Rect(-200, 350, 400, 10),

            Rect(-50, 300, 60, 50),
        ]
        from scripts.furniture import EndTV
        self.items.append(EndTV(-0.5, 1, 3))
        # self.eyes: bool = False
        self.game = self.items[0].mini_game  # type: ignore

        self.load_static_surfaces(self.caster)
        self._anim = 0

    def update(self, surface: Surface):
        from scripts.game import GAME
        from scripts.furniture import FloatingEye, Monster
        if self.game.ev == 0:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3

        if not self.game.pause:
            while len(self.items) < 15:
                self.items.append(FloatingEye(
                    x=uniform(-8, 8), y=uniform(1.6, 6), z=uniform(-5, 10), width=0.5, height=0.4,
                    texture=choice((1, 2, 3))))  # type: ignore

            temp_list = [self.items[0]]
            for eye in self.items[1:]:
                temp_x = cos(radians(PLAYER.rot_y) - pi/2)
                temp_z = sin(radians(PLAYER.rot_y) - pi/2)
                if ((2 * temp_x) * (eye.z + temp_z) - (2 * temp_z) * (eye.x + temp_x)) >= 0.1:
                    temp_list.append(eye)

            self.items = temp_list

            # if not self.eyes:
            #     self.eyes = True
            #     self.items.append(FloatingEye(x=-2.5, y=2.5, z=5, width=0.5, height=0.4))
            #     self.items.append(FloatingEye(x=5, y=1.8, z=8, width=0.5, height=0.4, texture=2))
            #     self.items.append(FloatingEye(x=1.0, y=1.2, z=-5, width=0.5, height=0.4, texture=3))
            #
            #     self.items.append(FloatingEye(x=7, y=0.4, z=1., width=0.5, height=0.4))
            #     self.items.append(FloatingEye(x=-4, y=3., z=-1, width=0.5, height=0.4, texture=2))
            #     self.items.append(FloatingEye(x=-4, y=1.5, z=6, width=0.5, height=0.4, texture=3))
            #
            #     self.items.append(FloatingEye(x=3, y=5., z=10., width=0.5, height=0.4))
            #     self.items.append(FloatingEye(x=0.5, y=3., z=5, width=0.5, height=0.4, texture=2))
            #     self.items.append(FloatingEye(x=-8, y=0.2, z=2, width=0.5, height=0.4, texture=3))
            #
            #     self.items.append(FloatingEye(x=6, y=1., z=4, width=0.5, height=0.4))
            #     self.items.append(FloatingEye(x=-3, y=2., z=3, width=0.5, height=0.4, texture=2))
            #     self.items.append(FloatingEye(x=4, y=1.6, z=4, width=0.5, height=0.4, texture=3))

        if PLAYER.z > 2.35 and (-0.5 < PLAYER.x < -0.0):
            PLAYER.z = 2.45
            PLAYER.x = -0.2
            PLAYER.step_sound0.set_volume(0)
            PLAYER.step_sound1.set_volume(0)

        if self.game.background_deca > 200 and self.game.ev == 0:
            self.game.ev = 1
            self.items.append(Monster(x=20, y=0, z=6, goal=(0, 0, 6), speed=4))
            self.items.append(Monster(x=0, y=0, z=-50, goal=(0, 0, -2), speed=0.5))
            print("Monster spawned")
        if self.game.ev == 2:
            self._anim += DISPLAY.delta_time
            GAME.BG_COLOR = ((1 - cos(self._anim / 5)) * 25, 0, 0)
        elif self.game.ev == 3:
            GAME.VIGNETTE += DISPLAY.delta_time
            if GAME.VIGNETTE > 10.:
                GAME.STATE = GAME.STATE.TITLE_END
                Sound(join_path("data", "sounds", "breath.wav")).play()
        super().update(surface)

        if len(self.game.entities) > 1:
            temp1 = Surface(GAME.SURFACE.get_size())
            temp2 = Surface(GAME.SURFACE.get_size())
            temp3 = Surface(GAME.SURFACE.get_size())
            distortion(
                GAME.SURFACE, temp1, True, True,
                (20 - self.game.entities[1].life) * GAME.SURFACE.get_width() / 1500, 0.05, 0.01)
            temp1.set_alpha(50 - self.game.entities[1].life)
            distortion(
                GAME.SURFACE, temp2, True, True,
                (20 - self.game.entities[1].life) * GAME.SURFACE.get_width() / 1000, 0.01, 0.01)
            temp2.set_alpha(20 - self.game.entities[1].life)
            distortion(
                GAME.SURFACE, temp3, True, True,
                (20 - self.game.entities[1].life) * GAME.SURFACE.get_width() / 500, 0.005, 0.005)
            temp3.set_alpha((20 - self.game.entities[1].life) // 2)

            GAME.SURFACE.blit(temp1, (0, 0))
            GAME.SURFACE.blit(temp2, (0, 0))
            GAME.SURFACE.blit(temp3, (0, 0))

            if self.game.entities[1].damage_anim > 0.:
                temp4 = Surface(GAME.SURFACE.get_size())
                distortion(
                    GAME.SURFACE, temp4, True, True,
                    (20 - self.game.entities[1].life) * GAME.SURFACE.get_width() / 250, 100, 1
                )
                temp4.set_alpha(512 * self.game.entities[1].damage_anim)
                GAME.SURFACE.blit(temp4, (0, 0))
                GAME.VIGNETTE += DISPLAY.delta_time * 0.1


class InfiniteRoom(Room):
    def __init__(self):
        from scripts.furniture import InfiniteRoomWalls, FloatingEye
        super().__init__()

        self.walls = InfiniteRoomWalls(x=-0.5, z=-0.5)
        self.items.append(self.walls)

        self.items.append(FloatingEye(x=-0.3, y=1.8, z=0.1))
        self.items.append(FloatingEye(x=0.4, y=1.6, z=-0.4, texture=2))
        self.items.append(FloatingEye(x=0.9, y=1.7, z=0.6, texture=3))

        self.items.append(FloatingEye(x=0.6, y=1.9, z=1.2))
        self.items.append(FloatingEye(x=1.2, y=1.4, z=0.8, texture=2))
        self.items.append(FloatingEye(x=-0.4, y=1.5, z=1.3, texture=3))

        self.items.append(FloatingEye(x=1.4, y=1.9, z=-0.1))

        self.room_number = 0
        self.door_texture = load_image(join_path("data", "textures", "furniture", "door.png"))

        self.default_collisions = [
            Rect(-50, -50, 200, 10),
            Rect(-50, -50, 10, 200),
            Rect(-50, 150, 200, 10),
            Rect(150, -50, 10, 200),
        ]

        self.collisions = self.default_collisions + [Rect(50, -50, 10, 150)]
        self.load_static_surfaces(self.caster)

    def update(self, surface: Surface):
        from scripts.furniture import Plant
        from scripts.game import GAME
        self.walls.mode = self.room_number
        super().update(surface)

        if self.room_number < 3:
            if GAME.VIGNETTE > 1.5:
                GAME.VIGNETTE -= DISPLAY.delta_time * 3
            else:
                GAME.VIGNETTE = 1.5

        match self.room_number:
            case 0:
                self.caster.add_surface(self.door_texture, -0.2, 1.8, -0.49, 0.2, 0, -0.49, rm=True)
                if PLAYER.x > 0.5:
                    self.room_number = 1
                    self.collisions = self.default_collisions + [Rect(50, 0, 10, 100)]
            case 1:
                if PLAYER.z > 1.:
                    if PLAYER.x < 1.0:
                        self.caster.add_surface(self.door_texture, -0.2, 1.8, -0.49, 0.2, 0, -0.49, rm=True)
                    if PLAYER.x < 0.5:
                        self.room_number = 0
                        self.collisions = self.default_collisions + [Rect(50, -50, 10, 150)]
                else:
                    if PLAYER.z < 0.5:
                        self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                    if PLAYER.x < 0.5:
                        self.room_number = 2

            case 2:
                self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                if PLAYER.z < 1.:
                    if PLAYER.x > 0.5:
                        self.room_number = 1
                else:
                    self.room_number = 3
                    self.collisions = self.default_collisions + [Rect(50, 0, 10, 100), Rect(50, 50, 50, 10)]
                    self.items.append(Plant(x=0.75, z=0.75))
                    self.caster.clear_surfaces()
                    self.load_static_surfaces(self.caster)

            case 3:
                self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                if PLAYER.z < 1.:
                    if PLAYER.x < 0.5:
                        self.room_number = 2
                        self.items = self.items[:-1]
                        self.caster.clear_surfaces()
                        self.load_static_surfaces(self.caster)
                        self.collisions = self.default_collisions + [Rect(50, 0, 10, 100)]
                else:
                    if PLAYER.x > 0.5:
                        self.room_number = 4

            case 4:
                self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                if PLAYER.z > 1.:
                    if PLAYER.x < 0.5:
                        self.room_number = 3
                else:
                    if PLAYER.x > 0.5:
                        self.room_number = 5
                        self.collisions = self.default_collisions + [Rect(50, 50, 10, 50), Rect(0, 50, 100, 10)]

            case 5:
                self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                self.caster.add_surface(self.door_texture, -0.49, 1.8, -0.2, -0.49, 0, 0.2, rm=True)
                if PLAYER.z > 1.0:
                    if PLAYER.x > 0.5:
                        self.room_number = 4
                        self.collisions = self.default_collisions + [Rect(50, 0, 10, 100), Rect(50, 50, 50, 10)]
                else:
                    if PLAYER.x < 0.5:
                        self.room_number = 6
                        self.collisions = self.default_collisions

            case 6:
                self.caster.add_surface(self.door_texture, -0.49, 1.8, 0.9, -0.49, 0, 1.3, rm=True)
                self.caster.add_surface(self.door_texture, -0.49, 1.8, -0.2, -0.49, 0, 0.2, rm=True)
                GAME.VIGNETTE += DISPLAY.delta_time
                if GAME.VIGNETTE > 7.0:
                    GAME.TEXT = Text("Reality is not what it seems.")
                    self.caster.clear_surfaces()
                    GAME.CURRENT_ROOM = TheEnd()  # TODO: add more rooms
                    mouse.get_rel()
                    PLAYER.x = PLAYER.z = PLAYER.rot_x = 0
                    PLAYER.rot_y = 90
