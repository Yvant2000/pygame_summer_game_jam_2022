from pygame import Surface
from pygame.transform import scale
from pygame import mouse

from scripts.display import DISPLAY, load_image
from scripts.player import PLAYER


class PauseMenu:
    def __init__(self):
        self._paused_surface: Surface | None = None
        self.pause_menu_image = load_image("data", "pause_menu", "pause_menu.png").convert_alpha()
        self._enter_pressed: bool = True

    @property
    def paused_surface(self) -> Surface:
        return self._paused_surface

    @paused_surface.setter
    def paused_surface(self, surf: Surface) -> None:
        self._paused_surface = surf.copy()

    def update(self) -> bool:
        """
        Display the pause menu on the screen.
        The pause_surface must be set before calling this function.
        @return: True if the player pressed the enter key, False otherwise.
        """
        assert self._paused_surface is not None, "The pause_surface must be set before calling this function."

        mouse.set_visible(True)

        surf: Surface = Surface(self.paused_surface.get_size())
        surf.blit(self._paused_surface, (0, 0))
        temp = scale(self.pause_menu_image, surf.get_size())
        surf.blit(temp, (0, 0))
        DISPLAY.display(surf)

        if PLAYER.skip:
            if self._enter_pressed:
                return False
            self._enter_pressed = True
            mouse.set_visible(False)
            return True
        self._enter_pressed = False
        return False


PAUSE_MENU: PauseMenu = PauseMenu()
