"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Standorte sind in der Anzeige ab 1 nummeriert (`inst.name`), im Kern ab 0 (das Lehrbeispiel hat Buchstaben)."""

import random
from dataclasses import dataclass, field

import gsc_algorithm as A
import gsc_constants as C
import gsc_scenario as S


@dataclass(frozen=True)
class Settings:
    kind: str = C.DEFAULT_KIND
    n: int = C.DEFAULT_N
    deg: float = C.DEFAULT_DEG
    links: int = C.DEFAULT_LINKS
    weights: str = C.DEFAULT_WEIGHTS
    seed: int = C.DEFAULT_SEED
    runs: int = C.DEFAULT_RUNS


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: S.Instance = field(compare=False, repr=False)
    sw: A.StoerWagner = field(compare=False, repr=False)
    mincuts: A.MinCuts | None = field(compare=False, repr=False)     # nur bei höchstens BRUTE_N Standorten
    batch: A.KargerBatch = field(compare=False, repr=False)

    @property
    def n(self):
        return self.inst.n

    @property
    def m(self):
        return self.inst.m

    @property
    def value(self):
        return self.sw.value

    @property
    def side(self):
        return A.canonical(self.n, self.sw.side)

    @property
    def other_side(self):
        return tuple(v for v in range(self.n) if v not in set(self.side))

    @property
    def degree_cut(self):
        return A.min_weighted_degree(self.n, self.inst.edges)

    @property
    def trivial(self):
        return A.is_trivial(self.n, self.side)

    @property
    def runs(self):
        return self.batch.runs

    @property
    def hits(self):
        return sum(1 for v in self.batch.values if v == self.value)

    @property
    def success_rate(self):
        return self.hits / self.runs if self.runs else 0.0

    @property
    def fixed_rate(self):
        return sum(1 for s in self.batch.sides if s == self.side) / self.runs if self.runs else 0.0

    @property
    def guarantee(self):
        return A.karger_guarantee(self.n)

    @property
    def reps_measured(self):
        return A.repetitions_for(self.success_rate, C.CONFIDENCE)

    @property
    def reps_bound(self):
        return A.repetitions_for(self.guarantee, C.CONFIDENCE)

    @property
    def mean_steps(self):
        return self.batch.steps / self.runs if self.runs else 0.0


def analyse(settings: Settings) -> Analysis:
    inst = S.make_instance(settings.kind, settings.n, settings.deg, settings.links, settings.weights, settings.seed)
    sw = A.stoer_wagner(inst.n, inst.edges)
    mc = A.all_min_cuts(inst.n, inst.edges) if inst.n <= C.BRUTE_N else None
    batch = A.karger_batch(inst.n, inst.edges, settings.runs, random.Random(settings.seed * 31 + C.KARGER_SALT))
    return Analysis(settings, inst, sw, mc, batch)


def validate(a: Analysis) -> list:
    """Unabhängige Prüfung vor der Anzeige: gibt die Liste der Probleme zurück (leer = alles in Ordnung)."""
    problems = []
    edges, n = a.inst.edges, a.n
    if A.cut_value(edges, a.sw.side) != a.sw.value:
        problems.append("Der Schnitt von Stoer–Wagner hat nicht den gemeldeten Wert")
    if not a.sw.side or len(a.sw.side) >= n:
        problems.append("Die Seite von Stoer–Wagner ist leer oder das ganze Netz")
    if len(a.sw.phases) != n - 1 or a.sw.value != min(p.cut for p in a.sw.phases):
        problems.append("Stoer–Wagner hat nicht n - 1 Phasen oder meldet nicht den kleinsten Schnitt der Phasen")
    if a.sw.value > a.degree_cut:
        problems.append("Der kleinste Schnitt ist größer als der kleinste einzelne Standort")
    for value, side in zip(a.batch.values, a.batch.sides):
        if value != A.cut_value(edges, side) or value < a.sw.value or not side or len(side) >= n:
            problems.append("Ein Lauf von Karger meldet einen falschen Schnitt oder einen kleineren als den kleinsten")
            break
    if a.mincuts is not None:
        if a.mincuts.value != a.sw.value:
            problems.append("Stoer–Wagner weicht von der Aufzählung aller Schnitte ab")
        if a.side not in a.mincuts.sides:
            problems.append("Die Seite von Stoer–Wagner ist keiner der kleinsten Schnitte der Aufzählung")
        for side in set(a.batch.sides):
            if A.cut_value(edges, side) == a.sw.value and side not in a.mincuts.sides:
                problems.append("Ein Lauf von Karger trifft einen kleinsten Schnitt, der in der Aufzählung fehlt")
                break
    return problems


