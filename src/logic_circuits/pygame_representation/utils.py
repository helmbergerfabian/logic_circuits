import pygame
from pygame.math import Vector2
from .colors import GRID

def draw_grid(surface, W, H, gap=24):
    for x in range(0, W, gap):
        pygame.draw.line(surface, GRID, (x, 0), (x, H))
    for y in range(0, H, gap):
        pygame.draw.line(surface, GRID, (0, y), (W, y))

def lerp(a, b, t):
    return a + (b - a) * t

def cubic_bezier(p0, p1, p2, p3, steps=30):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = lerp(p0, p1, t)
        b = lerp(p1, p2, t)
        c = lerp(p2, p3, t)
        d = lerp(a, b, t)
        e = lerp(b, c, t)
        f = lerp(d, e, t)
        pts.append((int(f.x), int(f.y)))
    return pts
