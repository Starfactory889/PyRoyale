import socket, threading, json, time
import troops as t
 
# Spielzustand
state_lock = threading.Lock()
<<<<<<< HEAD
 
troops_p1 = []   # Spieler 1 (Blau)
troops_p2 = []   # Spieler 2 (Rot)
 
 
 
#
blue_towers = [t.SecTower(180, 450, 0),
               t.SecTower(410, 450, 0),
               t.MainTower(0)]
 
red_towers  = [t.SecTower(180, 140, 1),
               t.SecTower(410, 140, 1),
               t.MainTower(1)]
 
=======

troops_p1 = []   # Spieler 1 (Blau)
troops_p2 = []   # Spieler 2 (Rot)

blue_towers = [t.SecTower(180, 450, 0),
               t.SecTower(410, 450, 0),
               t.MainTower(0)]

red_towers  = [t.SecTower(180, 140, 1),
               t.SecTower(410, 140, 1),
               t.MainTower(1)]

>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
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
        }) + "\n"
 
def game_loop():
    global troops_p1, troops_p2
    while True:
        with state_lock:
            troops_p1 = [t for t in troops_p1 if t.hp > 0]
            troops_p2 = [t for t in troops_p2 if t.hp > 0]
<<<<<<< HEAD
           
=======
            
>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
            red_targets  = [t for t in red_towers  if t.hp > 0] + troops_p2
            blue_targets = [t for t in blue_towers if t.hp > 0] + troops_p1
 
            for troop in troops_p1:
                troop.next_Step(red_targets)
            for troop in troops_p2:
                troop.next_Step(blue_targets)
<<<<<<< HEAD
 
        time.sleep(1/60)
 
=======

        time.sleep(1/60)

>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
#nested funktion
def handle_client(komm, player_id):
    print(f"Spieler {player_id} verbunden")
 
    def empfangen():
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
<<<<<<< HEAD
                                # müssen noch auf mehr truppen angepasst werden
                           
=======
                                # müssen noch auf mehr truppen angepasst werden 
                            
>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
                                if cmd["type"] == "Ritter":
                                    unit = t.Ritter(cmd["x"], cmd["y"], player_id)
                                elif cmd["type"] == "HogRider":
                                    unit = t.HogRider(cmd["x"], cmd["y"], player_id)
                                else:
                                    unit = t.Pekka(cmd["x"], cmd["y"], player_id)
                            
>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
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
<<<<<<< HEAD
 
 
=======


>>>>>>> 3aef356de8c83849447a9db492784c3b2be0dd57
try:
    player_id = 1
    while True:
        komm, addr = s.accept()
        threading.Thread(target=handle_client,
                        args=(komm, player_id), daemon=True).start()
        if player_id < 2:
            player_id += 1        
finally:
    s.close()