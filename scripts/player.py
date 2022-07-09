from typing import Sequence
from os.path import join as join_path
from math import sin, cos, radians, pi

from pygame import Rect
from pygame import key, mouse
from pygame import K_ESCAPE, K_RETURN, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_w, K_a, K_s, K_d
from pygame.mixer import Sound

from scripts.display import DISPLAY

d_pi: float = pi / 2


class Player:
    def __init__(self):
        self._keys: Sequence = []
        self.movements: bool = True  # TODO: set this to False

        self.x: float = -0.01
        self.y: float = 0.
        self.z: float = 0.1

        self.height: float = 1.2

        self.speed: float = 1.4

        self.rot_x: float = 7.0
        self.rot_y: float = 93.6

        self.FOV: float = 80.
        self.VIEW_DISTANCE: float = 50.

        self.mouse_sensitivity: float = 0.05

        self.step_sound0: Sound = Sound(join_path("data", "sounds", "step0.mp3"))
        self.step_sound1: Sound = Sound(join_path("data", "sounds", "step1.mp3"))
        # self.step_wood: Sound = Sound(join_path("data", "sounds", "wood_step.mp3"))

        self.step: float = 0.1
        self.foot: bool = True

    @property
    def skip(self) -> bool:
        return any(self._keys[k] for k in (K_RETURN, K_SPACE, K_ESCAPE))

    @property
    def keys(self) -> Sequence:
        return self._keys

    def update_keys(self):
        self._keys = key.get_pressed()

    def test_collisions(self, collisions: Sequence[Rect]):
        """Return True if the player is colliding with any of the given rectangles."""
        rect = Rect(self.x * 100, self.z * 100, 20, 20)
        return rect.collidelist(collisions) != -1

    def move(self, screen_size_mult: float = 1., collisions: list[Rect] | None = None):
        assert self.movements, "move method called while movements are blocked"

        if collisions is None:
            collisions = []

        delta: float = DISPLAY.delta_time

        if self.step <= 0:
            (self.step_sound1 if self.foot else self.step_sound0).play()
            self.foot = not self.foot
            self.step = 0.7

        if mouse.get_focused() and key.get_focused():

            rel = mouse.get_rel()
            self.rot_x -= float(rel[1]) * self.mouse_sensitivity
            self.rot_y = (self.rot_y - float(rel[0]) * self.mouse_sensitivity) % 360
            self.rot_x = max(min(self.rot_x, 35 - self.y * 3), -35 + self.y * 3)

            if rel[0] or rel[1]:
                mouse.set_pos(DISPLAY.width // 2, DISPLAY.height // 2)

        save = self.z, self.x
        moved = False

        if self._keys[K_w] or self._keys[K_UP]:
            moved = True
            self.z += delta * self.speed * sin(radians(self.rot_y))
            if self.test_collisions(collisions):
                self.z = save[0]
            self.x += delta * self.speed * cos(radians(self.rot_y))
            if self.test_collisions(collisions):
                self.x = save[1]
        elif self._keys[K_s] or self._keys[K_DOWN]:
            moved = True
            self.z -= delta * self.speed * sin(radians(self.rot_y))
            if self.test_collisions(collisions):
                self.z = save[0]
            self.x -= delta * self.speed * cos(radians(self.rot_y))
            if self.test_collisions(collisions):
                self.x = save[1]

        if self._keys[K_a] or self._keys[K_LEFT]:
            moved = True
            self.z += delta * self.speed * sin(radians(self.rot_y) + d_pi)
            if self.test_collisions(collisions):
                self.z = save[0]
            self.x += delta * self.speed * cos(radians(self.rot_y) + d_pi)
            if self.test_collisions(collisions):
                self.x = save[1]
        elif self._keys[K_d] or self._keys[K_RIGHT]:
            moved = True
            self.z -= delta * self.speed * sin(radians(self.rot_y) + d_pi)
            if self.test_collisions(collisions):
                self.z = save[0]
            self.x -= delta * self.speed * cos(radians(self.rot_y) + d_pi)
            if self.test_collisions(collisions):
                self.x = save[1]

        if moved:
            self.step -= delta
        else:
            self.step = 0.1


PLAYER: Player = Player()
