import pygame

class GameMap:
    def __init__(self, path, size):
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, size)

        self.allowed_areas = [
            pygame.Rect(140, 100, 380, 450)
            
        ]

        self.blocked_areas = [
            #pygame.Rect(200, 150, 80, 120),
            
        ]

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

    def draw_debug(self, screen):
        for r in self.allowed_areas:
            pygame.draw.rect(screen, (0, 0, 255), r, 2)

        for r in self.blocked_areas:
            pygame.draw.rect(screen, (255, 0, 0), r, 2)

    def is_allowed(self, pos):
        if any(r.collidepoint(pos) for r in self.blocked_areas):
            return False
        if any(r.collidepoint(pos) for r in self.allowed_areas):
            return True
