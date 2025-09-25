import pygame
from pygame.math import Vector2
from .colors import BLOCK_OUTL, PORT_IN, PORT_OUT, PORT_HOVER, TEXT
from . import fonts
from logic_circuits.gates.port import Port

class Port_graphical(Port):
    R = 7

    def __init__(self, gate, kind, offset, index):
        super().__init__()

        self.index = index
        self.gate = gate
        self.kind = kind  # 'in' or 'out'
        self.offset = Vector2(offset)

    @property
    def color(self):
        return PORT_IN if self.kind == 'in' else PORT_OUT

    def screen_pos(self):
        return Vector2(self.gate.rect.topleft) + self.offset

    def hover(self, mouse_pos):
        return (self.screen_pos() - Vector2(mouse_pos)).length() <= self.R + 2

    def draw(self, surf, hot=False):
        p = self.screen_pos()
        pygame.draw.circle(surf, BLOCK_OUTL, p, self.R + 2)
        pygame.draw.circle(surf, PORT_HOVER if hot else self.color, p, self.R)

        if fonts.FONT:
            label = fonts.FONT.render(str(self.index), True, TEXT)
            if self.kind == "in": dir = +15
            else: dir = -(15+self.R)
            surf.blit(label, (p[0] + dir, p[1] - 1.3*self.R))