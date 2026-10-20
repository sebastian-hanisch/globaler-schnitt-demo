"""Konstanten: Regler-Grenzen, feste Annahmen, Experiment-Raster, Farben und Presets."""

KINDS = ("textbook", "cycle", "tree", "random", "grid", "ring", "scalefree", "verbund")
KIND_NAMES = {"textbook": "Lehrbeispiel (zwei Werke)", "cycle": "Kreis (Extremfall)", "tree": "Baum (Extremfall)", "random": "Zufallsnetz", "grid": "Gitter",
              "ring": "Ring mit Abkürzungen", "scalefree": "Skalenfreies Netz", "verbund": "Verbundnetz"}
KIND_HELP = {
    "textbook": "Acht Standorte in zwei Werken, von Hand zu rechnen.",
    "cycle": "Alle Standorte auf einem Ring, jede Leitung nur zu den beiden Nachbarn: jeder Schnitt durch zwei Leitungen ist ein kleinster.",
    "tree": "Ein zufälliger Baum: jede Leitung ist eine Brücke, jede einzeln ein kleinster Schnitt.",
    "random": "Zufallsbaum plus zufällige Leitungen; der mittlere Grad ist einstellbar.",
    "grid": "Standorte auf einem Raster, Verbindungen zu den vier Nachbarn.",
    "ring": "Vier nächste Nachbarn auf einem Ring, ein Zehntel der Leitungen führt zu einem zufälligen Standort.",
    "scalefree": "Neue Standorte hängen sich bevorzugt an gut vernetzte an (je zwei Leitungen).",
    "verbund": "Drei Regionen mit dichten inneren Verbindungen und wenigen Leitungen dazwischen (einstellbar).",
}
KIND_REGLER = {
    "textbook": "Das Lehrbeispiel ist fest: Größe, Grad, Leitungen, Gewichte und Zufalls-Seed der Netze wirken hier nicht (die Zahl der Läufe schon).",
    "cycle": "Wirksam: Standorte, Gewichte. Grad und Leitungen zwischen den Regionen wirken nicht.",
    "tree": "Wirksam: Standorte, Gewichte, Zufalls-Seed. Grad und Leitungen zwischen den Regionen wirken nicht.",
    "random": "Wirksam: Standorte, mittlerer Grad, Gewichte, Zufalls-Seed.",
    "grid": "Wirksam: Standorte (gerundet auf ein Quadrat), Gewichte, Zufalls-Seed (nur für die Gewichte).",
    "ring": "Wirksam: Standorte, Gewichte, Zufalls-Seed.",
    "scalefree": "Wirksam: Standorte, Gewichte, Zufalls-Seed.",
    "verbund": "Wirksam: Standorte, mittlerer Grad (in den Regionen), Leitungen zwischen den Regionen, Gewichte, Zufalls-Seed.",
}
WEIGHTS = ("unit", "random")
WEIGHT_NAMES = {"unit": "alle Leitungen 1", "random": "zufällig 1 bis 5"}
WEIGHT_MAX = 5

N_MIN, N_MAX, DEFAULT_N = 6, 80, 16
DEG_MIN, DEG_MAX, DEFAULT_DEG = 2.0, 10.0, 4.0
LINKS_MIN, LINKS_MAX, DEFAULT_LINKS = 1, 8, 2
RUNS = (100, 300, 1000, 3000)
DEFAULT_RUNS = 1000
SEED_MAX, DEFAULT_SEED = 999999, 7
DEFAULT_KIND, DEFAULT_WEIGHTS = "textbook", "unit"
REGIONS = 3
RING_NEIGHBOURS, RING_REWIRE = 4, 0.1
SCALEFREE_M = 2
BRUTE_N = 16                             # größte Netzgröße für die Aufzählung aller Schnitte (App, Test, Experimente)
KARGER_SALT = 90210                      # Zufallsquelle der Karger-Läufe: getrennt von der des Netzes

