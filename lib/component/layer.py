import pygame
import os
import random


class Layer:
    def __init__(
        self,
        image_name,
        screen_width,
        screen_height,
        x=0,
        y=0,
        height_scale=1.0,
        random_scale=False
    ):

        path = os.path.join(
            "lib",
            "asset",
            image_name
        )

        self.original_image = pygame.image.load(
            path
        ).convert_alpha()

        self.screen_width = screen_width

        self.screen_height = screen_height

        self.x = x
        self.y = y

        self.height_scale = height_scale

        self.random_scale = random_scale

        base_height = int(
            self.screen_height *
            self.height_scale
        )

        self.base_image = self.scale_to_height(
            self.original_image,
            base_height
        )

        if not self.random_scale:

            self.image = self.base_image

            self.width = self.image.get_width()

        else:

            self.tiles = self.generate_random_tiles()

    def scale_to_height(
        self,
        image,
        height
    ):

        w = image.get_width()
        h = image.get_height()

        new_w = int(w * (height / h))

        return pygame.transform.scale(
            image,
            (new_w, height)
        )

    def generate_random_tiles(self):

        tiles = []

        x_offset = 0

        base_w = self.base_image.get_width()
        base_h = self.base_image.get_height()

        while x_offset < self.screen_width * 2:

            # Random size
            scale_factor = random.uniform(
                0.85,
                1.25
            )

            new_w = int(
                base_w * scale_factor
            )

            new_h = int(
                base_h * scale_factor
            )

            img = pygame.transform.scale(
                self.base_image,
                (new_w, new_h)
            )

            # Random Y offset
            y_offset = random.randint(
                -100,
                0
            )

            tiles.append(
                (img, x_offset, y_offset)
            )

            x_offset += new_w

        return tiles

    def draw(self, screen):

        if not self.random_scale:

            x_pos = self.x

            while x_pos < self.screen_width:

                screen.blit(
                    self.image,
                    (x_pos, self.y)
                )

                x_pos += self.width

        else:

            for img, x_offset, y_offset in self.tiles:

                screen.blit(
                    img,
                    (
                        self.x + x_offset,
                        self.y + y_offset
                    )
                )
