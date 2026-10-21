"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Experimentfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Zähler und Mittel über feste Netze (je Netztyp zwölf Netze mit 16 Standorten, feste Zufalls-Seeds; je Netz 400 Läufe von Karger), nie ein einzelner Zufalls-Seed. Aufwand in Matrixzugriffen (Stoer–Wagner) und
Kantenprüfungen (Karger), nicht in Sekunden. Die Zahlen der Vormessung im Einzelplan stammen aus Wegwerfskripten mit anderen Netzen (ohne Kreis und Baum); maßgeblich sind diese hier."""

import math

import pytest

import gsc_algorithm as A
import gsc_constants as C
import gsc_evaluation as ev

from conftest import cached


def test_every_method_agrees_with_the_enumeration_on_every_small_network():
    rows = cached("exactness_rows")
    assert len(rows) == 8 and sum(r["nets"] for r in rows) == 96 and sum(r["checks"] for r in rows) == 77280 and sum(r["wrong"] for r in rows) == 0
    assert all(r["n"] == 16 and r["runs"] == 400 and r["checks"] == 9660 for r in rows)


def test_how_often_the_minimum_cut_is_a_single_location():
    rows = [r for r in cached("trivial_rows") if r["weights"] == "unit"]
    assert [r["label"] for r in rows] == ["Kreis (Extremfall)", "Baum (Extremfall)", "Zufallsnetz, Grad 3", "Zufallsnetz, Grad 5", "Gitter", "Ring mit Abkürzungen", "Skalenfreies Netz", "Verbundnetz, Grad 5"]
    assert [r["all_trivial"] for r in rows] == [0, 0, 10, 12, 12, 12, 12, 0] and sum(r["all_trivial"] for r in rows) == 58 and sum(r["nets"] for r in rows) == 96
    assert [r["equal_degree"] for r in rows] == [12, 12, 12, 12, 12, 12, 12, 0] and sum(r["equal_degree"] for r in rows) == 84
    assert [r["max_cuts"] for r in rows] == [120, 15, 5, 4, 4, 6, 10, 3] and [r["sum_cuts"] for r in rows] == [1440, 180, 28, 19, 48, 40, 88, 36]
    assert [r["some_trivial"] for r in rows] == [12, 12, 12, 12, 12, 12, 12, 0]


def test_random_weights_move_the_cut_away_from_the_single_location():
    rows = [r for r in cached("trivial_rows") if r["weights"] == "random"]
    assert [r["all_trivial"] for r in rows] == [0, 2, 11, 11, 9, 11, 12, 1] and sum(r["all_trivial"] for r in rows) == 57
    assert [r["equal_degree"] for r in rows] == [5, 12, 12, 11, 11, 11, 12, 1] and sum(r["equal_degree"] for r in rows) == 75
    assert [r["max_cuts"] for r in rows] == [15, 6, 3, 2, 4, 3, 2, 3]


def test_the_success_rate_of_one_karger_run_against_the_guarantee():
    rows = cached("karger_rows")
    assert [round(r["mean_rate"], 4) for r in rows] == [1.0, 1.0, 0.5012, 0.331, 0.3556, 0.2548, 0.7392, 0.4529]
    assert [round(r["min_rate"], 4) for r in rows] == [1.0, 1.0, 0.26, 0.105, 0.3075, 0.1575, 0.62, 0.4225]
    assert all(r["guarantee"] == 1 / 120 and r["nets"] == 12 and r["runs"] == 400 and r["n"] == 16 for r in rows)
    assert round(min(r["mean_rate"] for r in rows if r["mean_rate"] < 1) / (1 / 120)) == 31 and round(max(r["mean_rate"] for r in rows if r["mean_rate"] < 1) / (1 / 120)) == 89
    assert [round(r["mean_fixed"], 4) for r in rows][:2] == [0.0083, 0.059]
    # für einen bestimmten kleinsten Schnitt (den von Stoer–Wagner gefundenen) ohne den Kreis: das 7- bis 31-Fache der Schranke
    fixed = [r["mean_fixed"] * 120 for r in rows if r["kind"] != "cycle"]
    assert round(min(fixed)) == 7 and round(max(fixed)) == 31


def test_on_the_cycle_the_guarantee_is_exact_and_measured():
    rows = cached("cycle_rows")
    exact = [r for r in rows if r["kind"] == "exact"]
    assert [(r["n"], r["cuts"], r["orders"], r["min_count"], r["max_count"]) for r in exact] == [(5, 10, 120, 12, 12), (6, 15, 720, 48, 48), (7, 21, 5040, 240, 240)]
    assert all(r["rate"] == pytest.approx(r["formula"]) and r["min_count"] == 2 * math.factorial(r["n"] - 2) for r in exact)
    measured = rows[-1]
    assert (measured["n"], measured["cuts"], measured["runs"], measured["hits"]) == (16, 120, 20000, 167) and round(measured["rate"], 5) == 0.00835 and measured["formula"] == 1 / 120


def test_the_runs_needed_for_99_percent_against_the_bound():
    rows = cached("repetition_rows")
    assert [r["median"] for r in rows] == [1, 1, 8, 16, 11, 17, 4, 8] and [r["worst"] for r in rows] == [1, 1, 16, 42, 13, 27, 5, 9]
    assert all(r["bound"] == 551 and r["never"] == 0 and r["n"] == 16 for r in rows)
    assert A.repetitions_for(A.karger_guarantee(16), C.CONFIDENCE) == 551


def test_the_cost_of_stoer_wagner_against_karger():
    rows = cached("cost_rows")
    assert [r["n"] for r in rows] == [20, 40, 80] and [r["phases"] for r in rows] == [19, 39, 79]
    assert [r["sw_steps"] for r in rows] == [1330.0, 10660.0, 85320.0] and all(r["sw_steps"] == (r["n"] + 1) * r["n"] * (r["n"] - 1) / 6 for r in rows)
    assert [round(r["karger_steps_per_run"], 1) for r in rows] == [25.5, 61.1, 142.9] and [r["reps"] for r in rows] == [10.0, 8.5, 14.0] and all(r["never"] == 0 for r in rows)
    assert [r["bound_reps"] for r in rows] == [873, 3590, 14551] and [r["m"] for r in rows] == [50.0, 100.0, 200.0]


def test_the_two_works_by_hand_and_in_the_app():
    a = ev.analyse(ev.Settings())
    assert (a.n, a.m, a.value, a.degree_cut, a.sw.steps, len(a.sw.phases)) == (8, 14, 2, 3, 84, 7) and a.side == (0, 1, 2, 3) and a.mincuts.count == 1
    assert (a.hits, a.runs, a.reps_measured, a.reps_bound) == (227, 1000, 18, 127) and a.guarantee == 2 / 56


def test_the_presets_reproduce_the_readme_numbers():
    def a(name):
        return ev.analyse(ev.Settings(**C.PRESETS[name]))
    cycle = a("Der Kreis: die Schranke ist scharf")
    assert cycle.mincuts.count == 120 and cycle.success_rate == 1.0 and cycle.runs == 3000
    tree = a("Der Baum: jede Leitung ein kleinster Schnitt")
    assert tree.mincuts.count == 15 and tree.mincuts.trivial == 7
    assert (a("Der kleinste Schnitt ist ein Standort").value, a("Der kleinste Schnitt ist ein Standort").hits / 1000) == (2, 0.243)
    pess = a("Die Schranke ist zu pessimistisch")
    assert (pess.value, pess.mincuts.count, pess.success_rate) == (3, 5, 0.627) and round(pess.success_rate / pess.guarantee) == 75
    verbund = a("Das Verbundnetz hat einen echten Schnitt")
    assert (verbund.value, verbund.degree_cut, len(verbund.side), verbund.mincuts.count, verbund.success_rate) == (2, 4, 11, 3, 0.463)
    weights = a("Gewichte verschieben den Schnitt")
    assert (weights.value, weights.degree_cut, weights.mincuts.count, len(weights.other_side)) == (2, 4, 1, 2)


def test_verdict_texts_quote_the_readme_numbers():
    x, t, k, c, r, cost = (cached(n) for n in ("exactness_rows", "trivial_rows", "karger_rows", "cycle_rows", "repetition_rows", "cost_rows"))
    assert "Auf 96 Netzen mit 16 Standorten (8 Netztypen) stimmen 77.280 Prüfungen" in ev.verdict_exact(x)[1]
    text = ev.verdict_trivial(t)[1]
    assert "in 58 (60 %) alle kleinsten Schnitte ein einzelner Standort" in text and "die größte 120" in text and "in 84 von 96 Netzen bei gleichen Gewichten und in 75 von 96 bei zufälligen Gewichten" in text
    assert "zwischen 25 % (Ring mit Abkürzungen) und 74 % (Skalenfreies Netz)" in ev.verdict_karger(k, c)[1] and "gemessen 0,0083 in 20.000 Läufen" in ev.verdict_karger(k, c)[1]
    assert "im Median höchstens 17 Läufe (Ring mit Abkürzungen), im schlechtesten Netz geschätzt 42 (Zufallsnetz, Grad 5); die Schranke verlangt 551" in ev.verdict_repetitions(r)[1]
    assert "1.330 / 10.660 / 85.320 Matrixzugriffe" in ev.verdict_cost(cost)[1] and "gemessen genügen im Mittel über 4 Netze je Größe 10 / 8,5 / 14" in ev.verdict_cost(cost)[1]


def test_the_experiment_grid_is_the_documented_one():
    assert C.EX_N == 16 and C.EX_RUNS == 400 and C.EX_COST_NS == (20, 40, 80) and C.EX_COST_SEEDS == 4 and len(C.SWEEP_SEEDS) == 12 and C.CONFIDENCE == 0.99
