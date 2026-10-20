"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einem festen Netz vor.

Ein Preset, das seine Beschreibung nicht einlöst (z. B. „Der Kreis: die Schranke ist scharf“ mit weniger als C(n, 2) kleinsten Schnitten), fällt hier auf."""

import dataclasses

import pytest

import gsc_algorithm as A
import gsc_constants as C
import gsc_evaluation as ev
import gsc_visualization as V


def _a(name, **over):
    return ev.analyse(ev.Settings(**{**C.PRESETS[name], **over}))


def test_lehrbeispiel_has_one_real_cut_of_two_and_a_trivial_cut_of_three():
    a = _a("Lehrbeispiel (zwei Werke)")
    assert (a.value, a.degree_cut) == (2, 3) and a.side == (0, 1, 2, 3) and not a.trivial and a.mincuts.count == 1 and ev.verdict_question(a)[0] == "info"


def test_the_cycle_has_every_cut_through_two_links_as_a_minimum_and_karger_always_hits():
    a = _a("Der Kreis: die Schranke ist scharf")
    assert a.n == 16 and a.value == 2 and a.mincuts.count == 120 == a.n * (a.n - 1) // 2 and a.success_rate == 1.0 and a.runs == 3000
    assert 0.003 < a.fixed_rate < 0.015                                                                 # ein bestimmter Schnitt: um 1 / 120


def test_the_tree_has_one_minimum_cut_per_link():
    a = _a("Der Baum: jede Leitung ein kleinster Schnitt")
    assert a.value == 1 and a.mincuts.count == a.n - 1 and a.success_rate == 1.0


def test_the_minimum_cut_is_a_single_location_in_its_preset():
    a = _a("Der kleinste Schnitt ist ein Standort")
    assert a.trivial and a.value == a.degree_cut and a.mincuts.count == a.mincuts.trivial == 1


def test_the_bound_is_pessimistic_in_its_preset():
    a = _a("Die Schranke ist zu pessimistisch")
    assert a.success_rate > 30 * a.guarantee and a.mincuts.count == a.mincuts.trivial == 5


def test_the_verbund_has_a_real_cut_below_the_smallest_degree_in_its_preset():
    a = _a("Das Verbundnetz hat einen echten Schnitt")
    assert not a.trivial and a.value < a.degree_cut and len(a.side) in (5, 11)


def test_weights_move_the_cut_in_their_preset():
    a = _a("Gewichte verschieben den Schnitt")
    assert a.settings.weights == "random" and a.value < a.degree_cut and not a.trivial and a.mincuts.count == 1
    unit = _a("Gewichte verschieben den Schnitt", weights="unit")
    assert unit.value == 2 and unit.mincuts.count == 120


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_passes_the_validation_and_renders_every_figure(name):
    a = _a(name)
    assert ev.validate(a) == []
    V.build_cut_map(a.inst, a.side)
    V.build_phase_map(a.inst, a.sw.phases[a.sw.best_phase])
    V.build_phase_cuts(a.sw)
    run = A.KargerRun(a.batch.values[0], a.batch.sides[0], a.batch.contracted[0], 0)
    for k in (0, len(run.contracted)):
        V.build_contraction_map(a.inst, run, k)
    V.build_karger_histogram(a.batch, a.value)
    V.build_success_curve(a.success_rate, a.guarantee, a.reps_bound)
    V.build_mincut_map(a.inst, a.mincuts)


def test_the_enumeration_tab_has_a_branch_for_large_networks():
    a = ev.analyse(ev.Settings("random", C.BRUTE_N + 4, 4.0, 2, "unit", 2, 100))
    assert a.mincuts is None and ev.validate(a) == []


def test_the_settings_are_immutable_and_hashable_for_the_cache():
    s = ev.Settings()
    assert hash(s) == hash(ev.Settings()) and dataclasses.replace(s, runs=100) != s


def test_contraction_state_after_zero_some_and_all_contractions():
    a = _a("Lehrbeispiel (zwei Werke)")
    contracted = a.batch.contracted[0]
    _p, groups0 = V.contraction_state(a.n, a.inst.edges, contracted, 0)
    _p, groups_all = V.contraction_state(a.n, a.inst.edges, contracted, len(contracted))
    _p, groups_half = V.contraction_state(a.n, a.inst.edges, contracted, 3)
    assert len(groups0) == 8 and len(groups_half) == 5 and len(groups_all) == 2
    assert sorted(v for g in groups_all for v in g) == list(range(8))
