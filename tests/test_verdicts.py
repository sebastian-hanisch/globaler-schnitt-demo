"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; ohne diese Datei überleben fast alle Mutanten der Verdikt-Arithmetik."""

import dataclasses

import gsc_algorithm as A
import gsc_evaluation as ev


# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

def test_question_names_the_cut_the_count_the_degree_and_the_karger_rates():
    kind, text = ev.verdict_question(ev.analyse(ev.Settings()))                                  # Lehrbeispiel: 8 Standorte, 14 Leitungen, kleinster Schnitt 2, kleinster Standort 3
    assert kind == "info"
    assert "**Bei 8 Standorten und 14 Leitungen ist der kleinste Schnitt 2; der kleinste Schnitt an einem einzelnen Standort ist 3.**" in text
    assert "Stoer–Wagner trennt A, B, C, D vom Rest (eine echte Teilung). Es gibt genau einen kleinsten Schnitt." in text
    assert ("Ein Lauf von Karger trifft einen kleinsten Schnitt in 23 % der 1.000 Läufe (Schranke für einen bestimmten Schnitt: 0,0357); "
            "für 99 % Sicherheit genügen gemessen 18 Läufe, die Schranke verlangt 127.") in text


def test_question_names_a_trivial_cut_with_the_smaller_side_and_several_cuts():
    a = ev.analyse(ev.Settings("cycle", 16, runs=100))
    text = ev.verdict_question(a)[1]
    assert "Stoer–Wagner trennt 16 vom Rest (ein einzelner Standort). Es gibt 120 kleinste Schnitte." in text and "genügt gemessen 1 Lauf, die Schranke verlangt 551." in text
    b = ev.analyse(ev.Settings("random", 16, 5.0, 2, "unit", 7, 100))
    assert "Es gibt 5 kleinste Schnitte, alle um einen einzelnen Standort." in ev.verdict_question(b)[1]


def test_question_without_the_enumeration_and_without_a_hit():
    a = ev.analyse(ev.Settings("random", 30, 4.0, 2, "unit", 1, 100))
    text = ev.verdict_question(a)[1]
    assert "Es gibt" not in text
    none = dataclasses.replace(ev.analyse(ev.Settings()), batch=dataclasses.replace(ev.analyse(ev.Settings()).batch, values=(99,) * 5, sides=((0,),) * 5, contracted=((),) * 5))
    assert "kein gemessener Lauf traf einen kleinsten Schnitt, die Schranke verlangt 127 Läufe für 99 % Sicherheit." in ev.verdict_question(none)[1]


# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

def _x_row(label="Kreis", nets=12, checks=9660, wrong=0, n=16, runs=400):
    return {"label": label, "nets": nets, "checks": checks, "wrong": wrong, "n": n, "runs": runs}


def test_exact_counts_nets_and_checks_and_warns_on_any_deviation():
    kind, text = ev.verdict_exact([_x_row(), _x_row("Baum")])
    assert kind == "info"
    assert ("Auf 24 Netzen mit 16 Standorten (2 Netztypen) stimmen 19.320 Prüfungen mit der Aufzählung aller Schnitte überein: Stoer–Wagner trifft den kleinsten Wert, und jeder der je 400 Läufe von Karger "
            "meldet einen echten Schnitt, nie einen kleineren als den kleinsten, und trifft er einen kleinsten, steht er in der Aufzählung. Abweichungen: 0.") == text
    kind2, text2 = ev.verdict_exact([_x_row(), _x_row("Baum", wrong=4)])
    assert kind2 == "warning" and text2 == "Auf 24 Netzen weichen 4 von 19.320 Prüfungen von der Aufzählung aller Schnitte ab."


# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

def _t_row(label, weights="unit", nets=12, all_trivial=12, equal=12, sum_cuts=20, max_cuts=3):
    return {"label": label, "weights": weights, "nets": nets, "all_trivial": all_trivial, "equal_degree": equal, "sum_cuts": sum_cuts, "max_cuts": max_cuts}


def test_trivial_counts_the_nets_names_the_exceptions_and_compares_with_random_weights():
    rows = [_t_row("Zufallsnetz"), _t_row("Kreis", all_trivial=0, max_cuts=120), _t_row("Gitter", all_trivial=10),
            _t_row("Zufallsnetz", "random", equal=11), _t_row("Kreis", "random", all_trivial=0, equal=5), _t_row("Gitter", "random", equal=9)]
    kind, text = ev.verdict_trivial(rows)
    assert kind == "info"
    assert ("Bei gleichen Gewichten sind auf 36 Netzen (3 Netztypen) in 22 (61 %) alle kleinsten Schnitte ein einzelner Standort. Kein Netz mit nur trivialen Schnitten gibt es bei: Kreis. "
            "Die kleinste Zahl kleinster Schnitte ist 1, die größte 120 (Kreis: alle C(n, 2) Schnitte durch zwei Leitungen). Der Wert des kleinsten Schnitts ist gleich dem des kleinsten einzelnen "
            "Standorts in 36 von 36 Netzen bei gleichen Gewichten und in 25 von 36 bei zufälligen Gewichten.") == text
    only_unit = ev.verdict_trivial([_t_row("Zufallsnetz"), _t_row("Gitter")])[1]
    assert "Kein Netz mit nur trivialen" not in only_unit and "zufälligen Gewichten" not in only_unit


# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

