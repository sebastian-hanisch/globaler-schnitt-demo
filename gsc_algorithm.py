"""Kern der Demo (nur Standardbibliothek): der kleinste Schnitt eines ganzen Netzes (globaler Min-Cut).

Ein Netz hat n Standorte und Leitungen `(u, v, w)` mit ganzzahligem Gewicht w; ein **Schnitt** teilt die Standorte in zwei nichtleere Seiten, sein Wert ist die Summe der Gewichte der Leitungen zwischen den Seiten.

* `stoer_wagner`: n - 1 Phasen; in jeder ordnet man die Standorte nach der stärksten Bindung an die schon gewählten (maximale Adjazenzordnung), der **Schnitt der Phase** trennt den letzten Standort vom Rest, dann
  werden die letzten beiden verschmolzen. Der kleinste Schnitt der Phasen ist der kleinste Schnitt des Netzes (exakt).
* `karger_run` und `karger_batch`: **zufällige Kontraktion**: Leitungen in zufälliger Reihenfolge (mit Gewicht als Wahrscheinlichkeit) zusammenziehen, bis zwei Standortgruppen übrig sind; der Wert zwischen ihnen ist ein Schnitt.
  Ein einzelner Lauf trifft einen festen kleinsten Schnitt mit Wahrscheinlichkeit mindestens 2 / (n (n - 1)); darum wiederholt man.
* `all_min_cuts`: Aufzählung aller 2^(n-1) Schnitte (kleine Netze) als Prüfer und für die Zahl und Gestalt aller kleinsten Schnitte.

Aufwand wird gezählt, nie in Sekunden: bei Stoer–Wagner in **Matrixzugriffen** (jede Bindungsaktualisierung), bei Karger in **Kantenprüfungen** (jede in der Zufallsreihenfolge angesehene Leitung)."""

import math
from dataclasses import dataclass
from itertools import permutations


# --- Hilfen --------------------------------------------------------------------------------------------------------------------------------------


def cut_value(edges, side):
    """Wert des Schnitts zwischen `side` und dem Rest."""
    s = set(side)
    return sum(w for u, v, w in edges if (u in s) != (v in s))


def cut_edges(edges, side):
    """Leitungen (u, v) zwischen `side` und dem Rest."""
    s = set(side)
    return tuple((u, v) for u, v, _w in edges if (u in s) != (v in s))


def min_weighted_degree(n, edges):
    """Kleinster gewichteter Grad: der Schnitt, der nur einen einzelnen Standort abtrennt."""
    deg = [0] * n
    for u, v, w in edges:
        deg[u] += w
        deg[v] += w
    return min(deg) if deg else 0


def is_trivial(n, side):
    """Trennt der Schnitt nur einen einzelnen Standort ab?"""
    return len(side) == 1 or len(side) == n - 1


def canonical(n, side):
    """Seite, die den Standort 0 enthält (jeder Schnitt hat zwei Darstellungen)."""
    s = set(side)
    return tuple(sorted(s if 0 in s else set(range(n)) - s))


# --- Stoer–Wagner --------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Phase:
    order: tuple            # Reihenfolge der Vertreter (verschmolzene Standorte), in der sie zur Menge A kommen
    bindings: tuple         # Bindung jedes Vertreters an A im Moment des Hinzufügens (der erste hat 0)
    last: int               # letzter Vertreter
    before: int             # vorletzter Vertreter: mit ihm wird verschmolzen
    cut: int                # Schnitt der Phase = Bindung des letzten Vertreters
    last_group: tuple       # ursprüngliche Standorte hinter dem letzten Vertreter (die eine Seite des Schnitts der Phase)
    groups: tuple           # vor der Phase: ((Vertreter, (ursprüngliche Standorte)), ...)
    steps: int


@dataclass(frozen=True)
class StoerWagner:
    value: int
    side: tuple             # eine Seite des kleinsten Schnitts (die letzte Gruppe der besten Phase), sortiert
    best_phase: int         # Index der ersten Phase mit dem kleinsten Schnitt, -1 ohne Phasen
    phases: tuple
    steps: int


def stoer_wagner(n, edges):
    """Stoer–Wagner mit Gewichtsmatrix: n - 1 Phasen, jede ordnet die aktiven Vertreter nach der stärksten Bindung an A (bei Gleichstand der kleinste Vertreter, Start ist der kleinste Vertreter)."""
    if n < 2:
        return StoerWagner(0, (), -1, (), 0)
    w = [[0] * n for _ in range(n)]
    for u, v, wt in edges:
        w[u][v] += wt
        w[v][u] += wt
    members = {v: [v] for v in range(n)}
    active = list(range(n))
    phases, total = [], 0
    while len(active) > 1:
        snapshot = tuple((v, tuple(sorted(members[v]))) for v in active)
        key = {v: 0 for v in active}
        rest = list(active)
        order, bindings, steps = [], [], 0
        while rest:
            best = min(rest, key=lambda v: (-key[v], v))
            order.append(best)
            bindings.append(key[best])
            rest.remove(best)
            for v in rest:
                key[v] += w[best][v]
            steps += len(rest)
        last, before = order[-1], order[-2]
        phases.append(Phase(tuple(order), tuple(bindings), last, before, bindings[-1], tuple(sorted(members[last])), snapshot, steps))
        total += steps
        for x in active:
            if x != last and x != before:
                w[before][x] += w[last][x]
                w[x][before] = w[before][x]
        members[before].extend(members[last])
        active.remove(last)
    best_phase = min(range(len(phases)), key=lambda i: (phases[i].cut, i))
    return StoerWagner(phases[best_phase].cut, phases[best_phase].last_group, best_phase, tuple(phases), total)


