import pygame
from . import fonts
from .gates_graphical import GateAND_graphical, GateNOT_graphical
from .pygame_cfg import *

class LibraryItem:
    def __init__(self, rect, text, gate_class):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.gate_class = gate_class

    def draw(self, surface):
        pygame.draw.rect(surface, (60, 60, 60), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        label = fonts.FONT.render(self.text, True, (255, 255, 255))
        surface.blit(label, (self.rect.x+10, self.rect.y+10))

    def hover(self, pos):
        return self.rect.collidepoint(pos)

library_items = [
    LibraryItem((20, 40, 100, 40), "AND", GateAND_graphical),
    LibraryItem((20, 40+50*1, 100, 40), "NOT", GateNOT_graphical),
]

dragging_library_item = None
ghost_gate = None