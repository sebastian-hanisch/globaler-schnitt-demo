"""Die Instanz dieser Demo: ein Verbindungsnetz zwischen Standorten (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed, mit ganzzahligen Leitungsgewichten (Kapazitäten oder Stärken).

Acht Netztypen: das handgebaute Lehrbeispiel (zwei Werke), die Extremfälle Kreis und Baum, Zufallsnetz, Gitter, Ring mit Abkürzungen, skalenfreies Netz und Verbundnetz (drei Regionen). Jedes Netz ist einfach (keine
Schleifen, keine Mehrfachverbindungen) und **zusammenhängend**; Standorte sind von 0 bis n - 1 durchnummeriert (die Anzeige zählt ab 1). Der Zufall kommt nur aus `random.Random(...)` mit `random()`, damit die Netze und alle
daraus gezählten Zahlen auf jeder Plattform gleich bleiben (kein `hash()`, kein numpy-Zufall). Die Karte (`xy`) dient nur der Anzeige."""

import math
import random
from dataclasses import dataclass

import numpy as np

import gsc_constants as C


@dataclass(frozen=True)
class Instance:
    n: int
    edges: tuple                # ((u, v, w), ...) mit u < v, sortiert; w ganze Zahl >= 1
    xy: np.ndarray              # (n, 2), nur zur Anzeige
    kind: str
    labels: tuple = ()          # Knotennamen (nur Lehrbeispiel), sonst leer

    @property
    def m(self):
        return len(self.edges)

    @property
    def pairs(self):
        return tuple((u, v) for u, v, _w in self.edges)

    @property
    def total_weight(self):
        return sum(w for _u, _v, w in self.edges)

    def name(self, v):
        return self.labels[v] if self.labels else str(v + 1)

    def weighted_degrees(self):
        d = [0] * self.n
        for u, v, w in self.edges:
            d[u] += w
            d[v] += w
        return d


def make_rng(seed, salt):
    return random.Random(int(seed) * 1_000_003 + int(salt))


def _below(rng, k):
    """Gleichverteilte ganze Zahl in 0 .. k - 1 aus `random()` allein."""
    return min(k - 1, int(rng.random() * k))


