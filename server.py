#server
import socket, threading,json,time
import troops as t

path_blau = "./assets/türme/turm_blau_1.png"
path_rot  = "./assets/türme/turm_rot_1.png"

#Start zustand
blue_towers = [
    t.SecTower(180, 450, 0, path_blau),
    t.SecTower(410, 450, 0, path_blau),
    t.MainTower(0, path_blau)
]
red_towers = [
    t.SecTower(180, 140, 1, path_rot),
    t.SecTower(410, 140, 1, path_rot),
    t.MainTower(1, path_rot)
]

def empfangen(komm, addr):
    """Läuft in eigenem Thread  empfängt Koordinaten vom Client"""
    while True:
        data = komm.recv(1024)
        if not data:
            break
        print(f"Koordinaten von {addr}: {data.decode()}")
        
        

def senden(komm):
    """Läuft in eigenem Thread – sendet alle 2ms den Spielzustand"""
    while True:
        spielzustand = {
            "truppen": [
                {"id": 1,
                 "art": "Ritter",
                 "health": 100,
                 "x": 10,
                 "y": 20},
                
                {"id": 2,
                 "art": "Archer",
                 "health": 80,
                 "x": 15,
                 "y": 25},
            ]
        }
        komm.send((json.dumps(spielzustand) + "\n").encode())#/n mach zeigt die Grenze zwischen server client
        time.sleep(0.002)  # 2ms

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #gibt port sofort frei wenn der server stoppt
s.bind(("", 50000))
s.listen(2)

try:
    while True:
        komm, addr = s.accept()
        print(f"Client verbunden: {addr}")

        # Für jeden Client 2 Threads starten
        t_empf = threading.Thread(target=empfangen, args=(komm, addr))
        t_send = threading.Thread(target=senden,    args=(komm,))

        t_empf.daemon = True  # Threads sterben wenn Hauptprogramm endet
        t_send.daemon = True

        t_empf.start()
        t_send.start()

finally:
    s.close()