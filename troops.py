import pygame

# =========================
# BASE UNIT
# =========================
class Unit:
    next_id = 0

    def __init__(self, x, y, hp, damage, speed, range, elexir, owner):
        self.id = Unit.next_id
        Unit.next_id += 1

        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp

        self.damage = damage
        self.speed = speed
        self.range = range
        self.elexir = elexir
        self.owner = owner

    def move(self):
        pass

    def attack(self):
        pass

    def update(self):
        self.move()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.die()

    def die(self):
        print(f"Unit {self.id} gestorben")


# =========================
# TROOPS
# =========================
class Pekka(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 1000, 200, 0.5, 50, 6, owner)


class HogRider(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 500, 100, 1, 40, 3, owner)


class Ritter(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 600, 120, 0.8, 50, 4, owner)


# =========================
# 🏰 TOWER SYSTEM
# =========================
class Tower(Unit):
    def __init__(self, x, y, image_path, owner):
        super().__init__(x, y, 2000, 100, 0, 200, 0, owner)

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, 60, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, 60 * ratio, 5))


# =========================
# 👑 MAIN TOWER (KING TOWER)
# =========================
class MainTower(Tower):
    def __init__(self, owner, image_path):
        if owner == 1:
            x, y = 295, 100
        else:
            x, y = 295, 490

        super().__init__(x, y, image_path, owner)
        self.hp = 5000
        self.max_hp = 5000


# =========================
# 🏰 SIDE TOWERS
# =========================
class SecTower(Tower):
    def __init__(self, x, y, owner, image_path):
        super().__init__(x, y, image_path, owner)
        self.hp = 3000
        self.max_hp = 3000