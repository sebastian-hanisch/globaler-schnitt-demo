"""Experimente über feste Netze (nie ein einzelner Zufalls-Seed als Befund). Jede Funktion gibt eine Liste von Zeilen (dict) zurück; Verdikte und Abbildungen lesen nur diese Zeilen.

1. `exactness_rows`: stimmen Stoer–Wagner und die Läufe von Karger mit der Aufzählung aller Schnitte überein?
2. `trivial_rows`: wie oft ist der kleinste Schnitt ein einzelner Standort, und wie viele kleinste Schnitte gibt es (Gewichte 1 und zufällig)?
3. `karger_rows`: Erfolgsrate eines Karger-Laufs gegen die Schranke 2 / (n (n - 1)); dazu `cycle_rows`: auf dem Kreis ist die Schranke scharf (exakt gerechnet und gemessen).
4. `repetition_rows`: Läufe bis 99 % Sicherheit, gemessen gegen die Schranke.
5. `cost_rows`: Aufwand von Stoer–Wagner gegen Karger bis 99 %."""

import math
import random

import gsc_algorithm as A
import gsc_constants as C
import gsc_scenario as S


def kind_label(kind, deg):
    name = C.KIND_NAMES[kind]
    return f"{name}, Grad {deg:g}".replace(".", ",") if kind in ("random", "verbund") else name


def _net(kind, deg, n, seed, weights="unit", links=1):
    return S.make_instance(kind, n, deg, links, weights, seed)


def _rng(seed):
    return random.Random(seed * 31 + C.KARGER_SALT)


def exactness_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        checks = wrong = 0
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_N, seed)
            sw = A.stoer_wagner(inst.n, inst.edges)
            mc = A.all_min_cuts(inst.n, inst.edges)
            results = [sw.value == mc.value, A.cut_value(inst.edges, sw.side) == sw.value, A.canonical(inst.n, sw.side) in mc.sides, len(sw.phases) == inst.n - 1,
                       min(p.cut for p in sw.phases) == sw.value]
            batch = A.karger_batch(inst.n, inst.edges, C.EX_RUNS, _rng(seed))
            for value, side in zip(batch.values, batch.sides):
                results.append(value >= mc.value and value == A.cut_value(inst.edges, side))
                results.append(value != mc.value or A.canonical(inst.n, side) in mc.sides)
            checks += len(results)
            wrong += results.count(False)
        rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": len(C.SWEEP_SEEDS), "checks": checks, "wrong": wrong, "n": C.EX_N, "runs": C.EX_RUNS})
    return rows


def trivial_rows():
    rows = []
    for weights in C.WEIGHTS:
        for kind, deg in C.EX_KINDS:
            row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "weights": weights, "nets": 0, "all_trivial": 0, "some_trivial": 0, "equal_degree": 0, "sum_cuts": 0, "max_cuts": 0, "n": C.EX_N}
            for seed in C.SWEEP_SEEDS:
                inst = _net(kind, deg, C.EX_N, seed, weights)
                mc = A.all_min_cuts(inst.n, inst.edges)
                row["nets"] += 1
                row["all_trivial"] += mc.trivial == mc.count
                row["some_trivial"] += mc.trivial > 0
                row["equal_degree"] += mc.value == A.min_weighted_degree(inst.n, inst.edges)
                row["sum_cuts"] += mc.count
                row["max_cuts"] = max(row["max_cuts"], mc.count)
            rows.append(row)
    return rows


