import pygame
from lib.component import assets


class AnimatedSprite:
    """
    Horizontal sprite-sheet animation.

    frame_size : (w, h) of each cell
    frames     : number of frames; auto-detected from sheet width when None
    scale      : uniform scale
    speed      : ticks per frame (lower = faster)
    one_shot   : stop on the last frame and set .done = True
    """

    def __init__(self, sheet_name, frame_size=(100, 100), frames=None,
                 scale=1, x=0, y=0, speed=8, one_shot=False, flip=False):
        sheet = assets.image(sheet_name)
        fw, fh = frame_size
        total = frames if frames is not None else sheet.get_width() // fw
        size = (int(fw * scale), int(fh * scale))

        self.frames = []
        for i in range(total):
            frame = pygame.transform.scale(sheet.subsurface((i * fw, 0, fw, fh)), size)
            if flip:
                frame = pygame.transform.flip(frame, True, False)
            self.frames.append(frame)

        self.speed = speed
        self.one_shot = one_shot
        self.x = x
        self.y = y
        self.reset()

    def reset(self):
        self.frame_index = 0
        self.timer = 0
        self.done = False

    def update(self):
        if self.done:
            return
        self.timer += 1
        if self.timer < self.speed:
            return
        self.timer = 0
        if self.frame_index + 1 < len(self.frames):
            self.frame_index += 1
        elif self.one_shot:
            self.done = True
        else:
            self.frame_index = 0

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], (self.x, self.y))

    def get_size(self):
        return self.frames[0].get_size()
