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
        surface.blit(label, (self.rect.x + 10, self.rect.y + 10))

    def hover(self, pos):
        return self.rect.collidepoint(pos)


def _item_rect(index: int) -> pygame.Rect:
    return pygame.Rect(20, 40 + 50 * index, 100, 40)


def add_library_item(text, gate_class):
    item = LibraryItem(_item_rect(len(library_items)), text, gate_class)
    library_items.append(item)
    return item


library_items = []
add_library_item("AND", GateAND_graphical)
add_library_item("NOT", GateNOT_graphical)


dragging_library_item = None
ghost_gate = None
