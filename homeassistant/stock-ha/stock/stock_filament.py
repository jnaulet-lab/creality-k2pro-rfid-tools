#!/usr/bin/env python3
"""Stock de filament pour Home Assistant (sans Spoolman).

Un compteur en grammes par reference de filament (code matiere + couleur).
Les donnees sont dans stock_filament.json (a cote du script), chaque debit est
aussi journalise dans stock_filament_log.csv (ouvrable dans Excel).

Commandes :
  debit  <cle> <libelle> <matiere> <longueur_cm>   retire la consommation
  set    <recherche> <grammes>                      fixe le stock (pesee, inventaire)
  add    <recherche> <grammes>                      ajoute au stock (achat)
  remove <recherche>                                supprime une reference (ex. l'entree de test)
  dump                                              affiche tout en JSON
<recherche> = libelle exact, ou morceau de la cle / du libelle (une seule reference).
"""
import colorsys
import csv
import fcntl
import json
import math
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, "stock_filament.json")
LOG = os.path.join(DIR, "stock_filament_log.csv")
LOCK = os.path.join(DIR, ".stock.lock")

DIAMETER_MM = 1.75
# Densites en g/cm3 ; la premiere correspondance (sous-chaine) l'emporte.
DENSITIES = [
    ("petg", 1.27), ("pctg", 1.23), ("pet", 1.38), ("tpu", 1.21), ("tpe", 1.20),
    ("asa", 1.07), ("abs", 1.04), ("pla", 1.24), ("pva", 1.23), ("hips", 1.04),
    ("pa", 1.14), ("pc", 1.20), ("pp", 0.90),
]
DEFAULT_DENSITY = 1.24


def density(material):
    m = (material or "").lower()
    for name, value in DENSITIES:
        if name in m:
            return value
    return DEFAULT_DENSITY


def grams_from_length(length_cm, material):
    radius_cm = DIAMETER_MM / 20.0
    return length_cm * math.pi * radius_cm ** 2 * density(material)


def color_dot(hexc):
    """Pastille emoji la plus proche d'une couleur hexadecimale (9 categories)."""
    if not re.fullmatch(r"[0-9a-fA-F]{6}", hexc or ""):
        return "\u2754"  # ? : couleur inconnue
    r, g, b = (int(hexc[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, sat, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    if v < 0.20:
        return "\u26ab"  # noir
    if sat < 0.15 or (sat < 0.35 and v > 0.75):
        return "\u26aa" if v >= 0.55 else "\u26ab"  # blanc / gris / pastel
    if 10 <= h < 45 and v < 0.62:
        return "\U0001f7e4"  # marron
    if h < 10 or h >= 345:
        return "\U0001f534"  # rouge
    if h < 45:
        return "\U0001f7e0"  # orange
    if h < 70:
        return "\U0001f7e1"  # jaune
    if h < 165:
        return "\U0001f7e2"  # vert
    if h < 255:
        return "\U0001f535"  # bleu / cyan
    return "\U0001f7e3"  # violet / rose


def split_label(label):
    """'eSUN PLA-Basic #ffffff' -> ('eSUN PLA-Basic', 'ffffff')"""
    m = re.match(r"^(.*?)\s*#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?\s*$", label or "")
    if m:
        return m.group(1).strip(), m.group(2).lower()
    return re.sub(r"\s*#\s*$", "", label or "").strip(), ""


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")


class CorruptData(Exception):
    pass


def load():
    try:
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except ValueError as e:  # JSON invalide (souvent une modification manuelle)
        raise CorruptData("stock_filament.json illisible : %s" % e)


def save(data):
    if os.path.exists(DATA):
        shutil.copy2(DATA, DATA + ".bak")  # derniere sauvegarde valide
    fd, tmp = tempfile.mkstemp(dir=DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, DATA)


def log(row):
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8-sig" if new else "utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        if new:
            w.writerow(["date", "action", "cle", "libelle", "matiere",
                        "longueur_cm", "grammes", "stock_apres_g"])
        w.writerow(row)


def fr(x):
    return str(round(x, 2)).replace(".", ",")


def find(data, query):
    q = query.strip().lower()
    if q in data:
        return q
    exact = [k for k, v in data.items() if v.get("label", "").strip().lower() == q]
    if len(exact) == 1:
        return exact[0]
    hits = [k for k, v in data.items() if q in k or q in v.get("label", "").lower()]
    if len(hits) != 1:
        sys.stderr.write("'%s' : %d correspondance(s) %s\n" % (query, len(hits), hits))
        sys.exit(2)
    return hits[0]


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 1
    cmd = argv[1]
    now = datetime.now().isoformat(timespec="seconds")
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            data = load()
        except CorruptData as e:
            if cmd == "dump":  # le capteur affiche -1 au lieu d'echouer
                print(json.dumps({"count": -1, "total_g": 0, "items": [], "error": str(e)}))
                return 0
            sys.stderr.write(str(e) + " (aucune modification effectuee)\n")
            return 3

        if cmd == "debit":
            key, label, material, length = slug(argv[2]), argv[3], argv[4], float(argv[5])
            if length <= 0:
                return 0
            g = grams_from_length(length, material)
            e = data.setdefault(key, {"label": label, "stock_g": 0.0, "tracked": False})
            e["label"] = label
            e["stock_g"] = round(e["stock_g"] - g, 2)
            e["last_used"] = now
            save(data)
            log([now, "debit", key, label, material, fr(length), fr(-g), fr(e["stock_g"])])

        elif cmd in ("set", "add"):
            key, value = find(data, argv[2]), float(argv[3])
            e = data[key]
            e["stock_g"] = round(value if cmd == "set" else e["stock_g"] + value, 2)
            e["tracked"] = True
            save(data)
            log([now, cmd, key, e["label"], "", "", fr(value), fr(e["stock_g"])])

        elif cmd == "remove":
            key = find(data, argv[2])
            e = data.pop(key)
            save(data)
            log([now, "remove", key, e.get("label", ""), "", "", "", ""])

        elif cmd == "dump":
            items = []
            for k, v in data.items():
                name, color = split_label(v.get("label", ""))
                dot = color_dot(color)
                items.append(dict(key=k, name=name, color=color, dot=dot,
                                  option="%s %s" % (dot, v.get("label", "")), **v))
            items.sort(key=lambda i: i.get("label", "").lower())
            print(json.dumps({
                "count": len(items),
                "total_g": round(sum(i["stock_g"] for i in items if i.get("tracked")), 1),
                "items": items,
            }, ensure_ascii=False))
        else:
            sys.stderr.write("commande inconnue : %s\n" % cmd)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
