from typing import Generator
from math import sin, pi

from pygame.transform import scale
from pygame import Surface
from pygame import K_RETURN, K_ESCAPE, K_SPACE

from scripts.display import DISPLAY, lazy_load_images
from scripts.player import PLAYER


class SplashScreen:
    SPLASH_DURATION: float = 2.5

    def __init__(self):
        self.surface: Surface = Surface(DISPLAY.size)
        self.splash_generator: Generator = lazy_load_images("data", "splash_screen")
        self._splash_image: Surface | None = None
        self._counter: float = 0.
        self._skip = False

    @property
    def skip(self) -> bool:
        """Allow the player to skip a splash screen.
        Waits for the player to stop pressing the skip key before allowing the player to skip another splash screen.
        @return: True if the player skipped the splash screen, False otherwise."""
        if any(PLAYER.keys[key] for key in (K_RETURN, K_SPACE, K_ESCAPE)):
            if self._skip:
                return False
            self._skip = True
            return True
        self._skip = False
        return False



    def next(self) -> bool:
        """Set the splash image to the next image in the generator and return True if there is no more image.
        @return: True if there is no more image, False otherwise.
        """
        try:
            self._splash_image = self.splash_generator.__next__()
        except StopIteration:
            return True
        else:
            return False

    def blit(self) -> None:
        """Blit the splash image on the screen."""

        alpha: int = int(sin(pi * (self._counter / SplashScreen.SPLASH_DURATION)) * 255)

        self.surface.fill((0, 0, 0))  # Clear the screen

        facto: float = 1 - (self._counter / SplashScreen.SPLASH_DURATION) * 0.1
        temp = scale(self._splash_image, (self.surface.get_width() * facto, self.surface.get_height() * facto))

        temp.set_alpha(alpha)
        temp_center: tuple[int, int] = temp.get_rect().center
        surface_center: tuple[int, int] = self.surface.get_rect().center
        self.surface.blit(temp, (surface_center[0] - temp_center[0], surface_center[1] - temp_center[1]))

    def update(self) -> bool:
        """Update the splash screen.

        @return: True if all the images have been displayed, False otherwise.
        """
        if self._counter <= 0. or self.skip:
            if self.next():
                return True
            self._counter = SplashScreen.SPLASH_DURATION

        self.blit()
        DISPLAY.display(self.surface)
        self._counter -= DISPLAY.delta_time


SPLASH_SCREEN: SplashScreen = SplashScreen()
