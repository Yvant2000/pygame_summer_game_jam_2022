from typing import Sequence

from pygame import key


class Player:
    def __init__(self):
        self._keys: Sequence = []

    def update_keys(self):
        self._keys = key.get_pressed()

    @property
    def keys(self) -> Sequence:
        return self._keys


PLAYER: Player = Player()
