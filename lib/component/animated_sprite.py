import pygame
import os


class AnimatedSprite:
    """
    Sprite sheet helper.
    frame_size : (w, h) of each cell  – default (100, 100)
    frames     : how many frames; if None, auto-detected from sheet width
    scale      : uniform scale
    speed      : ticks per frame (lower = faster)
    one_shot   : if True, stops at last frame and sets .done = True
    """

    def __init__(self, path, frame_size=(100, 100), frames=None,
                 scale=1, x=0, y=0, speed=8, one_shot=False):

        img = pygame.image.load(path).convert_alpha()

        total_frames = frames if frames is not None else img.get_width() // frame_size[0]

        self.frames = [
            pygame.transform.scale(
                img.subsurface((i * frame_size[0], 0, *frame_size)),
                (int(frame_size[0] * scale), int(frame_size[1] * scale))
            )
            for i in range(total_frames)
        ]

        self.base_frames = self.frames[:]
        self.frame_index = 0
        self.timer = 0
        self.speed = speed
        self.one_shot = one_shot
        self.done = False

        self.x = x
        self.y = y

    # ------------------------------------------------------------------ control
    def reset(self):
        self.frame_index = 0
        self.timer = 0
        self.done = False

    def update(self):
        if self.done:
            return
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            next_idx = self.frame_index + 1
            if next_idx >= len(self.frames):
                if self.one_shot:
                    self.done = True
                    return
                self.frame_index = 0
            else:
                self.frame_index = next_idx

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], (self.x, self.y))

    # ------------------------------------------------------------------ utils
    def set_scale(self, scale):
        self.frames = [
            pygame.transform.scale(f, (int(f.get_width() * scale), int(f.get_height() * scale)))
            for f in self.base_frames
        ]

    def get_size(self):
        return self.frames[0].get_size()

    def flip(self, x=True, y=False):
        self.frames = [pygame.transform.flip(f, x, y) for f in self.frames]
        self.base_frames = [pygame.transform.flip(f, x, y) for f in self.base_frames]
