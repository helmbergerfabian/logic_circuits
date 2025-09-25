import pygame
from .ports import Port_graphical
from .colors import BLOCK_FILL, BLOCK_OUTL, TEXT
from . import fonts
from pygame.math import Vector2
from logic_circuits.gates.gates import GateBase
from logic_circuits.gates.gates import GateAND, GateNOT, GatePASS, SysIN

class Gate_graphical:
    PAD = 14
    CORNER = 12

    def __init__(self, logical_gate: GateBase, name, x, y, w=220, h=140, num_in=1, num_out=1):
        self.logical_gate = logical_gate
        self.num_in = num_in
        self.num_out = num_out
        self.name = name
        self._x = x
        self._y = y
        self._w, self._h = w, h
        self.rect = pygame.Rect(self._x, self._y, self._w, self._h)
        self.inputs = []
        self.outputs = []
        self._make_ports()

    def _make_ports(self):
        left_x  = 0 + self.PAD
        right_x = self.rect.w - self.PAD
        ys_in   = [self.rect.h * (idx+1)/(self.num_in+1) for idx in range(self.num_in)]
        ys_out   = [self.rect.h * (idx+1)/(self.num_out+1) for idx in range(self.num_out)]
        # ys_in   = [self.rect.h * 0.33, self.rect.h * 0.66]
        # ys_out  = [self.rect.h * 0.33, self.rect.h * 0.66]
        self.inputs  = [Port_graphical(self, 'in',  (left_x,  y), idx) for idx, y in enumerate(ys_in)]
        self.outputs = [Port_graphical(self, 'out', (right_x, y), idx) for idx, y in enumerate(ys_out)]


    def hover(self, mouse):
        return self.rect.collidepoint(mouse)
    

    def move_by(self, dx, dy):
        self.rect.move_ip(dx, dy)
        # Update ports too
        # self._make_ports()

    def draw(self, surf):   
        pygame.draw.rect(surf, BLOCK_FILL, self.rect, border_radius=self.CORNER)
        pygame.draw.rect(surf, BLOCK_OUTL, self.rect, 2, border_radius=self.CORNER)
        if fonts.FONT:
            label = fonts.FONT.render(self.name, True, TEXT)
            surf.blit(label, (self.rect.x + 10, self.rect.y + 8))
        mx, my = pygame.mouse.get_pos()
        for p in self.inputs + self.outputs:
            p.draw(surf, p.hover((mx, my)))