SWEEP_SEEDS = tuple(range(100000, 100012))   # feste Netze für alle Experimente: nie ein einzelner Zufalls-Seed als Befund
EX_N = 16
EX_RUNS = 400
EX_KINDS = (("cycle", 0.0), ("tree", 0.0), ("random", 3.0), ("random", 5.0), ("grid", 0.0), ("ring", 0.0), ("scalefree", 0.0), ("verbund", 5.0))
EX_COST_NS = (20, 40, 80)
EX_COST_SEEDS = 4
CONFIDENCE = 0.99                        # Ziel der Wiederholungen

COLOR_SIDE_A = "#2F6B65"
COLOR_SIDE_B = "#4c78a8"
COLOR_CUT = "#d1495b"
COLOR_NODE = "#c9d1d3"
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_BAR = "#4c78a8"
COLOR_BAR2 = "#e8a33d"
COLOR_BAR3 = "#2F6B65"
COLOR_GROUPS = ("#2F6B65", "#4c78a8", "#e8a33d", "#8d6cab", "#d1495b", "#6a994e", "#bc6c25", "#457b9d")

PRESETS = {
    "Lehrbeispiel (zwei Werke)": {"kind": "textbook", "n": DEFAULT_N, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "weights": DEFAULT_WEIGHTS, "seed": DEFAULT_SEED, "runs": DEFAULT_RUNS},
    "Der Kreis: die Schranke ist scharf": {"kind": "cycle", "n": 16, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "weights": "unit", "seed": DEFAULT_SEED, "runs": 3000},
    "Der Baum: jede Leitung ein kleinster Schnitt": {"kind": "tree", "n": 16, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "weights": "unit", "seed": 1, "runs": DEFAULT_RUNS},
    "Der kleinste Schnitt ist ein Standort": {"kind": "random", "n": 16, "deg": 5.0, "links": DEFAULT_LINKS, "weights": "unit", "seed": 3, "runs": DEFAULT_RUNS},
    "Die Schranke ist zu pessimistisch": {"kind": "random", "n": 16, "deg": 5.0, "links": DEFAULT_LINKS, "weights": "unit", "seed": 7, "runs": DEFAULT_RUNS},
    "Das Verbundnetz hat einen echten Schnitt": {"kind": "verbund", "n": 16, "deg": 5.0, "links": 1, "weights": "unit", "seed": 1, "runs": DEFAULT_RUNS},
    "Gewichte verschieben den Schnitt": {"kind": "cycle", "n": 16, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "weights": "random", "seed": 1, "runs": DEFAULT_RUNS},
}
PRESET_HELP = {
    "Lehrbeispiel (zwei Werke)": "Zwei Werke mit je vier Standorten, nur über die Leitungen A–E und A–F verbunden: der kleinste Schnitt hat die Größe 2 (von Hand zu prüfen).",
    "Der Kreis: die Schranke ist scharf": "Auf dem Kreis ist jeder Schnitt durch zwei Leitungen ein kleinster: 120 bei 16 Standorten. Jeden einzelnen trifft Karger mit genau 1 / 120, die Schranke ist hier kein Zufall.",
    "Der Baum: jede Leitung ein kleinster Schnitt": "Im Baum ist jede Leitung eine Brücke: 15 kleinste Schnitte bei 16 Standorten, jeder Lauf von Karger trifft einen.",
    "Der kleinste Schnitt ist ein Standort": "Auf diesem Zufallsnetz trennt der kleinste Schnitt nur den am schwächsten angebundenen Standort ab: Stoer–Wagner sagt dasselbe wie der kleinste Grad.",
    "Die Schranke ist zu pessimistisch": "Derselbe Netztyp mit einem Netz, in dem fünf Standorte die kleinste Verbindung haben: Ein Lauf trifft einen kleinsten Schnitt viel öfter, als die Schranke garantiert.",
    "Das Verbundnetz hat einen echten Schnitt": "Drei Regionen, nur eine Leitung zwischen je zwei Regionen: Der kleinste Schnitt trennt eine ganze Region ab und liegt unter dem kleinsten Grad.",
    "Gewichte verschieben den Schnitt": "Auf dem Kreis mit zufälligen Gewichten trennt der kleinste Schnitt zwei Leitungen ab, die zusammen leichter sind als jeder einzelne Standort.",
}
