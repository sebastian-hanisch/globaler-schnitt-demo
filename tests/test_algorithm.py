"""Kern: jede Einheit an von Hand gerechneten Mini-Netzen (DEMO-PLAYBOOK §1b)."""

import math
import random

import pytest

import gsc_algorithm as A

from conftest import MINI, FixedRandom, unit


def test_cut_value_cut_edges_and_degrees_by_hand():
    n, edges, *_ = MINI["dreieck_gewichtet"]
    assert A.cut_value(edges, (2,)) == 3 and A.cut_value(edges, (0,)) == 4 and A.cut_value(edges, (1,)) == 5 and A.cut_value(edges, (0, 1)) == 3
    assert A.cut_edges(edges, (2,)) == ((1, 2), (0, 2)) and A.cut_edges(edges, (0, 1, 2)) == ()
    assert A.min_weighted_degree(n, edges) == 3 and A.min_weighted_degree(0, ()) == 0


def test_canonical_side_contains_location_zero_and_trivial_means_one_location():
    assert A.canonical(5, (3, 4)) == (0, 1, 2) and A.canonical(5, (0, 2)) == (0, 2) and A.canonical(4, {2}) == (0, 1, 3)
    assert A.is_trivial(5, (3,)) and A.is_trivial(5, (0, 1, 2, 3)) and not A.is_trivial(5, (1, 2)) and not A.is_trivial(4, (0, 1))


def test_stoer_wagner_on_the_path_phase_by_phase():
    n, edges, *_ = MINI["pfad4"]
    sw = A.stoer_wagner(n, edges)
    assert sw.value == 1 and sw.side == (3,) and sw.best_phase == 0 and len(sw.phases) == 3
    p1, p2, p3 = sw.phases
    assert (p1.order, p1.bindings, p1.last, p1.before, p1.cut, p1.last_group, p1.steps) == ((0, 1, 2, 3), (0, 1, 1, 1), 3, 2, 1, (3,), 6)
    assert (p2.order, p2.bindings, p2.last, p2.before, p2.cut, p2.last_group, p2.steps) == ((0, 1, 2), (0, 1, 1), 2, 1, 1, (2, 3), 3)
    assert (p3.order, p3.bindings, p3.last, p3.before, p3.cut, p3.last_group, p3.steps) == ((0, 1), (0, 1), 1, 0, 1, (1, 2, 3), 1)
    assert sw.steps == 10 and p2.groups == ((0, (0,)), (1, (1,)), (2, (2, 3)))


def test_stoer_wagner_on_the_weighted_triangle_by_hand():
    n, edges, *_ = MINI["dreieck_gewichtet"]
    sw = A.stoer_wagner(n, edges)
    p1, p2 = sw.phases
    assert (p1.order, p1.bindings, p1.cut, p1.last_group, p1.before) == ((0, 1, 2), (0, 3, 3), 3, (2,), 1)           # 0, dann 1 (Bindung 3), dann 2 (Bindung 1 + 2 = 3)
    assert (p2.order, p2.bindings, p2.cut, p2.last_group) == ((0, 1), (0, 4), 4, (1, 2))                              # nach dem Verschmelzen von 2 in 1 ist die Leitung 0-1 stark 3 + 1
    assert sw.value == 3 and sw.side == (2,) and sw.best_phase == 0


def test_stoer_wagner_picks_the_first_phase_with_the_smallest_cut_and_the_smallest_vertex_on_ties():
    n, edges, *_ = MINI["kreis5"]
    sw = A.stoer_wagner(n, edges)
    assert sw.value == 2 and [p.cut for p in sw.phases] == [2, 2, 2, 2] and sw.best_phase == 0
    assert sw.phases[0].order == (0, 1, 2, 3, 4) and sw.phases[0].bindings == (0, 1, 1, 1, 2)       # Gleichstand der Bindung: der kleinste Vertreter zuerst; der Standort 4 ist an 0 und an 3 gebunden: 2


