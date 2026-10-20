"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Netze, Grenzen inklusive, Gewicht 0, unzusammenhängende Netze, Regler-Extreme."""

import random

import gsc_algorithm as A
import gsc_constants as C
import gsc_evaluation as ev

from conftest import FixedRandom, unit


def test_one_location_has_no_cut():
    assert A.stoer_wagner(1, ()).value == 0 and A.all_min_cuts(1, ()).count == 0 and A.min_weighted_degree(1, ()) == 0
    assert A.karger_batch(1, (), 5, random.Random(1)).values == (0, 0, 0, 0, 0)


def test_two_locations_with_one_link_have_one_cut_of_the_link_weight():
    for w in (1, 6):
        edges = ((0, 1, w),)
        mc = A.all_min_cuts(2, edges)
        assert A.stoer_wagner(2, edges).value == w and mc.sides == ((0,),) and A.karger_run(2, edges, FixedRandom()).value == w


def test_two_locations_without_a_link_are_cut_for_free():
    assert A.stoer_wagner(2, ()).value == 0 and A.all_min_cuts(2, ()).value == 0 and A.karger_run(2, (), FixedRandom()).value == 0


def test_a_zero_weight_link_is_no_connection():
    edges = ((0, 1, 5), (1, 2, 0), (2, 3, 5))
    assert A.stoer_wagner(4, edges).value == 0 and A.all_min_cuts(4, edges).sides == ((0, 1),)
    run = A.karger_run(4, edges, FixedRandom())
    assert run.value == 0 and run.side == (0, 1) and run.contracted == (0, 2) and run.steps == 2        # Schlüssel: 13,8 / 5 für beide schweren Leitungen, unendlich für die Leitung ohne Gewicht (zuletzt)


def test_a_network_with_two_components_has_minimum_cut_zero_and_karger_never_fails_to_report_it():
    edges = unit([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)])
    assert A.stoer_wagner(6, edges).value == 0 and A.all_min_cuts(6, edges).sides == ((0, 1, 2),)
    batch = A.karger_batch(6, edges, 40, random.Random(2))
    assert set(batch.values) == {0} and all(A.cut_value(edges, s) == 0 for s in batch.sides)


def test_three_components_still_give_a_valid_zero_cut_for_karger():
    edges = unit([(0, 1), (2, 3), (4, 5)])
    run = A.karger_run(6, edges, FixedRandom())
    assert run.value == 0 and 0 in run.side and 0 < len(run.side) < 6


def test_complete_network_has_only_trivial_minimum_cuts():
    n = 7
    edges = unit([(a, b) for a in range(n) for b in range(a + 1, n)])
    mc = A.all_min_cuts(n, edges)
    assert mc.value == n - 1 and mc.count == mc.trivial == n and A.stoer_wagner(n, edges).value == n - 1


def test_multiple_links_between_the_same_two_locations_add_up():
    edges = ((0, 1, 1), (0, 1, 1), (1, 2, 5))
    assert A.stoer_wagner(3, edges).value == 2 and A.cut_value(edges, (0,)) == 2 and A.all_min_cuts(3, edges).sides == ((0,),)


def test_a_dumbbell_has_one_nontrivial_minimum_cut_and_karger_finds_it():
    left = [(a, b) for a in range(4) for b in range(a + 1, 4)]
    right = [(a + 4, b + 4) for a, b in left]
    edges = unit(left + right + [(0, 4)])
    mc = A.all_min_cuts(8, edges)
    assert mc.value == 1 and mc.sides == ((0, 1, 2, 3),) and mc.trivial == 0
    assert sum(1 for v in A.karger_batch(8, edges, 300, random.Random(4)).values if v == 1) > 100


def test_the_minimum_and_maximum_network_sizes_validate_for_every_kind_and_weight():
    for kind in C.KINDS:
        for weights in C.WEIGHTS:
            for n in (C.N_MIN, C.N_MAX):
                a = ev.analyse(ev.Settings(kind, n, 4.0, 2, weights, 3, C.RUNS[0]))
                assert ev.validate(a) == [] and a.n >= 4, (kind, weights, n)
                assert (a.mincuts is None) == (a.n > C.BRUTE_N)


def test_the_regler_extremes_of_the_verbund_and_the_run_counts_validate():
    for links in (C.LINKS_MIN, C.LINKS_MAX):
        for deg in (C.DEG_MIN, C.DEG_MAX):
            a = ev.analyse(ev.Settings("verbund", 16, deg, links, "random", 5, C.RUNS[-1]))
            assert ev.validate(a) == [] and a.runs == C.RUNS[-1]
    assert ev.validate(ev.analyse(ev.Settings("random", 16, 5.0, 2, "unit", 5, C.RUNS[0]))) == []


def test_the_largest_aufzaehlung_size_is_exact():
    a = ev.analyse(ev.Settings("random", C.BRUTE_N, 4.0, 2, "random", 9, 100))
    assert a.mincuts is not None and a.mincuts.value == a.value and ev.validate(a) == []
    b = ev.analyse(ev.Settings("random", C.BRUTE_N + 1, 4.0, 2, "random", 9, 100))
    assert b.mincuts is None and ev.validate(b) == []


def test_the_smallest_network_size_of_the_regler_with_the_grid_rounding():
    assert ev.analyse(ev.Settings("grid", C.N_MIN, 4.0, 2, "unit", 1, 100)).n == 4      # 2 x 2: Wurzel aus 6 gerundet ist 2
