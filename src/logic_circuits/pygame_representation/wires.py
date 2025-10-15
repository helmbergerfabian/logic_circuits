import pygame
from pygame.math import Vector2
from .utils import cubic_bezier
from .colors import WIRE_FALSE, WIRE_TRUE, WIRE_HOT
from logic_circuits.gates.port import Port

class Wire:
    def __init__(self, start_port: Port, end_port: Port):
        assert start_port.kind == 'out' and end_port.kind == 'in'
        self.a = start_port
        self.b = end_port
        self.parent_gate = self.a.gate
        self.col = WIRE_FALSE
        # print(f"connecting {self.a, self.b}")
        # print(f"start {self.a.state,}")
        # print(f"end {self.b.state,}")


    def hit_test(self, mouse, tol=6):
        pts = self._points()
        mv = Vector2(mouse)
        for i in range(len(pts) - 1):
            p = Vector2(pts[i]); q = Vector2(pts[i + 1])
            if (q - p).length() < 1e-5:
                d = (mv - p).length()
            else:
                t = max(0, min(1, (mv - p).dot(q - p) / (q - p).length_squared()))
                proj = p + t * (q - p)
                d = (mv - proj).length()
            if d <= tol:
                return True
        return False

    def _points(self):
        p0 = self.a.screen_pos(); p3 = self.b.screen_pos()
        dx = max(40, abs(p3.x - p0.x) * 0.5)
        c1 = Vector2(p0.x + dx, p0.y); c2 = Vector2(p3.x - dx, p3.y)
        return cubic_bezier(p0, c1, c2, p3, steps=36)

    def draw(self, surf, hot=False):
        if not self.parent_gate.state[self.a.index]: self.col = WIRE_FALSE
        else: self.col = WIRE_TRUE
        
        pts = self._points()
        pygame.draw.lines(surf, WIRE_HOT if hot else self.col, False, pts, 3)
        if len(pts) >= 2:
            p_end, p_prev = Vector2(pts[-1]), Vector2(pts[-2])
            dirv = (p_end - p_prev).normalize() if (p_end - p_prev).length() else Vector2(1, 0)
            left = dirv.rotate(150) * 10; right = dirv.rotate(-150) * 10
            pygame.draw.polygon(surf, WIRE_HOT if hot else WIRE_FALSE, [p_end, p_end - left, p_end - right])