import pygame
import os


class AnimatedSprite:
    def __init__(self, path, frame_size=(100, 100), frames=6, scale=1, x=0, y=0, speed=8):
        self.image = pygame.image.load(os.path.join(path)).convert_alpha()

        self.frames = [
            pygame.transform.scale(
                self.image.subsurface((i*frame_size[0], 0, *frame_size)),
                (int(frame_size[0]*scale), int(frame_size[1]*scale))
            )
            for i in range(frames)
        ]

        self.frame_index = 0
        self.timer = 0
        self.speed = speed

        self.x = x
        self.y = y

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.frame_index = (self.frame_index+1) % len(self.frames)

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], (self.x, self.y))

    def set_scale(self, scale):
        w, h = self.frames[0].get_size()
        self.frames = [
            pygame.transform.scale(f, (int(w*scale), int(h*scale)))
            for f in self.frames
        ]

    def get_size(self):
        return self.frames[0].get_size()
