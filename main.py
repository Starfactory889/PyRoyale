import pygame
import sys
import os

from map import GameMap
from troops import Tower, MainTower, SecTower, Pekka


BASE_DIR = os.path.dirname(__file__)

path_blau = os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png")
path_rot = os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png")
pygame.init()

WIDTH, HEIGHT = 640, 673
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clash Mini System")

clock = pygame.time.Clock()


# ----------------------------
# MAP
# ----------------------------
game_map = GameMap(
    os.path.join(BASE_DIR, "assets", "map.png"),
    (WIDTH, HEIGHT)
)




blue_towers = [
    SecTower(180, 450, 0, path_blau),
    SecTower(410, 450, 0, path_blau),
    MainTower(0, path_blau)
]
red_towers = [
    SecTower(180, 140, 1, path_rot),
    SecTower(410, 140, 1, path_rot),
    MainTower(1, path_rot)
]

troops=[]
# ----------------------------
# GAME LOOP
# ----------------------------
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_map.is_allowed(event.pos):
                x,y=event.pos
                #print(x,y)
                P1=Pekka(x,y,1)
                troops.append(P1)
                print(troops)

    # ----------------------------
    # DRAW
    # ----------------------------
    game_map.draw(screen)

    for t in blue_towers:
        t.draw(screen)

    for t in red_towers:
        t.draw(screen)
    
    for t in troops:
        t.draw_circle(screen)



    game_map.draw_debug(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()