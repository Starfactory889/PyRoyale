import pygame, socket, threading, json, os
from map import GameMap
from entity_animation import AnimatedEntity

pygame.init()

BASE_DIR = os.path.dirname(__file__)
WIDTH, HEIGHT = 640, 673
PLAYER_ID = 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clash Mini Spieler 2")
clock = pygame.time.Clock()

PLAYER_ID = 2

game_map = GameMap(os.path.join(BASE_DIR, "assets", "map.png"), (WIDTH, HEIGHT), PLAYER_ID)



state = {"troops_p1": [], "troops_p2": [],
         "blue_towers": [], "red_towers": [],
         "winner" : None,
         "elixir_p1": 0,
            "elixir_p2": 0}
state_lock = threading.Lock()

deck = ["Pekka", "Ritter", "HogRider", "Drache"]
#               ↑ Index 1 = Taste 2
selected_card = 0

ANIM_MAP = {
    "Pekka":    ("pekka",   "pekka_m",   "pekka_s"),
    "Ritter":   ("ritter",  "ritter_m",  "ritter_s"),  # ← neu
    "HogRider": ("hogrider", "hogrider_m", "hogrider_s"),
    "Drache":   ("drachen", "drachen_m", "drachen_s"),
}

slot_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "Kartenslots.png"))
slot_img = pygame.transform.scale(slot_img, (320, 170))

win_images = {
    1: pygame.transform.scale(
           pygame.image.load(os.path.join(BASE_DIR, "assets", "spieler1_win.png")),
           (WIDTH, HEIGHT)),
    2: pygame.transform.scale(
           pygame.image.load(os.path.join(BASE_DIR, "assets", "spieler2_win.png")),
           (WIDTH, HEIGHT)),
}

win_images = {
    1: pygame.transform.scale(
           pygame.image.load(os.path.join(BASE_DIR, "assets", "spieler1_win.png")),
           (WIDTH, HEIGHT)),
    2: pygame.transform.scale(
           pygame.image.load(os.path.join(BASE_DIR, "assets", "spieler2_win.png")),
           (WIDTH, HEIGHT)),
}

# Elixir Bild laden:
elixir_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "elixir_drop.png"))
elixir_img = pygame.transform.scale(elixir_img, (24, 24))

card_images = []
for name in deck:
    path = os.path.join(BASE_DIR, "assets", "cards", f"{name.lower()}_card.png")
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (74, 106)) 
        card_images.append(img)
    else:
        card_images.append(None)

def load_tower_img(filename, size=(48, 48)):
    path = os.path.join(BASE_DIR, "assets", "türme", f"{filename}.png")
    if os.path.exists(path):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)
    return None

tower_img_blue      = load_tower_img("turm_blau_1")
tower_img_red       = load_tower_img("turm_rot_1")
tower_img_blue_dead = load_tower_img("turm_blau_2")
tower_img_red_dead  = load_tower_img("turm_rot_2")

animations = {}

def flip(pos):
    return (WIDTH - pos[0], HEIGHT - pos[1])


def draw_unit_animated_flipped(u,dt): # 'targets' wird nicht mehr benötigt!
    sx, sy = flip((u["x"], u["y"]))
    anim = get_anim(u)
    anim.x, anim.y = sx, sy
    anim.winkel = u.get("winkel", 0) + 180  # gespiegelte Perspektive
    anim.update(dt)
    anim.draw(screen)
    draw_hp_bar(screen, int(sx), int(sy), u["hp"], u["max_hp"])

