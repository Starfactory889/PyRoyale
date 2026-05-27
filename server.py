import socket, threading, json, time
import troops as t
 
# Spielzustand
state_lock = threading.Lock()
clients = [] 

#Elexir
elixir_p1 = 5.0      # Startwert
elixir_p2 = 5.0
MAX_ELIXIR = 10.0
ELIXIR_PER_SECOND = 2.0

#Kosten der Truppen
ELIXIR_COSTS = {
    "Ritter": 3,
    "HogRider": 4,
    "Pekka": 7
}

troops_p1 = []   # Spieler 1 (Blau)
troops_p2 = []   # Spieler 2 (Rot)

blue_towers = [t.SecTower(180, 450, 0),
               t.SecTower(410, 450, 0),
               t.MainTower(0)]

red_towers  = [t.SecTower(180, 140, 1),
               t.SecTower(410, 140, 1),
               t.MainTower(1)]

KLASSEN = {"Pekka": t.Pekka, "Ritter": t.Ritter, "HogRider": t.HogRider}
 

# In server.py
def serialize(units):
    return [{
        "id": u.id, 
        "type": u.__class__.__name__, # Liefert "Pekka", "Ritter", etc.
        "x": u.x, 
        "y": u.y, 
        "hp": u.hp, 
        "max_hp": u.max_hp, 
        "owner": u.owner,
        "winkel": u.current_angle
    } for u in units]

def get_state():
    with state_lock:
        return json.dumps({
            "troops_p1":   serialize(troops_p1),
            "troops_p2":   serialize(troops_p2),
            "blue_towers": serialize(blue_towers),
            "red_towers":  serialize(red_towers),
            "elixir_p1": round(elixir_p1, 1),
            "elixir_p2": round(elixir_p2, 1)
        }) + "\n"
        
def broadcast(msg):
    for komm in clients:
        try:
            komm.send(msg.encode())
        except:
            pass
        
def game_loop():
    global troops_p1, troops_p2, elixir_p1, elixir_p2

    last_time = time.perf_counter()

    while True:
        now = time.perf_counter()
        dt = now - last_time
        last_time = now

        with state_lock:

            #Elexir erhöhen
            elixir_p1 = min(MAX_ELIXIR, elixir_p1 + ELIXIR_PER_SECOND * dt)
            elixir_p2 = min(MAX_ELIXIR, elixir_p2 + ELIXIR_PER_SECOND * dt)


            troops_p1 = [t for t in troops_p1 if t.hp > 0]
            troops_p2 = [t for t in troops_p2 if t.hp > 0]
            
            red_targets  = [t for t in red_towers  if t.hp > 0] + troops_p2
            blue_targets = [t for t in blue_towers if t.hp > 0] + troops_p1
 
            for troop in troops_p1:
                troop.next_Step(red_targets,dt)
            for troop in troops_p2:
                troop.next_Step(blue_targets,dt)
        
        winner = check_winner()
        if winner:
            broadcast(f'{{"winner": {winner}}}\n')

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
def handle_client(komm, player_id):

    print(f"Spieler {player_id} verbunden")
    clients.append(komm)
    def empfangen():
        global elixir_p1, elixir_p2
        puffer = ""
        while True:
            try:
                data = komm.recv(1024).decode()
                if not data:
                    break
                puffer += data  # wird nicht genutzt aber bleibt
                while "\n" in puffer:
                    msg, puffer = puffer.split("\n", 1)
                    if msg:
                        cmd = json.loads(msg)
                        if cmd["action"] == "spawn":
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
                                        elixir_p1 -= cost
                                else:
                                    if elixir_p2 > cost:
                                        if cmd["type"] == "Ritter":
                                            unit = t.Ritter(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "HogRider":
                                            unit = t.HogRider(cmd["x"], cmd["y"], player_id)
                                        elif cmd["type"] == "Pekka":
                                            unit = t.Pekka(cmd["x"], cmd["y"], player_id)

                                        elixir_p2 -= cost


                                
                                
                            

                                if player_id == 1:
                                    troops_p1.append(unit)
                                else:
                                    troops_p2.append(unit)
            except:
                break
 
    def senden():
        while True:
            try:
                komm.send(get_state().encode())
                time.sleep(1/30)
            except:
                break
 
    threading.Thread(target=empfangen, daemon=True).start()
    threading.Thread(target=senden,    daemon=True).start()
 
threading.Thread(target=game_loop, daemon=True).start()
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 50000))
s.listen(2)
print("Server läuft...")



try:
    player_id = 1
    while True:
        komm, addr = s.accept()
        threading.Thread(target=handle_client,
                        args=(komm, player_id), daemon=True).start()
        player_id += 1
       
finally:
    s.close()
 