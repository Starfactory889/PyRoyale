# Clash Mini 🏰

Ein lokales 2-Spieler Echtzeit-Strategiespiel inspiriert von Clash Royale, entwickelt mit Python und Pygame.

## Spielprinzip

Zwei Spieler treten gegeneinander an. Jeder Spieler hat drei Türme — zwei Sekundärtürme und einen Hauptturm. Ziel ist es, den gegnerischen Hauptturm zu zerstören, indem man Truppen auf dem Spielfeld platziert. Der erste Spieler dessen Hauptturm fällt, verliert.

## Voraussetzungen

- Python 3.10+
- Pygame

Installation der Abhängigkeiten:
```
pip install pygame
```

## Starten

1. Zuerst den Server starten:
```
python server.py
```

2. Dann Client 1 starten:
```
python client1.py
```

3. Dann Client 2 starten:
```
python client2.py
```

Server und beide Clients können auf demselben PC laufen. Der Server läuft auf Port `50000`.

## Steuerung

| Taste | Aktion |
|-------|--------|
| `1` | Karte 1 auswählen (Pekka) |
| `2` | Karte 2 auswählen (Ritter) |
| `3` | Karte 3 auswählen (HogRider) |
| `4` | Karte 4 auswählen (Drache) |
| Linksklick | Ausgewählte Truppe auf der Karte platzieren |

## Truppen

| Truppe | HP | Schaden | Elixir |
|--------|----|---------|--------|
| Pekka | 1000 | 200 | 7 |
| Ritter | 600 | 120 | 3 |
| HogRider | 500 | 100 | 4 |
| Drache | 800 | 150 | 4 |

## Elixir

- Beide Spieler starten mit 10 Elixir
- Elixir regeneriert sich automatisch über die Zeit
- Maximales Elixir: 10
- Truppen können nur gespawnt werden wenn genug Elixir vorhanden ist

## Türme

Jeder Spieler hat drei Türme:

- 2x Sekundärturm (3000 HP) — links und rechts
- 1x Hauptturm (2000 HP) — in der Mitte

Türme greifen automatisch feindliche Truppen in Reichweite an. Das Spiel endet sobald ein Hauptturm zerstört wird.

## Projektstruktur

```
├── server.py            # Spielserver — verwaltet Spielzustand und Logik
├── client1.py           # Client für Spieler 1
├── client2.py           # Client für Spieler 2 (gespiegelte Perspektive)
├── troops.py            # Truppen- und Turmklassen
├── map.py               # Spielkarte und erlaubte Bereiche
├── entity_animation.py  # Animations-System für Einheiten
└── assets/
    ├── map.png
    ├── Kartenslots.png
    ├── elixir_drop.png
    ├── cards/           # Kartenbilder
    └── türme/           # Turmbilder
```

## Netzwerk

Das Spiel nutzt eine einfache TCP-Verbindung. Server und Clients kommunizieren über JSON-Nachrichten. Der Server sendet den kompletten Spielzustand 30 mal pro Sekunde an beide Clients. Clients senden Spawn-Befehle an den Server wenn eine Truppe platziert wird.