def test_stoer_wagner_values_of_every_mini_network_and_the_cut_of_every_phase_is_a_real_cut():
    for name, (n, edges, value, count, trivial) in MINI.items():
        sw = A.stoer_wagner(n, edges)
        assert sw.value == value, name
        assert A.cut_value(edges, sw.side) == value, name
        for phase in sw.phases:
            assert A.cut_value(edges, phase.last_group) == phase.cut, name              # der Schnitt der Phase ist auch im ursprünglichen Netz ein Schnitt dieses Werts


def test_stoer_wagner_matrix_access_formula():
    for n in (3, 6, 8, 12):
        edges = unit([(v, v + 1) for v in range(n - 1)])
        assert A.stoer_wagner(n, edges).steps == (n + 1) * n * (n - 1) // 6


def test_stoer_wagner_of_one_location_and_two_locations():
    assert A.stoer_wagner(1, ()) == A.StoerWagner(0, (), -1, (), 0)
    sw = A.stoer_wagner(2, ((0, 1, 7),))
    assert sw.value == 7 and sw.side == (1,) and len(sw.phases) == 1 and sw.steps == 1


def test_stoer_wagner_adds_parallel_edges():
    sw = A.stoer_wagner(2, ((0, 1, 2), (0, 1, 3)))
    assert sw.value == 5


def test_edge_order_with_a_fixed_source_follows_the_weights():
    assert A.edge_order(((0, 1, 1), (1, 2, 1), (2, 3, 1)), FixedRandom()) == [0, 1, 2]                    # gleiche Gewichte: Reihenfolge der Leitungen
    assert A.edge_order(((0, 1, 1), (1, 2, 4), (2, 3, 2)), FixedRandom()) == [1, 2, 0]                    # größeres Gewicht zuerst
    assert A.edge_order(((0, 1, 0), (1, 2, 1)), FixedRandom()) == [1, 0]                                  # Gewicht 0 kommt zuletzt


def test_karger_run_on_the_path_by_hand():
    n, edges, *_ = MINI["pfad4"]
    run = A.karger_run(n, edges, FixedRandom())
    assert run.value == 1 and run.side == (0, 1, 2) and run.contracted == (0, 1) and run.steps == 2


def test_karger_run_on_the_weighted_triangle_contracts_the_heaviest_edge_first():
    n, edges, *_ = MINI["dreieck_gewichtet"]
    run = A.karger_run(n, edges, FixedRandom())
    assert run.value == 3 and run.side == (0, 1) and run.contracted == (0,) and run.steps == 1


def test_karger_run_of_a_complete_graph_stops_at_two_groups():
    n, edges, *_ = MINI["vollstaendig4"]
    run = A.karger_run(n, edges, FixedRandom())
    assert run.contracted == (0, 1) and run.side == (0, 1, 2) and run.value == 3 and run.steps == 2         # (0,1) und (0,2) ziehen zusammen, dann sind zwei Gruppen übrig: Schluss


def test_karger_run_skips_edges_inside_a_group_and_counts_them():
    edges = unit([(0, 1), (0, 1), (1, 2), (2, 3)])                                                         # eine Doppelleitung: die zweite wird übersprungen, aber gezählt
    run = A.karger_run(4, edges, FixedRandom())
    assert run.contracted == (0, 2) and run.steps == 3 and run.value == 1 and run.side == (0, 1, 2)


def test_karger_run_of_a_disconnected_network_gives_value_zero():
    run = A.karger_run(4, unit([(0, 1), (2, 3)]), FixedRandom())
    assert run.value == 0 and run.side == (0, 1)
    assert A.karger_run(1, (), FixedRandom()) == A.KargerRun(0, (), (), 0)
    two = A.karger_run(2, ((0, 1, 5),), FixedRandom())
    assert two.value == 5 and two.contracted == () and two.steps == 0


