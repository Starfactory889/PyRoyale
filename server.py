import socket, threading, json, time
import troops as t

state_lock = threading.Lock()

troops_p1 = []
troops_p2 = []

blue_towers = [
    t.SecTower(180, 450, 0),
    t.SecTower(410, 450, 0),
    t.MainTower(0)
]

red_towers = [
    t.SecTower(180, 140, 1),
    t.SecTower(410, 140, 1),
    t.MainTower(1)
]

KLASSEN = {
    "Pekka":    t.Pekka,
    "Ritter":   t.Ritter,
    "HogRider": t.HogRider,
    "Drache":   t.Drache,  
}

def serialize(units):
    result = []
    for u in units:
        result.append({
            "id":      u.id,
            "x":       u.x,
            "y":       u.y,
            "hp":      u.hp,
            "max_hp":  u.max_hp,
            "owner":   u.owner,
            "winkel":  getattr(u, "current_angle", 0),
            # Typ mitsenden damit Clients die richtige Animation laden können
            "type":    type(u).__name__,
        })
    return result

def get_state():
    with state_lock:
        return json.dumps({
            "troops_p1":   serialize(troops_p1),
            "troops_p2":   serialize(troops_p2),
            "blue_towers": serialize(blue_towers),
            "red_towers":  serialize(red_towers),
        }) + "\n"

def game_loop():
    global troops_p1, troops_p2

    while True:
        with state_lock:
            # Variable `u` statt `t` verwenden – kein Shadowing des Modul-Alias
            troops_p1 = [u for u in troops_p1 if u.hp > 0]
            troops_p2 = [u for u in troops_p2 if u.hp > 0]

            red_targets  = red_towers  + troops_p2
            blue_targets = blue_towers + troops_p1

            for unit in troops_p1:
                unit.next_Step(red_targets)

            for unit in troops_p2:
                unit.next_Step(blue_targets)

        time.sleep(1 / 60)

def handle_client(conn, player_id):

    def recv():
        buffer = ""
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                buffer += data

                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    cmd = json.loads(msg)

                    if cmd["action"] == "spawn":
                        klass = KLASSEN.get(cmd["type"])
                        if klass is None:
                            continue
                        unit = klass(cmd["x"], cmd["y"], player_id)

                        with state_lock:
                            if player_id == 1:
                                troops_p1.append(unit)
                            else:
                                troops_p2.append(unit)
            except Exception:
                break

    def send():
        while True:
            try:
                conn.send(get_state().encode())
                time.sleep(1 / 30)
            except Exception:
                break

    threading.Thread(target=recv, daemon=True).start()
    threading.Thread(target=send, daemon=True).start()

threading.Thread(target=game_loop, daemon=True).start()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("", 50000))
srv.listen(2)

print("Server läuft auf Port 50000 – warte auf 2 Spieler...")

player_id = 1
while True:
    conn, addr = srv.accept()
    print(f"Spieler {player_id} verbunden von {addr}")
    threading.Thread(target=handle_client, args=(conn, player_id), daemon=True).start()
    player_id = 2 if player_id == 1 else 1