class GateAND_graphical(GateAND):
    PAD = 14
    CORNER = 12

    def __init__(self, name, x, y, w=220, h=140, num_in=2, num_out=1):
        super().__init__(name=name)

        self.num_in = num_in
        self.num_out = num_out
        self._x = x
        self._y = y
        self._w, self._h = w, h
        self.rect = pygame.Rect(self._x, self._y, self._w, self._h)
        self.inputs = []
        self.outputs = []
        self._make_ports()

    def _make_ports(self):
        left_x  = 0 + self.PAD
        right_x = self.rect.w - self.PAD
        ys_in   = [self.rect.h * (idx+1)/(self.num_in+1) for idx in range(self.num_in)]
        ys_out   = [self.rect.h * (idx+1)/(self.num_out+1) for idx in range(self.num_out)]
        
        self.inputs  = [Port_graphical(self, 'in',  (left_x,  y), idx) for idx, y in enumerate(ys_in)]
        self.outputs = [Port_graphical(self, 'out', (right_x, y), idx) for idx, y in enumerate(ys_out)]

    
    def hover(self, mouse):
        return self.rect.collidepoint(mouse)
    

    def move_by(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def draw(self, surf):   
        pygame.draw.rect(surf, BLOCK_FILL, self.rect, border_radius=self.CORNER)
        pygame.draw.rect(surf, BLOCK_OUTL, self.rect, 2, border_radius=self.CORNER)
        if fonts.FONT:
            label = fonts.FONT.render(self.name, True, TEXT)
            label_rect = label.get_rect(center=(self.rect.centerx, self.rect.centery-30))
            surf.blit(label, label_rect) 
            
        mx, my = pygame.mouse.get_pos()
        for p in self.inputs + self.outputs:
            p.draw(surf, p.hover((mx, my)))



class GateNOT_graphical(GateNOT):
    PAD = 14
    CORNER = 12

    def __init__(self, name, x, y, w=220, h=140, num_in=1, num_out=1):
        super().__init__(name=name)

        self.num_in = num_in
        self.num_out = num_out
        self._x = x
        self._y = y
        self._w, self._h = w, h
        self.rect = pygame.Rect(self._x, self._y, self._w, self._h)
        self.inputs = []
        self.outputs = []
        self._make_ports()

    def _make_ports(self):
        left_x  = 0 + self.PAD
        right_x = self.rect.w - self.PAD
        ys_in   = [self.rect.h * (idx+1)/(self.num_in+1) for idx in range(self.num_in)]
        ys_out   = [self.rect.h * (idx+1)/(self.num_out+1) for idx in range(self.num_out)]
        
        self.inputs  = [Port_graphical(self, 'in',  (left_x,  y), idx) for idx, y in enumerate(ys_in)]
        self.outputs = [Port_graphical(self, 'out', (right_x, y), idx) for idx, y in enumerate(ys_out)]

    
    def hover(self, mouse):
        return self.rect.collidepoint(mouse)

    def move_by(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def draw(self, surf):   
        pygame.draw.rect(surf, BLOCK_FILL, self.rect, border_radius=self.CORNER)
        pygame.draw.rect(surf, BLOCK_OUTL, self.rect, 2, border_radius=self.CORNER)
        if fonts.FONT:
            label = fonts.FONT.render(self.name, True, TEXT)
            label_rect = label.get_rect(center=(self.rect.centerx, self.rect.centery-30))
            surf.blit(label, label_rect) 

        mx, my = pygame.mouse.get_pos()
        for p in self.inputs + self.outputs:
            p.draw(surf, p.hover((mx, my)))




class GatePass_graphical(GatePASS):
    PAD = 14
    CORNER = 12

    def __init__(self, name, x, y, w=220, h=140, num_in=1, num_out=1):
        super().__init__(name=name, num_in=num_in, num_out=num_out)

        self.num_in = num_in
        self.num_out = num_out
        self._x = x
        self._y = y
        self._w, self._h = w, h
        self.rect = pygame.Rect(self._x, self._y, self._w, self._h)
        self.plus = pygame.Rect(self._x+self._w/2, self._y, self._w/10, self._h/10)
        self.minus = pygame.Rect(self._x+self._w/2, self._y+self._h-self._h/10, self._w/10, self._h/10)

        self.inputs = []
        self.outputs = []
        self._make_ports()

    def _make_ports(self):
        left_x  = 0 + self.PAD
        right_x = self.rect.w - self.PAD
        ys_in   = [self.rect.h * (idx+1)/(self.num_in+1) for idx in range(self.num_in)]
        ys_out   = [self.rect.h * (idx+1)/(self.num_out+1) for idx in range(self.num_out)]
        
        self.inputs  = [Port_graphical(self, 'in',  (left_x,  y), idx) for idx, y in enumerate(ys_in)]
        self.outputs = [Port_graphical(self, 'out', (right_x, y), idx) for idx, y in enumerate(ys_out)]

    def increase_ports(self):
        self.__init__(self.name, self._x, self._y, self._w, self._h, self.num_in+1, self.num_in+1)
    
    def decrease_ports(self):
        if self.num_in>1:
            self.__init__(self.name, self._x, self._y, self._w, self._h, self.num_in-1, self.num_in-1)
    
    def hover(self, mouse):
        return self.rect.collidepoint(mouse)
    
    def hover_plus(self, mouse):
        return self.plus.collidepoint(mouse)
    
    def hover_minus(self, mouse):
        return self.minus.collidepoint(mouse)
    def move_by(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def draw(self, surf):   
        pygame.draw.rect(surf, BLOCK_FILL, self.rect, border_radius=self.CORNER)
        pygame.draw.rect(surf, BLOCK_OUTL, self.rect, 2, border_radius=self.CORNER)
        pygame.draw.rect(surf, (255, 255, 0), self.plus)
        pygame.draw.rect(surf, (255, 0, 0), self.minus)
        if fonts.FONT:
            label = fonts.FONT.render(self.name, True, TEXT)
            label_rect = label.get_rect(center=(self.rect.centerx, self.rect.centery))
            surf.blit(label, label_rect)
        mx, my = pygame.mouse.get_pos()
        for p in self.inputs + self.outputs:
            p.draw(surf, p.hover((mx, my)))



class SysIN_graphical(SysIN):
    PAD = 14
    CORNER = 12

    def __init__(self, name, x, y, w=220, h=140, num_in=1, num_out=1):
        super().__init__(name, num_in, num_out)

        self.num_in = num_in
        self.num_out = num_out
        self._x = x
        self._y = y
        self._w, self._h = w, h
        self.rect = pygame.Rect(self._x, self._y, self._w, self._h)
        self.plus = pygame.Rect(self._x+self._w/2, self._y, self._w/10, self._h/10)
        self.minus = pygame.Rect(self._x+self._w/2, self._y+self._h-self._h/10, self._w/10, self._h/10)

        self.inputs = []
        self.outputs = []
        self._make_ports()

    def _make_ports(self):
        left_x  = 0 + self.PAD
        right_x = self.rect.w - self.PAD
        ys_in   = [self.rect.h * (idx+1)/(self.num_in+1) for idx in range(self.num_in)]
        ys_out   = [self.rect.h * (idx+1)/(self.num_out+1) for idx in range(self.num_out)]
        
        self.inputs  = [Port_graphical(self, 'in',  (left_x,  y), idx) for idx, y in enumerate(ys_in)]
        self.outputs = [Port_graphical(self, 'out', (right_x, y), idx) for idx, y in enumerate(ys_out)]

    def increase_ports(self):
        self.__init__(self.name, self._x, self._y, self._w, self._h, self.num_in+1, self.num_in+1)
    
    def decrease_ports(self):
        if self.num_in>1:
            self.__init__(self.name, self._x, self._y, self._w, self._h, self.num_in-1, self.num_in-1)
    
    def hover(self, mouse):
        return self.rect.collidepoint(mouse)
    
    def hover_plus(self, mouse):
        return self.plus.collidepoint(mouse)
    
    def hover_minus(self, mouse):
        return self.minus.collidepoint(mouse)
    
    # def move_by(self, dx, dy):
    #     self.rect.move_ip(dx, dy)
    #     self.plus.move_ip(dx, dy)

    def draw(self, surf):   
        pygame.draw.rect(surf, BLOCK_FILL, self.rect, border_radius=self.CORNER)
        pygame.draw.rect(surf, BLOCK_OUTL, self.rect, 2, border_radius=self.CORNER)
        pygame.draw.rect(surf, (255, 255, 0), self.plus)
        pygame.draw.rect(surf, (255, 0, 0), self.minus)
        if fonts.FONT:
            label = fonts.FONT.render(self.name, True, TEXT)
            label_rect = label.get_rect(center=(self.rect.centerx, self.rect.centery))
            surf.blit(label, label_rect)

        mx, my = pygame.mouse.get_pos()
        for p in self.inputs + self.outputs:
            p.draw(surf, p.hover((mx, my)))