# --- Formate ---------------------------------------------------------------------------------------------------------------------------------------


def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x, digits=1) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    if x == int(x):
        return _i(x)
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(share, digits=0) -> str:
    return _dec(round(100.0 * share, digits), digits) if digits else _i(round(100.0 * share))


def _prob(p) -> str:
    """Wahrscheinlichkeit mit drei gültigen Stellen nach dem Komma bei kleinen Werten (0,0083), sonst zwei."""
    return _dec(p, 4 if p < 0.1 else 2)


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------


def verdict_question(a: Analysis):
    """Kernfrage: kleinster Schnitt, trivial oder nicht, und wie oft ein Karger-Lauf ihn trifft."""
    if a.n < 2:
        return "info", "Es gibt keinen Schnitt."
    small = min((a.side, a.other_side), key=len)
    names = ", ".join(a.inst.name(v) for v in small)
    kind = "ein einzelner Standort" if a.trivial else "eine echte Teilung"
    head = f"**Bei {_i(a.n)} Standorten und {_i(a.m)} Leitungen ist der kleinste Schnitt {_i(a.value)}; der kleinste Schnitt an einem einzelnen Standort ist {_i(a.degree_cut)}.**"
    where = f" Stoer–Wagner trennt {names} vom Rest ({kind})."
    count = ""
    if a.mincuts is not None:
        only = ", alle um einen einzelnen Standort" if a.mincuts.count == a.mincuts.trivial and a.mincuts.count > 1 else ""
        count = " Es gibt genau einen kleinsten Schnitt." if a.mincuts.count == 1 else f" Es gibt {_i(a.mincuts.count)} kleinste Schnitte{only}."
    if a.reps_measured:
        sure = f"für {_pct(C.CONFIDENCE)} % Sicherheit {'genügt' if a.reps_measured == 1 else 'genügen'} gemessen {_i(a.reps_measured)} {'Lauf' if a.reps_measured == 1 else 'Läufe'}, die Schranke verlangt {_i(a.reps_bound)}."
    else:
        sure = f"kein gemessener Lauf traf einen kleinsten Schnitt, die Schranke verlangt {_i(a.reps_bound)} Läufe für {_pct(C.CONFIDENCE)} % Sicherheit."
    karger = f" Ein Lauf von Karger trifft einen kleinsten Schnitt in {_pct(a.success_rate)} % der {_i(a.runs)} Läufe (Schranke für einen bestimmten Schnitt: {_prob(a.guarantee)}); {sure}"
    return "info", head + where + count + karger


def verdict_exact(rows):
    nets, checks, wrong = (sum(r[k] for r in rows) for k in ("nets", "checks", "wrong"))
    n, runs = rows[0]["n"], rows[0]["runs"]
    if wrong:
        return "warning", f"Auf {_i(nets)} Netzen weichen {_i(wrong)} von {_i(checks)} Prüfungen von der Aufzählung aller Schnitte ab."
    return "info", (f"Auf {_i(nets)} Netzen mit {_i(n)} Standorten ({len(rows)} Netztypen) stimmen {_i(checks)} Prüfungen mit der Aufzählung aller Schnitte überein: Stoer–Wagner trifft den kleinsten Wert, "
                    f"und jeder der je {_i(runs)} Läufe von Karger meldet einen echten Schnitt, nie einen kleineren als den kleinsten, und trifft er einen kleinsten, steht er in der Aufzählung. Abweichungen: 0.")


def verdict_trivial(rows):
    unit = [r for r in rows if r["weights"] == "unit"]
    nets = sum(r["nets"] for r in unit)
    all_trivial = sum(r["all_trivial"] for r in unit)
    no_trivial = [r for r in unit if r["all_trivial"] == 0]
    names = ", ".join(r["label"] for r in no_trivial)
    text = (f"Bei gleichen Gewichten sind auf {_i(nets)} Netzen ({len(unit)} Netztypen) in {_i(all_trivial)} ({_pct(all_trivial / nets)} %) alle kleinsten Schnitte ein einzelner Standort. "
            + (f"Kein Netz mit nur trivialen Schnitten gibt es bei: {names}. " if no_trivial else "")
            + "Die kleinste Zahl kleinster Schnitte ist 1, die größte "
            + f"{_i(max(r['max_cuts'] for r in unit))} (Kreis: alle C(n, 2) Schnitte durch zwei Leitungen).")
    rand = [r for r in rows if r["weights"] == "random"]
    if rand:
        eq_u, eq_r = sum(r["equal_degree"] for r in unit), sum(r["equal_degree"] for r in rand)
        text += f" Der Wert des kleinsten Schnitts ist gleich dem des kleinsten einzelnen Standorts in {_i(eq_u)} von {_i(nets)} Netzen bei gleichen Gewichten und in {_i(eq_r)} von {_i(sum(r['nets'] for r in rand))} bei zufälligen Gewichten."
    return "info", text


