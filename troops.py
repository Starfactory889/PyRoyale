import os
import math


class Unit:
    next_id = 0

    def __init__(self, x, y, hp, damage, speed, range_, elexir, owner, attack_cooldown=60):
        self.id = Unit.next_id
        Unit.next_id += 1
        self.current_angle = 0
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp

        self.damage = damage
        self.speed = speed
        self.range = range_
        self.elexir = elexir
        self.owner = owner

        # Angriffs-Cooldown in Frames (60 = 1 Angriff/Sek bei 60fps)
        self.attack_cooldown = attack_cooldown
        self._attack_timer = 0

    def distance(self, goal):
        dx = goal.x - self.x
        dy = goal.y - self.y
        d = math.sqrt(dx**2 + dy**2)
        return d, (dx, dy)

    def next_objekt(self, enemys: list):
        min_d = float("inf")
        next_enemy = None
        for enemy in enemys:
            if enemy.hp <= 0:
                continue
            d, _ = self.distance(enemy)
            if d < min_d and d != 0:
                min_d = d
                next_enemy = enemy
        return next_enemy, min_d

    def next_Step(self, enemys: list, dt: float):
        # Cooldown-Timer runterzählen
        if self._attack_timer > 0:
            self._attack_timer -= 1

        enemy, d = self.next_objekt(enemys)
        if enemy is None:
            return

        if d <= self.range:
            if self._attack_timer == 0:
                self.attack(enemy)
                self._attack_timer = self.attack_cooldown
                
        elif not isinstance(self, Tower):
            d,(dx,dy) = self.distance(enemy)
            x,y = self.move(d,dx,dy,dt)
            self.current_angle = math.degrees(math.atan2(-dy, dx)) - 90
            return x,y
            
            
            
    def move(self,d,dx,dy,dt):
        self.x = round(self.x + (dx / d) * self.speed * dt,2)
        self.y = round(self.y + (dy / d) * self.speed * dt,2)
        return self.x,self.y
            

    def attack(self, enemy):
        if enemy.hp <= 0:
            return
        enemy.hp -= self.damage
        if enemy.hp <= 0:
            enemy.hp = 0
            enemy.die()

    def die(self):
        print(f"Unit {self.id} ({type(self).__name__}) gestorben")


# ── Truppen ────────────────────────────────────────────────────────────────────

class Pekka(Unit):
    # 7 Elixir — stärkste Einheit, langsamer Tank mit hohem Schaden
    # Sehr viel HP, sehr hoher Schaden, langsam
    def __init__(self, x, y, owner):
        super().__init__(x, y, 2000, 250, 25, 15, 7, owner, attack_cooldown=40)


class HogRider(Unit):
    # hp=500, dmg=100, speed=70, range=3, elexir=3
    # attack_cooldown=50 → 1.2 Angriffe/Sek
    def __init__(self, x, y, owner):
        super().__init__(x, y, 600, 110,70, 15, 4, owner, attack_cooldown=45)

class Ritter(Unit):
    # 3 Elixir — günstiger Tank
    # Viel HP, wenig Schaden, langsam
    def __init__(self, x, y, owner):
        super().__init__(x, y, 800, 80, 40, 15, 3, owner, attack_cooldown=60)

class Drache(Unit):
    # 4 Elixir — Fernkämpfer
    # Wenig HP, hoher Schaden, große Reichweite
    def __init__(self, x, y, owner, base_path=None):
        super().__init__(x, y, 500, 140, 55, 75, 4, owner, attack_cooldown=50)
# ── Türme ─────────────────────────────────────────────────────────────────────

class Tower(Unit):
    # Türme stehen still (speed=0), greifen aber an
    # attack_cooldown=90 → 1 Angriff alle 1.5 Sek
    def __init__(self, x, y, owner):
        super().__init__(x, y, 2000, 50, 0, 200, 0, owner, attack_cooldown=90)


class MainTower(Tower):
    def __init__(self,x,y, owner):
        #x, y = (295, 120) if owner == 1 else (320, 520)  weiter an den Rand
        super().__init__(x, y, owner)
        self.hp = 4000
        self.max_hp = 4000


class SecTower(Tower):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.hp = 3000
        self.max_hp = 3000