from enum import Enum, auto

from scripts.player import PLAYER
from scripts.splash_screen import SPLASH_SCREEN


class GAME_STATE(Enum):
    SPLASH_SCREEN = auto()
    MENU = auto()


class GAME:

    STATE: GAME_STATE = GAME_STATE.SPLASH_SCREEN

    @classmethod
    def update(cls):
        PLAYER.update_keys()

        match cls.STATE:
            case GAME_STATE.SPLASH_SCREEN:
                if SPLASH_SCREEN.update():
                    cls.STATE = GAME_STATE.MENU