def test_karger_batch_counts_runs_and_steps_and_is_deterministic():
    n, edges, *_ = MINI["zwei_werke"]
    b1 = A.karger_batch(n, edges, 30, random.Random(5))
    b2 = A.karger_batch(n, edges, 30, random.Random(5))
    rng = random.Random(5)
    assert b1 == b2 and b1.runs == 30 and len(b1.sides) == len(b1.contracted) == 30 and b1.steps == sum(A.karger_run(n, edges, rng).steps for _ in range(30))
    assert b1.steps >= sum(len(c) for c in b1.contracted)
    assert min(b1.values) >= 2 and all(len(c) == n - 2 for c in b1.contracted)


def test_guarantee_and_repetitions_by_hand():
    assert A.karger_guarantee(16) == 1 / 120 and A.karger_guarantee(5) == 0.1 and A.karger_guarantee(2) == 1.0 and A.karger_guarantee(1) == 1.0
    assert A.repetitions_for(0.5, 0.99) == 7 and A.repetitions_for(1.0, 0.99) == 1 and A.repetitions_for(0.0, 0.99) is None and A.repetitions_for(0.9999, 0.99) == 1
    assert A.repetitions_for(A.karger_guarantee(16), 0.99) == 551 and A.repetitions_for(0.1, 0.99) == math.ceil(math.log(0.01) / math.log(0.9))


def test_exact_distribution_on_the_path_and_the_cycle():
    assert A.exact_distribution(4, MINI["pfad4"][1]) == {(0,): 2, (0, 1): 2, (0, 1, 2): 2}                  # die nicht zusammengezogene Leitung ist die letzte der Reihenfolge: je zwei von sechs
    dist = A.exact_distribution(5, MINI["kreis5"][1])
    assert len(dist) == 10 and set(dist.values()) == {12}                                                    # 120 Reihenfolgen, zehn Schnitte durch zwei Leitungen, jeder 2 · 3! = 12


def test_all_min_cuts_of_every_mini_network():
    for name, (n, edges, value, count, trivial) in MINI.items():
        mc = A.all_min_cuts(n, edges)
        assert (mc.value, mc.count, mc.trivial) == (value, count, trivial), name
        assert all(0 in s and A.cut_value(edges, s) == value for s in mc.sides), name


def test_all_min_cuts_by_hand_on_the_path_the_works_and_a_disconnected_network():
    assert A.all_min_cuts(4, MINI["pfad4"][1]).sides == ((0,), (0, 1), (0, 1, 2))
    assert A.all_min_cuts(8, MINI["zwei_werke"][1]).sides == ((0, 1, 2, 3),)
    mc = A.all_min_cuts(4, unit([(0, 1), (2, 3)]))
    assert mc.value == 0 and mc.sides == ((0, 1),)


def test_all_min_cuts_of_one_two_and_weighted_two_locations():
    assert A.all_min_cuts(1, ()) == A.MinCuts(0, (), 0)
    mc = A.all_min_cuts(2, ((0, 1, 4),))
    assert (mc.value, mc.sides, mc.trivial) == (4, ((0,),), 1)


def test_min_cuts_are_at_most_n_choose_2():
    for name, (n, edges, value, count, trivial) in MINI.items():
        assert count <= n * (n - 1) // 2, name


def test_stoer_wagner_agrees_with_the_enumeration_on_random_small_networks():
    rng = random.Random(3)
    for _ in range(40):
        n = rng.randint(3, 9)
        edges = tuple((u, v, rng.randint(1, 4)) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.5)
        if not edges:
            continue
        sw, mc = A.stoer_wagner(n, edges), A.all_min_cuts(n, edges)
        assert sw.value == mc.value and A.canonical(n, sw.side) in mc.sides


@pytest.mark.parametrize("name", list(MINI))
def test_a_karger_run_never_beats_the_minimum_and_reports_a_real_cut(name):
    n, edges, value, *_ = MINI[name]
    batch = A.karger_batch(n, edges, 60, random.Random(11))
    assert min(batch.values) >= value and all(v == A.cut_value(edges, s) for v, s in zip(batch.values, batch.sides))
