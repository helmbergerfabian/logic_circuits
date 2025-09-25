import pygame

class Button:
    def __init__(self, rect, text, font, bg_color, fg_color, hover_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.fg_color, self.rect, 2, border_radius=8)

        label = self.font.render(self.text, True, self.fg_color)
        surface.blit(
            label,
            label.get_rect(center=self.rect.center)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True  # clicked!
        return False
