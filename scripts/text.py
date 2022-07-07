from os.path import join as join_path

from pygame.font import Font
from pygame import Surface
from pygame.transform import scale
from pygame.mixer import Sound

from scripts.display import DISPLAY


class Text:
    def __init__(self, text: str, event: callable = None, font: str = "Pixel.ttf",
                 color: tuple[int, int, int] = (255, 255, 255), fade_out: float = 5.0,
                 sound: str = None):
        self.text: str = text
        self.event: callable = event
        self.font: Font = Font(join_path("data", "fonts", font), 50)
        self.color: tuple[int, int, int] = color
        self.size = self.font.render(self.text, True, self.color).get_size()
        self.counter: float = 0
        self.letters: int = 0
        self.fade_out: float = fade_out
        self.sound: Sound | None = None if sound is None else Sound(join_path("data", "sounds", sound))

    def draw(self, surface: Surface, center_x: int, center_y: int) -> bool:
        self.counter += DISPLAY.delta_time
        temp = int(self.counter * 10)
        if self.letters < temp < len(self.text):
            self.letters = temp
            if self.sound is not None:
                self.sound.play()
        text = self.text[:temp]
        render = self.font.render(text, True, self.color)
        render = scale(
            render,
            (render.get_width() * surface.get_width() * 0.75 / self.size[0],
             render.get_height() * surface.get_width() * 0.75 / self.size[0])
        )
        surface.blit(render, (center_x - render.get_width() / 2, center_y - render.get_height() / 2))

        if temp < len(self.text):
            return False

        if self.event is not None:
            self.event()
            self.event = None

        self.fade_out -= DISPLAY.delta_time
        if self.fade_out > 0:
            return False

        return True
