import pygame

class Tower:
    def __init__(self, pos, image_path, team, hp=1000):
        self.x, self.y = pos
        self.team = team
        self.hp = hp
        self.max_hp = hp

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, 60, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, 60 * ratio, 5))