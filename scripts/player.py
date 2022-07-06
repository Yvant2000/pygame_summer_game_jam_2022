from typing import Sequence

from pygame import key
from pygame import K_ESCAPE, K_RETURN, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_w, K_a, K_s, K_d


class Player:
    def __init__(self):
        self._keys: Sequence = []
        self.movements: bool = True

        self.x: float = 0.
        self.y: float = 0.
        self.z: float = 0.

        self.rot_x: float = 0.
        self.rot_y: float = 0.

    @property
    def skip(self) -> bool:
        return any(self._keys[k] for k in (K_RETURN, K_SPACE, K_ESCAPE))

    @property
    def keys(self) -> Sequence:
        return self._keys

    def update_keys(self):
        self._keys = key.get_pressed()

    def move(self):
        assert self.movements, "move method called while movements are blocked"


PLAYER: Player = Player()
