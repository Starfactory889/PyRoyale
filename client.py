#client
import socket
import threading
import json
#import gui (philip)

def empfangen(s):
    puffer = ""
    while True:
        data = s.recv(4096).decode()
        puffer += data
        
        while "\n" in puffer:
            nachricht, puffer = puffer.split("\n", 1)  # erstes komplettes Paket
            if nachricht: #überprüft ob nachricht leer ist reiner zusatz schutz
                spielzustand = json.loads(nachricht)
                #print(f"Spielzustand: {spielzustand}")

def senden(s):
    """Sendet Koordinaten an den Server"""
    while True:
        koordinaten = input("Koordinaten (x,y): ")  # später durch GUI ersetzen
        if koordinaten == "exit":
            break
        s.send(koordinaten.encode())

# Verbindung zum Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 50000))  # 127.0.0.1 = gleicher PC, sonst Server-IP
print("Verbunden mit Server!")

# 2 Threads starten
t_empf = threading.Thread(target=empfangen, args=(s,))
t_send = threading.Thread(target=senden,    args=(s,))

t_empf.daemon = True
t_send.daemon = True

t_empf.start()
t_send.start()

t_send.join()  # Warten bis senden-Thread fertig ist
s.close()