from typing import enum, auto

from scripts.player import PLAYER
from scripts.splash_screen import SPLASH_SCREEN


class GAME_STATE(enum.Enum):
    SPLASH_SCREEN = auto()


class Game:

    def __init__(self):
        self.state = GAME_STATE.SPLASH_SCREEN

    def update(self):
        PLAYER.update_keys()

        match self.state:
            case GAME_STATE.SPLASH_SCREEN:
                SPLASH_SCREEN.update()