def verdict_karger(rows, cycle):
    full = [r for r in rows if r["mean_rate"] >= 1]
    partial = [r for r in rows if r["mean_rate"] < 1]
    g = rows[0]["guarantee"]
    n = _i(rows[0]["n"])
    if partial:
        lo, hi = min(partial, key=lambda r: r["mean_rate"]), max(partial, key=lambda r: r["mean_rate"])
        text = (f"Ein Lauf von Karger trifft auf den Modellnetzen mit {n} Standorten im Mittel einen kleinsten Schnitt mit Wahrscheinlichkeit zwischen {_pct(lo['mean_rate'])} % ({lo['label']}) und "
                f"{_pct(hi['mean_rate'])} % ({hi['label']}); die Schranke für einen bestimmten Schnitt ist {_prob(g)}.")
        if full:
            text += f" Bei {' und '.join(r['label'] for r in full)} ist jeder mögliche Ausgang ein kleinster Schnitt: Jeder Lauf trifft."
    else:
        text = f"Ein Lauf von Karger trifft auf allen Modellnetzen mit {n} Standorten einen kleinsten Schnitt; die Schranke für einen bestimmten Schnitt ist {_prob(g)}."
    measured = next((c for c in cycle if c["kind"] == "measured"), None)
    exact = [c for c in cycle if c["kind"] == "exact"]
    if measured and exact:
        first = exact[0]
        text += (f" Auf dem Kreis ist die Schranke scharf: Für {', '.join(_i(c['n']) for c in exact[:-1])} und {_i(exact[-1]['n'])} Standorte trifft jeder der C(n, 2) kleinsten Schnitte bei genau 2 (n − 2)! von n! "
                 f"Kantenreihenfolgen (n = {_i(first['n'])}: {_i(first['min_count'])} von {_i(first['orders'])}), also mit 1 / C(n, 2); bei {_i(measured['n'])} Standorten gemessen {_prob(measured['rate'])} in "
                 f"{_i(measured['runs'])} Läufen (Formel {_prob(measured['formula'])}).")
    bad = [c for c in exact if c["min_count"] != c["max_count"]]
    return ("warning" if bad else "info"), text


def verdict_repetitions(rows):
    bound = rows[0]["bound"]
    worst = max((r for r in rows if r["worst"] is not None), key=lambda r: r["worst"])
    med = max((r for r in rows if r["median"] is not None), key=lambda r: r["median"])
    text = (f"Für {_pct(C.CONFIDENCE)} % Sicherheit braucht Karger auf den Modellnetzen im Median höchstens {_i(med['median'])} Läufe ({med['label']}), im schlechtesten Netz {_i(worst['worst'])} ({worst['label']}); "
            f"die Schranke verlangt {_i(bound)} Läufe bei {_i(rows[0]['n'])} Standorten.")
    never = sum(r["never"] for r in rows)
    if never:
        text += f" In {_i(never)} Netzen traf kein gemessener Lauf einen kleinsten Schnitt."
    return ("warning" if never else "info"), text


def verdict_cost(rows):
    parts = ", ".join(f"{_i(r['n'])}" for r in rows[:-1]) + f" und {_i(rows[-1]['n'])}"
    sw = " / ".join(_i(r["sw_steps"]) for r in rows)
    k = " / ".join(_dec(r["karger_steps_per_run"]) for r in rows)
    text = (f"Stoer–Wagner braucht bei {parts} Standorten {' / '.join(_i(r['phases']) for r in rows)} Phasen und {sw} Matrixzugriffe; ein Lauf von Karger {k} Kantenprüfungen. "
            f"Bis {_pct(C.CONFIDENCE)} % Sicherheit rechnet die Schranke mit {' / '.join(_i(r['bound_reps']) for r in rows)} Läufen, gemessen genügen im Mittel "
            f"{' / '.join(_dec(r['reps']) if r['reps'] is not None else '?' for r in rows)}. Matrixzugriffe und Kantenprüfungen sind verschiedene Einheiten: verglichen werden die Läufe, nicht die Zahlen.")
    return ("warning" if any(r["never"] for r in rows) else "info"), text
