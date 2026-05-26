import pygame, socket, threading, json, sys, os, math
from map import GameMap
from entity_animation import AnimatedEntity

pygame.init()
BASE_DIR = os.path.dirname(__file__)
path_blau = os.path.join(BASE_DIR, "assets", "türme", "turm_blau_1.png")
path_rot  = os.path.join(BASE_DIR, "assets", "türme", "turm_rot_1.png")
path_map  = os.path.join(BASE_DIR, "assets", "map.png")
WIDTH, HEIGHT = 640, 673
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# MAP Initialisierung und 180° Drehung
game_map = GameMap(os.path.join(BASE_DIR, "assets", "map.png"), (WIDTH, HEIGHT))

# Bilder laden und skalieren
img_blau = pygame.image.load(path_blau).convert_alpha()
img_blau = pygame.transform.scale(img_blau, (60, 60))
img_rot  = pygame.image.load(path_rot).convert_alpha()
img_rot  = pygame.transform.scale(img_rot, (60, 60))


PLAYER_ID = 2 
state = {"troops_p1": [], "troops_p2": [], "blue_towers": [], "red_towers": []}
state_lock = threading.Lock()
animations = {}

def flip(pos):
    return (WIDTH - pos[0], HEIGHT - pos[1])

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

def draw_tower_flipped(screen, tower, image):
    fx, fy = flip((tower["x"], tower["y"]))
    screen.blit(image, (fx - 30, fy - 30))
    
    ratio = max(tower["hp"] / tower["max_hp"], 0)
    
    pygame.draw.rect(screen, (0,0,0),   (fx - 30, fy - 38, 60, 5))   # ← fx/fy statt tower["x"]/tower["y"]
    pygame.draw.rect(screen, (0,255,0), (fx - 30, fy - 38, int(60*ratio), 5))
    


def draw_unit_animated_flipped(unit):
    anim = get_or_create_anim(unit)
    anim.x, anim.y = flip((unit["x"], unit["y"]))
    anim.winkel = unit.get("winkel", 0) + 180 
    anim.update()
    anim.draw(screen)

def spawn(troop_type, x, y):
    cmd = json.dumps({"action": "spawn", "type": troop_type, "x": x, "y": y})
    s.send((cmd + "\n").encode())

# Netzwerk Setup
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("127.0.0.1", 50000))
except:
    print("Server nicht gefunden!")
    sys.exit()

def empfangen():
    puffer = ""
    while True:
        try:
            data = s.recv(4096).decode()
            puffer += data
            while "\n" in puffer:
                msg, puffer = puffer.split("\n", 1)
                if msg:
                    with state_lock:
                        state.update(json.loads(msg))
        except: break

threading.Thread(target=empfangen, daemon=True).start()

# --- Hauptschleife ---
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Klick für Server zurückdrehen
            real_x, real_y = flip(event.pos)
            if game_map.is_allowed((real_x, real_y)):
                spawn("Pekka", real_x, real_y)

    game_map.draw(screen)

    with state_lock:
        # 1. Türme gespiegelt
        for tower in state["blue_towers"] + state["red_towers"]:
            img = img_rot if tower["owner"] == 0 else img_blau
            draw_tower_flipped(screen, tower, img)

        # 2. Truppen gespiegelt
        all_troops = state["troops_p1"] + state["troops_p2"]
        active_ids = [u["id"] for u in all_troops]
        
        for u in all_troops:
            if u["owner"] == PLAYER_ID:
                draw_unit_animated_flipped(u)
            else:
                # Feinde als gespiegelte Kreise
                fx, fy = flip((u["x"], u["y"]))
                pygame.draw.circle(screen, (255, 50, 50), (int(fx), int(fy)), 10)
        
        # Aufräumen alter Animationen (Memory Leak Schutz)
        animations = {uid: anim for uid, anim in animations.items() if uid in active_ids}

    pygame.display.flip()

pygame.quit()
s.close()