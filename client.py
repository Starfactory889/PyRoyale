import pygame, socket, threading, json, sys, os, math
from map import GameMap
from entity_animation import AnimatedEntity

pygame.init()
BASE_DIR = os.path.dirname(__file__)
WIDTH, HEIGHT = 640, 673
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
game_map = GameMap(os.path.join(BASE_DIR, "assets", "map.png"), (WIDTH, HEIGHT))

PLAYER_ID = 1  # ← 1 oder 2 je nach Client

# Spielzustand — nur Dicts, keine Klassen
state = {"troops_p1": [], "troops_p2": [],
         "blue_towers": [], "red_towers": []}
state_lock = threading.Lock()

# Animationen pro Einheit speichern
animations = {}  # id → AnimatedEntity

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

def draw_unit_animated(unit):
    anim = get_or_create_anim(unit)
    anim.x = int(unit["x"])
    anim.y = int(unit["y"])
    anim.update()
    anim.draw(screen)

def draw_unit_circle(unit, color):
    pygame.draw.circle(screen, color, (int(unit["x"]), int(unit["y"])), 5)
    ratio = max(unit["hp"] / unit["max_hp"], 0)
    pygame.draw.rect(screen, (0,0,0),   (int(unit["x"])-15, int(unit["y"])-12, 30, 4))
    pygame.draw.rect(screen, (0,255,0), (int(unit["x"])-15, int(unit["y"])-12, int(30*ratio), 4))

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
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_map.is_allowed(event.pos):
                spawn("Pekka", *event.pos)

    game_map.draw(screen)

    with state_lock:
        for u in state["blue_towers"] + state["red_towers"]:
            # Turm zeichnen als Rechteck (kein Bild am Client nötig)
            pygame.draw.rect(screen, (100,100,200) if u["owner"]==0 else (200,100,100),
                             (int(u["x"]), int(u["y"]), 60, 60))
            ratio = max(u["hp"] / u["max_hp"], 0)
            pygame.draw.rect(screen, (0,0,0),   (int(u["x"]), int(u["y"])-8, 60, 5))
            pygame.draw.rect(screen, (0,255,0), (int(u["x"]), int(u["y"])-8, int(60*ratio), 5))

        for u in state["troops_p1"]:
            draw_unit_animated(u)

        for u in state["troops_p2"]:
            draw_unit_circle(u, (255, 50, 50))

    game_map.draw_debug(screen)
    pygame.display.flip()

pygame.quit()
s.close()
sys.exit()