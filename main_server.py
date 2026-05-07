#import server
import troops as t
import time

ritter_p1  = t.Ritter(x=200, y=200, owner=1)
pekka_p1   = t.Pekka(x=250, y=200, owner=1)
hog_p1     = t.HogRider(x=300, y=200, owner=1)

# ── Truppen Spieler 2 ────────────────────────────────────────
ritter_p2  = t.Ritter(x=250, y=500, owner=2)
pekka_p2   = t.Pekka(x=250, y=400, owner=2)
hog_p2     = t.HogRider(x=300, y=400, owner=2)

# ── Listen für einfache Verwaltung ──────────────────────────
truppen_p1 = [ritter_p1]
truppen_p2 = [ritter_p2]



while True:
    x1,x2 = ritter_p1.next_Step(truppen_p2)
    p1,p2 = ritter_p2.next_Step(truppen_p1)
    print("Koordinaten",x1,x2)
    print("Koordinaten",p1,p2)
    time.sleep(1)