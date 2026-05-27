import pygame, socket, threading, json, os
from map import GameMap
from entity_animation import AnimatedEntity
from troops import Pekka, Ritter, HogRider

pygame.init()

BASE_DIR = os.path.dirname(__file__)
WIDTH, HEIGHT = 640, 673

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clash Mini – Spieler 1")
clock = pygame.time.Clock()

game_map = GameMap(os.path.join(BASE_DIR, "assets", "map.png"), (WIDTH, HEIGHT))

PLAYER_ID = 1

state = {"troops_p1": [], "troops_p2": [], "blue_towers": [], "red_towers": []}
lock = threading.Lock()

deck = ["Pekka", "Ritter", "HogRider", "Drache"]
selected_card = 0

ANIM_MAP = {
    "Pekka":    ("pekka",   "pekka_m",   "pekka_s"),
    "HogRider": ("hogrider", "hogrider_m", "hogrider_s"),  # eigene Assets wenn vorhanden
    "Drache":   ("drachen", "drachen_m", "drachen_s"),     # ← korrekter Eintrag
}

slot_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "Kartenslots.png"))
slot_img = pygame.transform.scale(slot_img, (320, 170))

card_images = []
for name in deck:
    path = os.path.join(BASE_DIR, "assets", "cards", f"{name.lower()}_card.png")
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (74, 106))
        card_images.append(img)
    else:
        card_images.append(None)

def load_tower_img(color, size=(48, 48)):
    path = os.path.join(BASE_DIR, "assets", "türme", f"turm_{color}_1.png")
    if os.path.exists(path):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)
    return None

tower_img_blue = load_tower_img("blau")
tower_img_red  = load_tower_img("rot")

animations = {}

def get_anim(u):
    uid = u["id"]
    troop_type = u.get("type", "Pekka")
    if uid not in animations:
        folder, move_prefix, stand_prefix = ANIM_MAP.get(troop_type, ("drachen", "drachen_m", "drachen_s"))
        animations[uid] = AnimatedEntity(
            folder,
            os.path.join(BASE_DIR, "assets"),
            move_prefix,
            stand_prefix,
            (u["x"], u["y"]),
            (40, 40),
            12,
            5
        )
    return animations[uid]

def draw_hp_bar(screen, cx, cy, hp, max_hp, w=32, offset_y=20):
    if max_hp <= 0:
        return
    ratio = max(0, hp / max_hp)
    bx = cx - w // 2
    by = cy - offset_y
    pygame.draw.rect(screen, (40, 40, 40), (bx, by, w, 4))
    pygame.draw.rect(screen, (60, 200, 80), (bx, by, int(w * ratio), 4))

def draw_tower(screen, tower, img, cx, cy):
    size = 48
    if img:
        screen.blit(img, (cx - size // 2, cy - size // 2))
    else:
        color = (50, 100, 255) if tower.get("owner", 0) == 0 else (255, 60, 60)
        pygame.draw.rect(screen, color, (cx - 16, cy - 16, 32, 32), border_radius=4)
    draw_hp_bar(screen, cx, cy, tower["hp"], tower["max_hp"], w=48, offset_y=28)

def spawn(card, x, y):
    s.send(json.dumps({"action": "spawn", "type": card, "x": x, "y": y}).encode() + b"\n")

def draw_bar():
    bar_x = WIDTH // 2 - 160
    bar_y = HEIGHT - 130
    screen.blit(slot_img, (bar_x, bar_y))

    slot_w = 60
    slot_h = 80
    gap = (320 - 4 * slot_w) // 5
    font = pygame.font.SysFont(None, 22)
    font_big = pygame.font.SysFont(None, 26)

    for i, name in enumerate(deck):
        cx = bar_x + gap + i * (slot_w + gap)
        cy = bar_y + 25
        is_selected = (i == selected_card)

        
        if is_selected:
            screen.blit(card_images[i], (cx-10, cy - 13))  # ← 10px nach oben, Zahl anpassen
        else:
            screen.blit(card_images[i], (cx-10, cy))
        if card_images[i]:
            if is_selected:
                screen.blit(card_images[i], (cx-10, cy - 13))
            else:
                screen.blit(card_images[i], (cx-10, cy))
        else:
            label = font_big.render(name[:3], True, (220, 220, 220) if not is_selected else (40, 40, 40))
            screen.blit(label, (cx + slot_w // 2 - label.get_width() // 2, cy + slot_h // 2 - label.get_height() // 2))
# Network
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 50000))

def recv():
    buf = ""
    while True:
        try:
            data = s.recv(4096).decode()
            if not data:
                break
            buf += data
            while "\n" in buf:
                msg, buf = buf.split("\n", 1)
                with lock:
                    state.update(json.loads(msg))
        except Exception:
            break
    # Verbindung weg → alles leeren
    with lock:
        state["troops_p1"].clear()
        state["troops_p2"].clear()
    animations.clear()

threading.Thread(target=recv, daemon=True).start()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: selected_card = 0
            if event.key == pygame.K_2: selected_card = 1
            if event.key == pygame.K_3: selected_card = 2
            if event.key == pygame.K_4: selected_card = 3
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if game_map.is_allowed((x, y)):
                spawn(deck[selected_card], x, y)

    game_map.draw(screen)

    with lock:
        for tower in state.get("blue_towers", []):
            draw_tower(screen, tower, tower_img_blue, tower["x"], tower["y"])
        for tower in state.get("red_towers", []):
            draw_tower(screen, tower, tower_img_red, tower["x"], tower["y"])

        for u in state["troops_p1"] + state["troops_p2"]:
            if u["owner"] == PLAYER_ID:
                anim = get_anim(u)
                anim.x, anim.y = u["x"], u["y"]
                anim.update()
                anim.draw(screen)
            else:
                pygame.draw.circle(screen, (255, 60, 60), (int(u["x"]), int(u["y"])), 10)
            draw_hp_bar(screen, int(u["x"]), int(u["y"]), u["hp"], u["max_hp"])

    draw_bar()
    pygame.display.flip()

s.close()
pygame.quit()