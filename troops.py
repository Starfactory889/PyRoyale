import os
from entity_animation import AnimatedEntity
import math


class Unit:
    next_id = 0

    def __init__(self, x, y, hp, damage, speed, range, elexir, owner):
        self.id = Unit.next_id
        Unit.next_id += 1
        self.current_angle = 0
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp

        self.damage = damage
        self.speed = speed
        self.range = range
        self.elexir = elexir
        self.owner = owner

    def distance(self, goal:object):
        dx = (goal.x - self.x)
        dy = (goal.y - self.y)
        d = math.sqrt(dx**2+dy**2)
        return d,(dx,dy)

    def next_objekt(self,enemys:list):
        min_d = float("inf")
        next_enemy = None
        for enemy in enemys:
            if enemy.hp <= 0:
                continue
            
            d,_ = self.distance(enemy)
            if d < min_d and d != 0:
                min_d = d
                next_enemy = enemy
        return next_enemy,min_d
    
    def next_Step(self,enemys:list):
        enemy,d = self.next_objekt(enemys)
        if enemy is None:
            return
    
        elif d < self.range:
            self.attack(enemy)
        
        else:
            d,(dx,dy) = self.distance(enemy)
            x,y = self.move(d,dx,dy)
            
            self.current_angle = math.degrees(math.atan2(-dy, dx)) - 90
            
            return x,y
            
            
            
    def move(self,d,dx,dy):
        self.x = round(self.x + (dx / d) * self.speed,2)
        self.y = round(self.y + (dy / d) * self.speed,2)
        return self.x,self.y
            

    def attack(self,enemy:object):
        if enemy.hp <= 0:
            return  
        enemy.hp -= self.damage
        if enemy.hp <=0:
            enemy.hp = 0
            enemy.die()
            

    def die(self):
        print(f"Unit {self.id} gestorben")
        
    '''
    def draw_circle(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 5)
        return screen
    '''

class Pekka(Unit):
    """Pekka ohne Animation – nur für Serverlogik"""
    def __init__(self, x, y, owner):
        super().__init__(x, y, 1000, 200, 2.5, 50, 6, owner)
        

class HogRider(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 500, 100, 1, 3, 3, owner)


class Ritter(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 600, 120, 0.8, 2, 4, owner)



class Tower(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, 2000, 100, 0, 200, 0, owner)

        



class MainTower(Tower):
    def __init__(self, owner):
        if owner == 1:
            x, y = 295, 100
        else:
            x, y = 295, 490

        super().__init__(x, y, owner)
        self.hp = 5000
        self.max_hp = 5000


class SecTower(Tower):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.hp = 3000
        self.max_hp = 3000