def _shuffle(items, rng):
    """Fisher–Yates mit `random()` (plattformstabil)."""
    items = list(items)
    for i in range(len(items) - 1, 0, -1):
        j = _below(rng, i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def _adj_from_pairs(n, pairs):
    nb = [set() for _ in range(n)]
    for u, v in pairs:
        if u != v:
            nb[u].add(v)
            nb[v].add(u)
    return tuple(tuple(sorted(s)) for s in nb)


def _components(adj):
    comp, seen = [], [False] * len(adj)
    for s in range(len(adj)):
        if seen[s]:
            continue
        seen[s] = True
        stack, cur = [s], [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
                    cur.append(v)
        comp.append(sorted(cur))
    return comp


def _ensure_connected(n, pairs):
    """Verbindet übrig gebliebene Teile mit dem Teil des Standorts 0 (je eine Leitung vom kleinsten Standort des Teils zum Standort 0)."""
    adj = _adj_from_pairs(n, pairs)
    comps = _components(adj)
    pairs = set(pairs)
    for comp in comps[1:]:
        pairs.add((0, comp[0]))
    return sorted(pairs)


def random_connected(n, m, rng):
    """Zufälliger zusammenhängender einfacher Graph mit genau max(n - 1, min(m, n(n-1)/2)) Kanten: erst ein Zufallsbaum, dann zufällige weitere Kanten."""
    m = max(n - 1, min(int(m), n * (n - 1) // 2))
    order = _shuffle(range(n), rng)
    pairs = set()
    for i in range(1, n):
        a, b = order[i], order[_below(rng, i)]
        pairs.add((min(a, b), max(a, b)))
    while len(pairs) < m:
        a, b = _below(rng, n), _below(rng, n)
        if a != b:
            pairs.add((min(a, b), max(a, b)))
    return sorted(pairs)


def grid_pairs(side):
    out = []
    for r in range(side):
        for c in range(side):
            v = r * side + c
            if c + 1 < side:
                out.append((v, v + 1))
            if r + 1 < side:
                out.append((v, v + side))
    return out


def ring_pairs(n, rng, k=C.RING_NEIGHBOURS, rewire=C.RING_REWIRE):
    """Ringgitter (jeder Standort mit den k/2 nächsten Nachbarn je Seite) mit Abkürzungen: jede „vorwärts“ laufende Leitung wird mit Wahrscheinlichkeit `rewire` an einen zufälligen anderen Standort umgehängt."""
    half = max(1, k // 2)
    pairs = set()
    for v in range(n):
        for d in range(1, half + 1):
            w = (v + d) % n
            if w != v:
                pairs.add((min(v, w), max(v, w)))
    for v in range(n):
        for d in range(1, half + 1):
            w = (v + d) % n
            e = (min(v, w), max(v, w))
            if w == v or e not in pairs or rng.random() >= rewire:
                continue
            for _ in range(20):
                x = _below(rng, n)
                f = (min(v, x), max(v, x))
                if x != v and f not in pairs:
                    pairs.discard(e)
                    pairs.add(f)
                    break
    return _ensure_connected(n, sorted(pairs))


def scalefree_pairs(n, rng, m=C.SCALEFREE_M):
    """Bevorzugte Anbindung (Barabási–Albert): Start ist ein vollständiges Netz aus m + 1 Standorten, jeder neue Standort hängt sich an m verschiedene bestehende, mit Wahrscheinlichkeit proportional zum Grad."""
    n = max(n, m + 1)
    pairs = [(a, b) for a in range(m + 1) for b in range(a + 1, m + 1)]
    pool = [v for e in pairs for v in e]
    for v in range(m + 1, n):
        targets = set()
        while len(targets) < m:
            targets.add(pool[_below(rng, len(pool))])
        for t in sorted(targets):
            pairs.append((t, v))
            pool.extend((t, v))
    return sorted(pairs)


def region_sizes(n, k=C.REGIONS):
    base, extra = divmod(n, k)
    return [base + (1 if i < extra else 0) for i in range(k)]


def verbund_pairs(n, deg, links, rng):
    """Drei Regionen, innen zusammenhängend mit dem mittleren Grad `deg`; zwischen je zwei Regionen genau `links` verschiedene Leitungen (höchstens alle Paare)."""
    sizes = region_sizes(n)
    starts = [sum(sizes[:i]) for i in range(len(sizes))]
    pairs = []
    for size, s0 in zip(sizes, starts):
        for a, b in random_connected(size, round(size * deg / 2), rng):
            pairs.append((s0 + a, s0 + b))
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            want = min(int(links), sizes[i] * sizes[j])
            chosen = set()
            while len(chosen) < want:
                chosen.add((starts[i] + _below(rng, sizes[i]), starts[j] + _below(rng, sizes[j])))
            pairs.extend(sorted(chosen))
    return sorted(set(pairs))


def cycle_pairs(n):
    return sorted((min(v, (v + 1) % n), max(v, (v + 1) % n)) for v in range(n))


def tree_pairs(n, rng):
    """Zufälliger Baum: ein Standort nach dem anderen (in zufälliger Reihenfolge) hängt sich an einen zufälligen früheren."""
    order = _shuffle(range(n), rng)
    pairs = set()
    for i in range(1, n):
        a, b = order[i], order[_below(rng, i)]
        pairs.add((min(a, b), max(a, b)))
    return sorted(pairs)


def assign_weights(pairs, mode, rng):
    """Gewicht je Leitung: alle 1 oder zufällig 1 bis `WEIGHT_MAX`."""
    if mode not in C.WEIGHTS:
        raise ValueError(f"unbekannte Gewichtung {mode}")
    return tuple((u, v, 1 if mode == "unit" else 1 + _below(rng, C.WEIGHT_MAX)) for u, v in pairs)


# --- Karte (nur Anzeige) --------------------------------------------------------------------------------------------------------------------------


def spring_layout(n, pairs, rng, iterations=90):
    """Einfache Federkraft-Anordnung (Fruchterman–Reingold) mit fester Startverteilung aus `random()`."""
    pos = np.array([[rng.random() * 2 - 1, rng.random() * 2 - 1] for _ in range(n)], dtype=float)
    if n < 2:
        return pos
    edge = np.array(pairs, dtype=int).reshape(-1, 2)
    k = math.sqrt(4.0 / n)
    temp = 0.2
    for _ in range(iterations):
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.maximum(np.linalg.norm(delta, axis=2), 1e-3)
        force = (delta / dist[:, :, None]) * (k * k / dist)[:, :, None]
        disp = force.sum(axis=1)
        if len(edge):
            d = pos[edge[:, 0]] - pos[edge[:, 1]]
            dl = np.maximum(np.linalg.norm(d, axis=1), 1e-3)
            pull = (d / dl[:, None]) * (dl * dl / k)[:, None]
            np.add.at(disp, edge[:, 0], -pull)
            np.add.at(disp, edge[:, 1], pull)
        length = np.maximum(np.linalg.norm(disp, axis=1), 1e-9)
        pos += (disp / length[:, None]) * np.minimum(length, temp)[:, None]
        temp *= 0.96
    pos -= pos.mean(axis=0)
    span = max(float(np.abs(pos).max()), 1e-9)
    return pos / span


def region_layout(n, rng):
    sizes = region_sizes(n)
    centers = [(0.0, 1.0), (-0.87, -0.5), (0.87, -0.5)]
    pts = []
    for size, (cx, cy) in zip(sizes, centers):
        for _ in range(size):
            r, a = 0.42 * math.sqrt(rng.random()), 2 * math.pi * rng.random()
            pts.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    return np.array(pts, dtype=float)


# --- Lehrbeispiel -----------------------------------------------------------------------------------------------------------------------------------


TEXTBOOK_LABELS = ("A", "B", "C", "D", "E", "F", "G", "H")
TEXTBOOK_PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7), (0, 4), (0, 5))


def textbook_instance():
    """**Zwei Werke**, acht Standorte, 14 Leitungen mit Gewicht 1: Werk 1 sind A, B, C, D (jeder mit jedem), Werk 2 sind E, F, G, H (jeder mit jedem), dazu die Leitungen A-E und A-F. Von Hand: der kleinste Schnitt hat die
    Größe **2** (A-E und A-F) und ist der einzige; der kleinste Schnitt an einem einzelnen Standort ist 3 (B, C, D, G oder H)."""
    xy = np.array([[-1.0, 0.0], [-2.4, 1.1], [-2.4, -1.1], [-3.4, 0.0], [1.2, 0.9], [1.2, -0.9], [2.8, 1.1], [2.8, -1.1]], dtype=float)
    return Instance(8, tuple((u, v, 1) for u, v in sorted(TEXTBOOK_PAIRS)), xy, "textbook", TEXTBOOK_LABELS)


def make_instance(kind, n, deg=C.DEFAULT_DEG, links=C.DEFAULT_LINKS, weights=C.DEFAULT_WEIGHTS, seed=C.DEFAULT_SEED):
    """Das Netz zu den Einstellungen. Das Gitter hat side² Standorte (side = Rundung der Wurzel aus n); das Lehrbeispiel ignoriert alles außer dem Typ."""
    if kind not in C.KINDS:
        raise ValueError(f"unbekannter Netztyp {kind}")
    if kind == "textbook":
        return textbook_instance()
    n = int(n)
    if n < 4:
        raise ValueError("mindestens 4 Standorte")
    rng = make_rng(seed, 5)
    layout_rng = make_rng(seed, 77)
    weight_rng = make_rng(seed, 313)
    if kind == "grid":
        side = max(2, round(math.sqrt(n)))
        pairs = grid_pairs(side)
        n = side * side
        xy = np.array([[c, r] for r in range(side) for c in range(side)], dtype=float)
        xy = (xy - xy.mean(axis=0)) / max(side - 1, 1) * 2
    elif kind == "cycle":
        pairs = cycle_pairs(n)
        xy = np.array([[math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)] for i in range(n)], dtype=float)
    elif kind == "ring":
        pairs = ring_pairs(n, rng)
        xy = np.array([[math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)] for i in range(n)], dtype=float)
    elif kind == "verbund":
        pairs = verbund_pairs(n, float(deg), int(links), rng)
        xy = region_layout(n, layout_rng)
    elif kind == "scalefree":
        pairs = scalefree_pairs(n, rng)
        n = max(n, C.SCALEFREE_M + 1)
        xy = spring_layout(n, pairs, layout_rng)
    elif kind == "tree":
        pairs = tree_pairs(n, rng)
        xy = spring_layout(n, pairs, layout_rng)
    else:
        pairs = random_connected(n, round(n * float(deg) / 2), rng)
        xy = spring_layout(n, pairs, layout_rng)
    return Instance(n, assign_weights(sorted(set(pairs)), weights, weight_rng), xy, kind)
