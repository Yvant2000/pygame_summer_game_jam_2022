from typing import Sequence

from math import sin, cos, radians, pi

from pygame import key, mouse
from pygame import K_ESCAPE, K_RETURN, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_w, K_a, K_s, K_d

from scripts.display import DISPLAY

d_pi: float = pi / 2


class Player:
    def __init__(self):
        self._keys: Sequence = []
        self.movements: bool = False

        self.x: float = -0.01
        self.y: float = 0.
        self.z: float = 0.1

        self.height: float = 1.2

        self.speed: float = 2.5

        self.rot_x: float = 7.0
        self.rot_y: float = 93.6

        self.FOV: float = 80.
        self.VIEW_DISTANCE: float = 50.

        self.mouse_sensitivity: float = 0.05

    @property
    def skip(self) -> bool:
        return any(self._keys[k] for k in (K_RETURN, K_SPACE, K_ESCAPE))

    @property
    def keys(self) -> Sequence:
        return self._keys

    def update_keys(self):
        self._keys = key.get_pressed()

    def move(self, screen_size_mult: float = 1.):
        assert self.movements, "move method called while movements are blocked"

        delta: float = DISPLAY.delta_time

        if mouse.get_focused() and key.get_focused():

            rel = mouse.get_rel()
            self.rot_x -= float(rel[1]) * self.mouse_sensitivity
            self.rot_y = (self.rot_y - float(rel[0]) * self.mouse_sensitivity) % 360
            self.rot_x = max(min(self.rot_x, 35), -35)

            if rel[0] or rel[1]:
                mouse.set_pos(DISPLAY.width // 2, DISPLAY.height // 2)

        if self._keys[K_w] or self._keys[K_UP]:
            self.z += delta * self.speed * sin(radians(self.rot_y))
            self.x += delta * self.speed * cos(radians(self.rot_y))
        elif self._keys[K_s] or self._keys[K_DOWN]:
            self.z -= delta * self.speed * sin(radians(self.rot_y))
            self.x -= delta * self.speed * cos(radians(self.rot_y))

        if self._keys[K_a] or self._keys[K_LEFT]:
            self.z += delta * self.speed * sin(radians(self.rot_y) + d_pi)
            self.x += delta * self.speed * cos(radians(self.rot_y) + d_pi)
        elif self._keys[K_d] or self._keys[K_RIGHT]:
            self.z -= delta * self.speed * sin(radians(self.rot_y) + d_pi)
            self.x -= delta * self.speed * cos(radians(self.rot_y) + d_pi)


PLAYER: Player = Player()
