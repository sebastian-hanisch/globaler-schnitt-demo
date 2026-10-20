"""Auswertung: Analyse des Lehrbeispiels von Hand, Prüfung vor der Anzeige, Formate."""

import dataclasses

import gsc_algorithm as A
import gsc_constants as C
import gsc_evaluation as ev


def _textbook(**over):
    return ev.analyse(ev.Settings(**over))


def test_analysis_of_the_two_works_by_hand():
    a = _textbook()
    assert (a.n, a.m, a.value, a.degree_cut) == (8, 14, 2, 3) and a.side == (0, 1, 2, 3) and a.other_side == (4, 5, 6, 7) and not a.trivial
    assert a.sw.best_phase >= 0 and len(a.sw.phases) == 7 and a.sw.steps == 84 and a.mincuts.count == 1 and a.mincuts.trivial == 0
    assert ev.validate(a) == []


def test_the_karger_batch_of_the_default_settings_is_a_fixed_record():
    a = _textbook()
    assert a.runs == C.DEFAULT_RUNS == 1000 and a.hits == 227 and a.success_rate == 0.227 and a.fixed_rate == 0.227       # ein einziger kleinster Schnitt: Treffer und feste Seite sind dasselbe
    assert a.guarantee == 2 / 56 and a.reps_bound == 127 and a.reps_measured == 18 and 6 < a.mean_steps < 7


def test_default_settings_are_the_constants_and_the_textbook():
    s = ev.Settings()
    assert (s.kind, s.n, s.deg, s.links, s.weights, s.seed, s.runs) == (C.DEFAULT_KIND, C.DEFAULT_N, C.DEFAULT_DEG, C.DEFAULT_LINKS, C.DEFAULT_WEIGHTS, C.DEFAULT_SEED, C.DEFAULT_RUNS) and s.kind == "textbook"


def test_the_same_settings_give_the_same_analysis_and_the_seed_changes_the_network():
    s = ev.Settings("random", 12, 4.0, 2, "unit", 3, 100)
    assert ev.analyse(s) == ev.analyse(s) and ev.analyse(s).inst.edges == ev.analyse(s).inst.edges
    assert ev.analyse(s).inst.edges != ev.analyse(dataclasses.replace(s, seed=4)).inst.edges
    assert ev.analyse(s).batch.values != ev.analyse(dataclasses.replace(s, seed=4)).batch.values


def test_the_run_count_changes_only_the_batch():
    a = _textbook(runs=100)
    assert a.runs == 100 and a.value == 2 and a.inst.edges == _textbook().inst.edges and len(a.batch.values) == 100


def test_trivial_flag_and_other_side():
    a = ev.analyse(ev.Settings("tree", 12, seed=1, runs=100))
    assert a.value == 1 and a.trivial == A.is_trivial(a.n, a.side) and len(a.side) + len(a.other_side) == a.n


def test_validate_names_every_kind_of_error():
    a = _textbook()
    assert ev.validate(a) == []
    assert any("nicht den gemeldeten Wert" in p for p in ev.validate(dataclasses.replace(a, sw=dataclasses.replace(a.sw, side=(0, 4)))))
    assert any("leer oder das ganze Netz" in p for p in ev.validate(dataclasses.replace(a, sw=dataclasses.replace(a.sw, side=()))))
    assert any("Phasen" in p for p in ev.validate(dataclasses.replace(a, sw=dataclasses.replace(a.sw, phases=a.sw.phases[:3]))))
    assert any("größer als der kleinste einzelne Standort" in p for p in ev.validate(dataclasses.replace(a, sw=dataclasses.replace(a.sw, value=99))))
    bad_batch = dataclasses.replace(a.batch, values=(1,) + a.batch.values[1:])
    assert any("Lauf von Karger meldet" in p for p in ev.validate(dataclasses.replace(a, batch=bad_batch)))
    assert any("weicht von der Aufzählung aller Schnitte ab" in p for p in ev.validate(dataclasses.replace(a, mincuts=A.MinCuts(3, a.mincuts.sides, 0))))
    assert any("keiner der kleinsten Schnitte" in p for p in ev.validate(dataclasses.replace(a, mincuts=A.MinCuts(2, ((0, 1),), 0))))
    missing = dataclasses.replace(a, mincuts=A.MinCuts(2, ((0, 1, 2, 3, 4),), 0), sw=dataclasses.replace(a.sw, side=(0, 1, 2, 3, 4)))
    assert any("fehlt" in p or "keiner der kleinsten" in p or "nicht den gemeldeten" in p for p in ev.validate(missing))


def test_without_the_enumeration_the_checks_against_it_are_skipped():
    a = _textbook()
    assert ev.validate(dataclasses.replace(a, mincuts=None)) == []


def test_number_formats():
    assert ev._i(1234567) == "1.234.567" and ev._dec(12.5) == "12,5" and ev._dec(12.0) == "12" and ev._dec(1.08333, 3) == "1,083" and ev._dec(1234.5) == "1.234,5"
    assert ev._pct(0.4567) == "46" and ev._pct(0.4567, 1) == "45,7" and ev._pct(1.0) == "100" and ev._pct(0.0) == "0"
    assert ev._prob(1 / 120) == "0,0083" and ev._prob(0.5) == "0,50" and ev._prob(0.2273) == "0,23"
