from pygame import Surface

from scripts.display import load_image, DISPLAY


class END_SCREEN:
    END_SURFACE: Surface = load_image("data", "end", "end.png")
    ALPHA: int = 0

    @classmethod
    def blit(cls):
        cls.ALPHA += DISPLAY.delta_time * 20
        if cls.ALPHA > 255:
            cls.alpha = 255
        cls.END_SURFACE.set_alpha(int(cls.ALPHA))
        temp = Surface(cls.END_SURFACE.get_size())
        temp.fill((0, 0, 0))
        temp.blit(cls.END_SURFACE, (0, 0))
        DISPLAY.display(temp)
