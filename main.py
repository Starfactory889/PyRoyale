import pygame
import sys
import os
from map import GameMap
from troops import Tower, MainTower, SecTower, Pekka, Ritter, HogRider

selected_card = 0
BASE_DIR = os.path.dirname(__file__)

path_blau = os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png")
path_rot = os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png")
base_bath = os.path.join(BASE_DIR)
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

towers = red_towers + blue_towers

#müll
troops=[]
ritter_p2  = Ritter(x=200, y=200, owner=2)
pekka_p2   = Pekka(x=250, y=200, owner=2,base_path=base_bath)
hog_p2     = HogRider(x=370, y=200, owner=2)
enemys = [hog_p2,pekka_p2,ritter_p2]
# ----------------------------
# GAME LOOP
# ----------------------------
running = True

while running:
    clock.tick(30)


    # Ziele jeden Frame neu berechnen
    # ... draw ...

    selected_types = [Pekka, Ritter, HogRider, Pekka]

for event in pygame.event.get():

    # ----------------------------
    # Spiel schließen
    # ----------------------------
    if event.type == pygame.QUIT:
        running = False

    # ----------------------------
    # Karten auswählen (1–4)
    # ----------------------------
    if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_1:
            selected_card = 0

        elif event.key == pygame.K_2:
            selected_card = 1

        elif event.key == pygame.K_3:
            selected_card = 2

        elif event.key == pygame.K_4:
            selected_card = 3

    # ----------------------------
    # Einheit spawnen
    # ----------------------------
    if event.type == pygame.MOUSEBUTTONDOWN:

        if game_map.is_allowed(event.pos):

            x, y = event.pos

            troop_class = selected_types[selected_card]

            P1 = troop_class(x, y, 1, BASE_DIR)

            troops.append(P1)

            print("Spawn:", troop_class.__name__)
    
    
    
    red_targets  = red_towers + enemys
    blue_targets = blue_towers + troops
    for troop in troops:
        troop.next_Step(red_targets)  # ← fehlt noch!
    for enemy in enemys:
        enemy.next_Step(blue_targets)

    # Tote entfernen
    troops = [t for t in troops if t.hp > 0]
    towers = [t for t in towers if t.hp > 0]
    enemys = [e for e in enemys if e.hp > 0]

    # ----------------------------
    # DRAW
    # ----------------------------
    game_map.draw(screen)

    for t in towers:
        t.draw(screen)
    
    for troop in troops:
        ziel, _ = troop.next_objekt(red_targets)
        troop.update(ziel)
        troop.draw(screen)
        
    for t in enemys:
        t.draw_circle(screen)

    game_map.draw_debug(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()