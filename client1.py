import pygame, socket, threading, json, sys, os, math
from map import GameMap
from entity_animation import AnimatedEntity

pygame.init()
BASE_DIR = os.path.dirname(__file__)
path_blau = os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png")
path_rot  = os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png")
WIDTH, HEIGHT = 640, 673
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
game_map = GameMap(os.path.join(BASE_DIR, "assets", "map.png"), (WIDTH, HEIGHT))

# Bilder einmal laden
img_blau = pygame.image.load(path_blau).convert_alpha()
img_blau = pygame.transform.scale(img_blau, (60, 60))
img_rot  = pygame.image.load(path_rot).convert_alpha()
img_rot  = pygame.transform.scale(img_rot, (60, 60))

PLAYER_ID = 1  # ← 1 oder 2 je nach Client

# Spielzustand — nur Dicts, keine Klassen
state = {"troops_p1": [], "troops_p2": [],
         "blue_towers": [], "red_towers": []}
state_lock = threading.Lock()

# Animationen pro Einheit speichern
animations = {}  # id → AnimatedEntity

def draw_tower(screen, tower, image):
    screen.blit(image, (int(tower["x"]), int(tower["y"])))
    ratio = max(tower["hp"] / tower["max_hp"], 0)
    pygame.draw.rect(screen, (0,0,0),   (int(tower["x"]), int(tower["y"])-8, 60, 5))
    pygame.draw.rect(screen, (0,255,0), (int(tower["x"]), int(tower["y"])-8, int(60*ratio), 5))

def draw_unit_animated(unit,dt): # 'targets' wird nicht mehr benötigt!
    anim = get_or_create_anim(unit)
    anim.x = int(unit["x"])
    anim.y = int(unit["y"])
    # Wir nehmen direkt den Winkel, den der Server berechnet hat
    anim.winkel = unit.get("winkel", 0) 
    anim.update(dt)
    anim.draw(screen)

    
def get_or_create_anim(unit):
    uid = unit["id"]
    if uid not in animations:
        animations[uid] = AnimatedEntity(
            folder_name="drachen",
            base_path=os.path.join(BASE_DIR, "assets"),
            walk_prefix="drachen_m",
            spawn_prefix="drachen_s",
            pos=(unit["x"], unit["y"]),
            size=(40, 40),
            walk_frames=12,
            spawn_frames=5
        )
    return animations[uid]
    
def spawn(troop_type, x, y):
    cmd = json.dumps({"action": "spawn", "type": troop_type, "x": x, "y": y})
    s.send((cmd + "\n").encode())

# Netzwerk
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 50000))

def empfangen():
    puffer = ""
    while True:
        data = s.recv(4096).decode()
        puffer += data
        while "\n" in puffer:
            msg, puffer = puffer.split("\n", 1)
            if msg:
                with state_lock:
                    state.update(json.loads(msg))
                    
                    
                    

threading.Thread(target=empfangen, daemon=True).start()

# Game Loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_map.is_allowed(event.pos):
                 spawn("Pekka", *event.pos)

    game_map.draw(screen)

    with state_lock:
        # 1. Türme zeichnen
        for tower in state["blue_towers"] + state["red_towers"]:
            # Blau ist Team 0 (Server Index), Rot ist Team 1
            img = img_blau if tower["owner"] == 0 else img_rot
            draw_tower(screen, tower, img)

        # 2. Alle Truppen beider Listen durchgehen
        all_troops = state["troops_p1"] + state["troops_p2"]
        for u in all_troops:
            # Wenn die Einheit mir gehört -> Animiert zeichnen
            # (PLAYER_ID ist 1 oder 2, owner am Server ist auch 1 oder 2)
            targets = state["red_towers"] + state["troops_p2"] if PLAYER_ID == 1 else state["blue_towers"] + state["troops_p1"]
            draw_unit_animated(u,dt) 

    game_map.draw_debug(screen)
    pygame.display.flip()

pygame.quit()
s.close()
sys.exit()