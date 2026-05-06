import math

def distance(x,y,xgoal,ygoal):
    dx = (xgoal - x)**2
    dy = (ygoal - y)**2
    d = math.sqrt(dx+dy)
    return d

def nächste_Objekt(x:int,y:int,enemys:list):
    min_d = float("inf")
    for enemy in enemys:
        x_enemy  = enemy["x"]
        y_enemy = enemy["y"]
        d = distance(x,y,x_enemy,y_enemy)
        print(d)
        if d < min_d:
            min_d = d
            next_enemy = enemy 
            
    return next_enemy
    
def attack():
    pass
    
troups = [
    {"id": 1, "art": "Ritter", "x": 0,  "y": 0,
     "geschwindigkeit": 1, "reichweite": 2, "schaden": 20},
]

enemys = [
    {"id": 1, "art": "Archer",    "x": 10, "y": 0,  "health": 80},
    {"id": 2, "art": "Riese",     "x": 5,  "y": 5,  "health": 150},
    {"id": 3, "art": "Goblin",    "x": 8,  "y": 3,  "health": 50},
    {"id": 4, "art": "Barbar",    "x": 15, "y": 10, "health": 120},
    {"id": 5, "art": "Drache",    "x": 20, "y": 20, "health": 200},
    {"id": 6, "art": "Skelett",   "x": 3,  "y": 12, "health": 30},
    {"id": 7, "art": "Hexer",     "x": 25, "y": 5,  "health": 90},
    {"id": 8, "art": "Pekka",     "x": 30, "y": 15, "health": 300},
]
        
for troup in troups:
    x_troup = troup["x"]
    y_troup = troup["y"]
    ek = nächste_Objekt(x_troup,y_troup,enemys)
    print((x_troup,y_troup),ek)
    
    