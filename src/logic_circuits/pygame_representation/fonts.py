import pygame

FONT = None

def init():
    """Initialize global fonts (call after pygame.init())."""
    global FONT
    FONT = pygame.font.SysFont("consolas", 18)