# --- Karger --------------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class KargerRun:
    value: int
    side: tuple             # Seite mit dem Standort 0, sortiert
    contracted: tuple       # Indizes der zusammengezogenen Leitungen in der Reihenfolge der Kontraktion
    steps: int              # angesehene Leitungen


def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def edge_order(edges, rng):
    """Zufällige Reihenfolge der Leitungen mit Gewicht als Wahrscheinlichkeit: Schlüssel -ln(1 - r) / w (bei gleichen Gewichten eine gleichverteilte Reihenfolge); Leitungen ohne Gewicht kommen zuletzt."""
    keys = []
    for i, (_u, _v, w) in enumerate(edges):
        r = rng.random()
        keys.append((-math.log(1.0 - r) / w if w > 0 else math.inf, i))
    return [i for _k, i in sorted(keys)]


def contract(n, edges, order, stop=2):
    """Zieht die Leitungen in `order` zusammen (Leitungen innerhalb einer Gruppe werden übersprungen), bis nur noch `stop` Gruppen übrig sind. Gibt (Vertreter-Feld, zusammengezogene Leitungen, Prüfungen) zurück."""
    parent = list(range(n))
    comps, contracted, steps = n, [], 0
    for i in order:
        if comps <= stop:
            break
        steps += 1
        u, v, _w = edges[i]
        ru, rv = _find(parent, u), _find(parent, v)
        if ru != rv:
            parent[rv] = ru
            contracted.append(i)
            comps -= 1
    return parent, tuple(contracted), steps


def karger_run(n, edges, rng):
    """Ein Lauf der zufälligen Kontraktion."""
    if n < 2:
        return KargerRun(0, (), (), 0)
    parent, contracted, steps = contract(n, edges, edge_order(edges, rng))
    root0 = _find(parent, 0)
    side = tuple(v for v in range(n) if _find(parent, v) == root0)
    return KargerRun(cut_value(edges, side), side, contracted, steps)


@dataclass(frozen=True)
class KargerBatch:
    values: tuple
    sides: tuple
    contracted: tuple       # je Lauf die Indizes der zusammengezogenen Leitungen (für den Ablauf in der App)
    steps: int

    @property
    def runs(self):
        return len(self.values)


def karger_batch(n, edges, runs, rng):
    values, sides, contracted, steps = [], [], [], 0
    for _ in range(runs):
        run = karger_run(n, edges, rng)
        values.append(run.value)
        sides.append(run.side)
        contracted.append(run.contracted)
        steps += run.steps
    return KargerBatch(tuple(values), tuple(sides), tuple(contracted), steps)


def karger_guarantee(n):
    """Untere Schranke für die Wahrscheinlichkeit, dass ein Lauf einen **bestimmten** kleinsten Schnitt trifft: 2 / (n (n - 1)) = 1 / C(n, 2)."""
    return 2.0 / (n * (n - 1)) if n >= 2 else 1.0


def repetitions_for(p, confidence):
    """Zahl der Wiederholungen, damit mit Wahrscheinlichkeit `confidence` mindestens ein Lauf trifft, wenn jeder mit `p` trifft (None, wenn p = 0)."""
    if p <= 0:
        return None
    if p >= 1:
        return 1
    return max(1, math.ceil(math.log(1.0 - confidence) / math.log(1.0 - p)))


def exact_distribution(n, edges):
    """Alle m! Kantenreihenfolgen (ungewichtet, m <= 8): wie oft endet die Kontraktion bei welcher Seite? Gibt {Seite: Anzahl} zurück; nur als exakte Gegenprobe für Karger."""
    counts = {}
    for order in permutations(range(len(edges))):
        parent, _c, _s = contract(n, edges, order)
        root0 = _find(parent, 0)
        side = tuple(v for v in range(n) if _find(parent, v) == root0)
        counts[side] = counts.get(side, 0) + 1
    return counts


# --- Aufzählung aller Schnitte -------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MinCuts:
    value: int
    sides: tuple            # alle kleinsten Schnitte als Seite mit dem Standort 0, sortiert
    trivial: int            # wie viele davon nur einen Standort abtrennen

    @property
    def count(self):
        return len(self.sides)


def all_min_cuts(n, edges):
    """Zählt alle 2^(n-1) - 1 Schnitte (Standort 0 liegt immer auf der Seite S) und gibt die kleinsten zurück; nur für kleine Netze (n <= 20)."""
    if n < 2:
        return MinCuts(0, (), 0)
    nb = [[] for _ in range(n)]
    dw = [0] * n
    for u, v, w in edges:
        nb[u].append((v, w))
        nb[v].append((u, w))
        dw[u] += w
        dw[v] += w
    total = 1 << (n - 1)
    cut = [0] * total
    cut[0] = dw[0]
    for mask in range(1, total):
        p = mask.bit_length() - 1
        prev = mask ^ (1 << p)
        v = p + 1
        inside = 0
        for u, w in nb[v]:
            if u == 0 or (prev >> (u - 1)) & 1:
                inside += w
        cut[mask] = cut[prev] + dw[v] - 2 * inside
    best = min(cut[m] for m in range(total - 1))                  # die Maske mit allen Bits wäre S = V
    sides = []
    for mask in range(total - 1):
        if cut[mask] == best:
            sides.append(tuple([0] + [v + 1 for v in range(n - 1) if (mask >> v) & 1]))
    sides = tuple(sorted(sides))
    return MinCuts(best, sides, sum(1 for s in sides if is_trivial(n, s)))
