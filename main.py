import pygame
import sys
import os

from map import GameMap
from troops import Tower

pygame.init()

WIDTH, HEIGHT = 640, 673
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clash Mini System")

clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(__file__)

# ----------------------------
# MAP
# ----------------------------
game_map = GameMap(
    os.path.join(BASE_DIR, "assets", "map.png"),
    (WIDTH, HEIGHT)
)



# ----------------------------
# 🏰 TÜRME (BLUE)
# ----------------------------
blue_towers = [
    Tower((180, 450), os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png"), "blue"),
    Tower((295, 490), os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png"), "blue"),
    Tower((410, 450), os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png"), "blue")
]

# ----------------------------
# 🔴 TÜRME (RED)
# ----------------------------
red_towers = [
    Tower((180, 140), os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png"), "red"),
    Tower((295, 100), os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png"), "red"),
    Tower((410, 140), os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png"), "red")
]

# ----------------------------
# GAME LOOP
# ----------------------------
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----------------------------
    # DRAW
    # ----------------------------
    game_map.draw(screen)

    for t in blue_towers:
        t.draw(screen)

    for t in red_towers:
        t.draw(screen)



    game_map.draw_debug(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()