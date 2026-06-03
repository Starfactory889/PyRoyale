import socket, threading, json, time
import troops as t

state_lock = threading.Lock()
clients = [] 


#Elexir
elixir_p1 = 10.0      # Startwert
elixir_p2 = 10.0
MAX_ELIXIR = 10.0
ELIXIR_PER_SECOND = 1.0

#Kosten der Truppen
ELIXIR_COSTS = {
    "Ritter":   3,
    "HogRider": 4,
    "Pekka":    7,
    "Drache":   4,  
}

troops_p1 = []   # Spieler 1 (Blau)
troops_p2 = []   # Spieler 2 (Rot)
winner  =None

# server.py

blue_towers = [
    t.SecTower(420, 476, 0),   # links
    t.SecTower(220, 476, 0),   # rechts
    t.MainTower(320, 536, 0)              # mitte, weiter unten
]

red_towers = [
    t.SecTower(220, 196, 1),   # links
    t.SecTower(420, 196, 1),   # rechts
    t.MainTower(320, 136, 1)              # mitte, weiter oben
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
            "elixir_p1": round(elixir_p1, 1),
            "elixir_p2": round(elixir_p2, 1),
            "winner": winner,
        }) + "\n"
        
        
def game_loop():
    global troops_p1, troops_p2, elixir_p1, elixir_p2,winner
    last_time = time.perf_counter()

    while True:
        now = time.perf_counter()
        dt = now - last_time
        last_time = now

        with state_lock:

            #Elexir erhöhen
            elixir_p1 = min(MAX_ELIXIR, elixir_p1 + ELIXIR_PER_SECOND * dt)
            elixir_p2 = min(MAX_ELIXIR, elixir_p2 + ELIXIR_PER_SECOND * dt)

            troops_p1 = [troop for troop in troops_p1 if troop.hp > 0]
            troops_p2 = [troop for troop in troops_p2 if troop.hp > 0]
            
            red_targets  = [troop for troop in red_towers  if troop.hp > 0] + troops_p2
            blue_targets = [troop for troop in blue_towers if troop.hp > 0] + troops_p1
 
            for troop in troops_p1:
                troop.next_Step(red_targets,dt)
            for troop in troops_p2:
                troop.next_Step(blue_targets,dt)

            for tower in blue_towers:
                tower.next_Step(troops_p2, dt)
            for tower in red_towers:
                tower.next_Step(troops_p1, dt)
            
            if winner is None:
                winner = check_winner()
        time.sleep(1/60)
        
def check_winner():
    for tower in blue_towers:
        if isinstance(tower, t.MainTower) and tower.hp <= 0:
            return 2  # Rot gewinnt
        
    for tower in red_towers:
        if isinstance(tower, t.MainTower) and tower.hp <= 0:
            return 1  # Blau gewinnt
        
    return None

#nested funktion
def handle_client(conn, player_id):

    print(f"Spieler {player_id} verbunden")
    clients.append(conn)
    def empfangen():
        global elixir_p1, elixir_p2
        puffer = ""
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                puffer += data  # wird nicht genutzt aber bleibt
                while "\n" in puffer:
                    msg, puffer = puffer.split("\n", 1)
                    if msg:
                        cmd = json.loads(msg)
                        if cmd["action"] == "spawn":
                            klass = KLASSEN.get(cmd["type"])
                            if klass is None:
                                continue
                            unit = klass(cmd["x"], cmd["y"], player_id)
                            with state_lock:
                                klasse = KLASSEN[cmd["type"]]

                                # falls er die klasse nicht kennt kommt 999 zurück dadurch wird spawn unmöglich
                                cost = ELIXIR_COSTS.get(cmd["type"], 999)

                                # Elixir prüfen und abziehen
                                if player_id == 1:
                                    if elixir_p1 > cost:
                                        if cmd["type"] == "Ritter":
                                            unit = t.Ritter(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "HogRider":
                                            unit = t.HogRider(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "Pekka":
                                            unit = t.Pekka(cmd["x"], cmd["y"], player_id)
                                            
                                        troops_p1.append(unit)
                                        elixir_p1 -= cost
                                else:
                                    if elixir_p2 > cost:
                                        if cmd["type"] == "Ritter":
                                            unit = t.Ritter(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "HogRider":
                                            unit = t.HogRider(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "Pekka":
                                            unit = t.Pekka(cmd["x"], cmd["y"], player_id)
                                            
                                        troops_p2.append(unit)
                                        elixir_p2 -= cost
                            
                                    
            except Exception as e:
                print(f"Server empfangen Fehler (Spieler {player_id}): {e}")  # ← echter Fehler
                import traceback
                traceback.print_exc()
                break

    def senden():
        while True:
            try:
                conn.send(get_state().encode())
                time.sleep(1 / 30)
            except Exception:
                break

    threading.Thread(target=empfangen, daemon=True).start()
    threading.Thread(target=senden, daemon=True).start()

threading.Thread(target=game_loop, daemon=True).start()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("", 50000))
srv.listen(2)

print("Server läuft auf Port 50000 – warte auf 2 Spieler...")



try:
    player_id = 1
    while True:
        komm, addr = srv.accept()
        threading.Thread(target=handle_client,
                        args=(komm, player_id), daemon=True).start()
        player_id += 1
        
except Exception as e:
        print("Spiel beendet")
       
finally:
    srv.close()
 