def karger_rows():
    rows = []
    guarantee = A.karger_guarantee(C.EX_N)
    for kind, deg in C.EX_KINDS:
        rates, fixed, reps = [], [], []
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_N, seed)
            sw = A.stoer_wagner(inst.n, inst.edges)
            batch = A.karger_batch(inst.n, inst.edges, C.EX_RUNS, _rng(seed))
            hit = sum(1 for v in batch.values if v == sw.value)
            ref = A.canonical(inst.n, sw.side)
            rates.append(hit / C.EX_RUNS)
            fixed.append(sum(1 for s in batch.sides if s == ref) / C.EX_RUNS)
            reps.append(A.repetitions_for(hit / C.EX_RUNS, C.CONFIDENCE))
        rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": len(rates), "runs": C.EX_RUNS, "n": C.EX_N, "mean_rate": sum(rates) / len(rates), "min_rate": min(rates),
                     "max_rate": max(rates), "mean_fixed": sum(fixed) / len(fixed), "guarantee": guarantee, "reps": reps})
    return rows


def cycle_rows():
    """Auf dem Kreis ist die Schranke scharf: Jeder der C(n, 2) kleinsten Schnitte wird mit genau 1 / C(n, 2) getroffen. Exakt gerechnet über alle Kantenreihenfolgen (n <= 7) und gemessen (n = 16)."""
    rows = []
    for n in (5, 6, 7):
        inst = _net("cycle", 0.0, n, 1)
        dist = A.exact_distribution(inst.n, inst.edges)
        total = math.factorial(inst.m)
        rows.append({"n": n, "kind": "exact", "cuts": len(dist), "orders": total, "min_count": min(dist.values()), "max_count": max(dist.values()), "rate": min(dist.values()) / total, "formula": A.karger_guarantee(n)})
    inst = _net("cycle", 0.0, C.EX_N, 1)
    runs = 20000
    batch = A.karger_batch(inst.n, inst.edges, runs, _rng(0))
    ref = tuple(range(C.EX_N // 2))
    rows.append({"n": C.EX_N, "kind": "measured", "cuts": C.EX_N * (C.EX_N - 1) // 2, "runs": runs, "hits": sum(1 for s in batch.sides if s == ref), "rate": sum(1 for s in batch.sides if s == ref) / runs,
                 "formula": A.karger_guarantee(C.EX_N)})
    return rows


def repetition_rows():
    """Zeilen aus `karger_rows`, bezogen auf 99 % Sicherheit: gemessene Läufe (Median über die Netze, schlechtestes Netz) gegen die Schranke."""
    bound = A.repetitions_for(A.karger_guarantee(C.EX_N), C.CONFIDENCE)
    rows = []
    for r in karger_rows():
        reps = sorted(x for x in r["reps"] if x is not None)
        rows.append({"label": r["label"], "kind": r["kind"], "median": reps[len(reps) // 2] if reps else None, "worst": reps[-1] if reps else None, "never": len(r["reps"]) - len(reps), "bound": bound, "n": C.EX_N})
    return rows


def cost_rows():
    rows = []
    for n in C.EX_COST_NS:
        sw_steps = k_steps = m_total = 0
        reps = []
        for seed in C.SWEEP_SEEDS[:C.EX_COST_SEEDS]:
            inst = _net("random", 5.0, n, seed)
            sw = A.stoer_wagner(inst.n, inst.edges)
            batch = A.karger_batch(inst.n, inst.edges, 300, _rng(seed))
            hit = sum(1 for v in batch.values if v == sw.value)
            sw_steps += sw.steps
            k_steps += batch.steps / batch.runs
            reps.append(A.repetitions_for(hit / batch.runs, C.CONFIDENCE))
            m_total += inst.m
        c = C.EX_COST_SEEDS
        known = [r for r in reps if r is not None]
        bound = A.repetitions_for(A.karger_guarantee(n), C.CONFIDENCE)
        per_run = k_steps / c
        mean_reps = sum(known) / len(known) if known else None
        rows.append({"n": n, "nets": c, "m": m_total / c, "phases": n - 1, "sw_steps": sw_steps / c, "karger_steps_per_run": per_run, "reps": mean_reps, "never": len(reps) - len(known),
                     "bound_reps": bound, "karger_steps": mean_reps * per_run if mean_reps is not None else None, "bound_steps": bound * per_run})
    return rows
