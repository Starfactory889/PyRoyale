import pygame
import os


class AnimatedEntity:

    def __init__(
        self,
        folder_name,
        base_path,
        walk_prefix,
        spawn_prefix,
        pos=(300, 300),
        size=(120, 120),
        walk_frames=12,
        spawn_frames=5
    ):

        self.x, self.y = pos

        self.walk_animation = []
        self.spawn_animation = []

        path = os.path.join(base_path, folder_name)

        # -----------------------------
        # WALK Animation laden
        # -----------------------------
        for i in range(1, walk_frames + 1):

            img_path = os.path.join(
                path,
                f"{walk_prefix}_{i}.png"
            )

            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, size)

            self.walk_animation.append(img)

        # -----------------------------
        # SPAWN Animation laden
        # -----------------------------
        for i in range(1, spawn_frames + 1):

            img_path = os.path.join(
                path,
                f"{spawn_prefix}_{i}.png"
            )

            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, size)

            self.spawn_animation.append(img)

        # Aktuelle Animation
        self.frames = self.spawn_animation

        self.index = 0
        self.anim_speed = 0.18

        self.playing_spawn = True
        self.winkel = 0  # ← hier hinzufügen

    # ---------------------------------
    # Update
    # ---------------------------------
    def update(self):

        self.index += self.anim_speed

        # Spawn Animation fertig
        if self.index >= len(self.frames):

            if self.playing_spawn:

                self.playing_spawn = False

                self.frames = self.walk_animation

                self.index = 0

            else:
                self.index = 0

    # ---------------------------------
    # Draw
    # ---------------------------------
    def draw(self, screen):

        frame = self.frames[int(self.index)]
        rotiert = pygame.transform.rotate(frame, self.winkel)  # ← rotieren
        rect = rotiert.get_rect(center=(self.x, self.y))   
        screen.blit(rotiert, rect)