def get_anim(u):
    uid = u["id"]
    troop_type = u.get("type", "Pekka")
    if uid not in animations:
        folder, move_prefix, stand_prefix = ANIM_MAP.get(troop_type, ("drachen", "drachen_m", "drachen_s"))
        sx, sy = flip((u["x"], u["y"]))
        animations[uid] = AnimatedEntity(
            folder,
            os.path.join(BASE_DIR, "assets"),
            move_prefix,
            stand_prefix,
            (sx, sy),
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

def draw_tower(screen, tower, img, img_dead, cx, cy):
    size = 48
    use_img = img_dead if tower["hp"] <= 0 else img
    if use_img:
        screen.blit(use_img, (cx - size // 2, cy - size // 2))
    else:
        color = (50, 100, 255) if tower.get("owner", 0) == 0 else (255, 60, 60)
        pygame.draw.rect(screen, color, (cx - 16, cy - 16, 32, 32), border_radius=4)
    draw_hp_bar(screen, cx, cy, tower["hp"], tower["max_hp"], w=48, offset_y=28)

def spawn(card, x, y):
    rx, ry = flip((x, y))
    s.send(json.dumps({"action": "spawn", "type": card, "x": rx, "y": ry}).encode() + b"\n")

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
            screen.blit(card_images[i], (cx, cy - 10))  # ← 10px nach oben, Zahl anpassen
        else:
            screen.blit(card_images[i], (cx, cy))
        if card_images[i]:
            if is_selected:
                screen.blit(card_images[i], (cx, cy - 10))
            else:
                screen.blit(card_images[i], (cx, cy))
        else:
            label = font_big.render(name[:3], True, (220, 220, 220) if not is_selected else (40, 40, 40))
            screen.blit(label, (cx + slot_w // 2 - label.get_width() // 2, cy + slot_h // 2 - label.get_height() // 2))
        
    #elixier anzeige
    ziel_hoehe = 80  # ← hier anpassen
    ziel_breite = 150
    elixir_img_big = pygame.transform.scale(elixir_img, (ziel_breite, ziel_hoehe))
    ex = bar_x + 350
    ey = bar_y - 55
    screen.blit(elixir_img_big, (ex, ey))
    
    font_elixir = pygame.font.SysFont(None, 36)
    elixir = state.get("elixir_p1") if PLAYER_ID == 1 else state.get("elixir_p2")
    elixir_text = font_elixir.render(f"{int(elixir)}", True, (255, 255, 255))
    tx = ex + ziel_breite // 2 - elixir_text.get_width() // 2
    ty = ey + ziel_hoehe // 2 - elixir_text.get_height() // 2
    screen.blit(elixir_text, (tx, ty+10))

# Network
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 50000))

def recv():
    puffer = ""
    while True:
        try:
            data = s.recv(4096).decode()
            if not data:
                break
            puffer += data
            while "\n" in puffer:
                msg, puffer = puffer.split("\n", 1)
                with state_lock:
                    state.update(json.loads(msg))
        except Exception:
            break
    # Verbindung weg → alles leeren
    with state_lock:
        state["troops_p1"].clear()
        state["troops_p2"].clear()
    animations.clear()

threading.Thread(target=recv, daemon=True).start()

running = True
while running:
    dt = clock.tick(60) / 1000.0
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
            if game_map.is_allowed(flip((x, y))):
                spawn(deck[selected_card], x, y)

    game_map.draw(screen)

    print(state["elixir_p2"])

    
    with state_lock:
        winner = state.get("winner")
    if winner:
        screen.blit(win_images[winner], (0, 0))
        pygame.display.flip()
        pygame.time.wait(10000)
        break
    with state_lock:
        # client2.py
        for tower in state.get("red_towers", []):
            tx, ty = flip((tower["x"], tower["y"]))
            draw_tower(screen, tower, tower_img_blue, tower_img_blue_dead, tx, ty)
            

        for tower in state.get("blue_towers", []):
            tx, ty = flip((tower["x"], tower["y"]))
            draw_tower(screen, tower, tower_img_red, tower_img_red_dead, tx, ty)

        for u in state["troops_p1"] + state["troops_p2"]:
            draw_unit_animated_flipped(u, dt)

    draw_bar()
    pygame.display.flip()

s.close()
pygame.quit()