def _k_row(label="Zufallsnetz", rate=0.5, fixed=0.2, n=16):
    return {"label": label, "mean_rate": rate, "mean_fixed": fixed, "guarantee": 1 / 120, "n": n}


def _c_rows():
    return [{"n": 5, "kind": "exact", "cuts": 10, "orders": 120, "min_count": 12, "max_count": 12, "rate": 0.1, "formula": 0.1},
            {"n": 6, "kind": "exact", "cuts": 15, "orders": 720, "min_count": 48, "max_count": 48, "rate": 0.0667, "formula": 0.0667},
            {"n": 16, "kind": "measured", "cuts": 120, "runs": 20000, "hits": 167, "rate": 0.00835, "formula": 1 / 120}]


def test_karger_names_the_range_the_extremes_and_the_exact_cycle_numbers():
    rows = [_k_row("Ring", 0.2548), _k_row("Skalenfrei", 0.7392), _k_row("Kreis", 1.0), _k_row("Baum", 1.0)]
    kind, text = ev.verdict_karger(rows, _c_rows())
    assert kind == "info"
    assert ("Ein Lauf von Karger trifft auf den Modellnetzen mit 16 Standorten im Mittel einen kleinsten Schnitt mit Wahrscheinlichkeit zwischen 25 % (Ring) und 74 % (Skalenfrei); "
            "die Schranke für einen bestimmten Schnitt ist 0,0083. Bei Kreis und Baum ist jeder mögliche Ausgang ein kleinster Schnitt: Jeder Lauf trifft. Auf dem Kreis ist die Schranke scharf: "
            "Für 5 und 6 Standorte trifft jeder der C(n, 2) kleinsten Schnitte bei genau 2 (n − 2)! von n! Kantenreihenfolgen (n = 5: 12 von 120), also mit 1 / C(n, 2); bei 16 Standorten gemessen "
            "0,0083 in 20.000 Läufen (Formel 0,0083).") == text


def test_karger_warns_when_the_cycle_is_not_uniform_and_handles_missing_pieces():
    crooked = _c_rows()
    crooked[0] = dict(crooked[0], max_count=13)
    assert ev.verdict_karger([_k_row()], crooked)[0] == "warning"
    only_full = ev.verdict_karger([_k_row("Kreis", 1.0)], [])[1]
    assert only_full == "Ein Lauf von Karger trifft auf allen Modellnetzen mit 16 Standorten einen kleinsten Schnitt; die Schranke für einen bestimmten Schnitt ist 0,0083."
    assert "Auf dem Kreis" not in ev.verdict_karger([_k_row()], [])[1] and "Bei " not in ev.verdict_karger([_k_row()], [])[1]


# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

def _r_row(label, median, worst, never=0, bound=551, n=16):
    return {"label": label, "median": median, "worst": worst, "never": never, "bound": bound, "n": n}


def test_repetitions_name_the_largest_median_the_worst_net_and_the_bound():
    rows = [_r_row("Kreis", 1, 1), _r_row("Ring", 17, 27), _r_row("Zufall", 16, 42)]
    kind, text = ev.verdict_repetitions(rows)
    assert kind == "info"
    assert ("Für 99 % Sicherheit braucht Karger auf den Modellnetzen im Median höchstens 17 Läufe (Ring), im schlechtesten Netz 42 (Zufall); die Schranke verlangt 551 Läufe bei 16 Standorten.") == text
    kind2, text2 = ev.verdict_repetitions(rows[:2] + [_r_row("Zufall", 16, 42, never=2)])
    assert kind2 == "warning" and text2.endswith("In 2 Netzen traf kein gemessener Lauf einen kleinsten Schnitt.")


# --- Experiment 5 --------------------------------------------------------------------------------------------------------------------------

def _cost_row(n, phases, sw, per_run, reps, bound, never=0):
    return {"n": n, "phases": phases, "sw_steps": sw, "karger_steps_per_run": per_run, "reps": reps, "bound_reps": bound, "never": never}


def test_cost_names_phases_accesses_runs_and_the_unit_note():
    rows = [_cost_row(20, 19, 1330.0, 25.5283, 10.0, 873), _cost_row(40, 39, 10660.0, 61.0575, 8.5, 3590), _cost_row(80, 79, 85320.0, 142.9208, 14.0, 14551)]
    kind, text = ev.verdict_cost(rows)
    assert kind == "info"
    assert ("Stoer–Wagner braucht bei 20, 40 und 80 Standorten 19 / 39 / 79 Phasen und 1.330 / 10.660 / 85.320 Matrixzugriffe; ein Lauf von Karger 25,5 / 61,1 / 142,9 Kantenprüfungen. "
            "Bis 99 % Sicherheit rechnet die Schranke mit 873 / 3.590 / 14.551 Läufen, gemessen genügen im Mittel 10 / 8,5 / 14. Matrixzugriffe und Kantenprüfungen sind verschiedene Einheiten: "
            "verglichen werden die Läufe, nicht die Zahlen.") == text
    unknown = rows[:2] + [_cost_row(80, 79, 85320.0, 142.9208, None, 14551, never=1)]
    assert ev.verdict_cost(unknown)[0] == "warning" and "10 / 8,5 / ?" in ev.verdict_cost(unknown)[1]


def test_guarantee_constant_used_by_the_texts():
    assert A.karger_guarantee(16) == 1 / 120
