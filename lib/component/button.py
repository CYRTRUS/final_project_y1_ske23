import pygame
import os


class Button:

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        callback,
        click_sound,
        font_size=None
    ):

        self.rect = pygame.Rect(x, y, width, height)

        self.text = text
        self.callback = callback
        self.click_sound = click_sound

        font_path = os.path.join("lib", "font", "minercraftory.regular.ttf")

        if font_size == None:
            font_size = int(height*0.5)
        self.font = pygame.font.Font(font_path, font_size)

        self.color_idle = (70, 130, 180)
        self.color_hover = (100, 160, 210)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):

                if self.click_sound:
                    self.click_sound.play()

                self.callback()

    def draw(self, screen):

        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            color = self.color_hover
        else:
            color = self.color_idle

        pygame.draw.rect(screen, color, self.rect)

        text_surface = self.font.render(self.text, True, (255, 255, 255))

        text_rect = text_surface.get_rect(center=self.rect.center)

        screen.blit(text_surface, text_rect)
