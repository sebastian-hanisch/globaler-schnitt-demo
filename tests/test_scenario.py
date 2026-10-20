"""Netz-Erzeuger: einfach, zusammenhängend, deterministisch, dokumentierte Größen, Gewichte."""

import math

import pytest

import gsc_algorithm as A
import gsc_constants as C
import gsc_scenario as S

from conftest import FixedRandom


def _simple_connected(inst):
    seen_pairs = set()
    for u, v, w in inst.edges:
        assert 0 <= u < v < inst.n and w >= 1 and (u, v) not in seen_pairs
        seen_pairs.add((u, v))
    adj = S._adj_from_pairs(inst.n, inst.pairs)
    return len(S._components(adj)) == 1


def test_below_stays_in_range_and_shuffle_with_a_fixed_source_is_the_identity():
    assert S._below(FixedRandom(), 5) == 4 and S._below(FixedRandom(), 1) == 0
    assert S._shuffle(range(6), FixedRandom()) == [0, 1, 2, 3, 4, 5]
    assert sorted(S._shuffle(range(10), S.make_rng(3, 1))) == list(range(10))


def test_cycle_and_tree_by_hand():
    assert S.cycle_pairs(4) == [(0, 1), (0, 3), (1, 2), (2, 3)]
    assert S.tree_pairs(5, FixedRandom()) == [(0, 1), (1, 2), (2, 3), (3, 4)]                    # feste Quelle: jeder hängt sich an den Vorgänger, ein Pfad
    t = S.tree_pairs(12, S.make_rng(2, 2))
    assert len(t) == 11 and len(S._components(S._adj_from_pairs(12, t))) == 1


def test_weights_unit_and_random_stay_in_range_and_are_deterministic():
    pairs = [(0, 1), (1, 2), (2, 3), (0, 3)]
    assert S.assign_weights(pairs, "unit", FixedRandom()) == ((0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 1))
    assert S.assign_weights(pairs, "random", FixedRandom()) == ((0, 1, 5), (1, 2, 5), (2, 3, 5), (0, 3, 5))      # feste Quelle: immer das größte Gewicht
    w1 = S.assign_weights(pairs * 25, "random", S.make_rng(1, 1))
    assert w1 == S.assign_weights(pairs * 25, "random", S.make_rng(1, 1)) and {w for _u, _v, w in w1} == set(range(1, C.WEIGHT_MAX + 1))
    with pytest.raises(ValueError):
        S.assign_weights(pairs, "dreifach", FixedRandom())


def test_grid_pairs_and_the_grid_network():
    assert S.grid_pairs(2) == [(0, 1), (0, 2), (1, 3), (2, 3)]
    inst = S.make_instance("grid", 30, seed=1)
    assert inst.n == 25 and inst.m == 40 and sorted(inst.weighted_degrees()) == [2] * 4 + [3] * 12 + [4] * 9


def test_scalefree_has_the_documented_number_of_links():
    for n in (6, 20, 50):
        inst = S.make_instance("scalefree", n, seed=4)
        assert inst.n == n and inst.m == 3 + 2 * (n - 3)


def test_ring_without_rewiring_is_four_regular():
    pairs = S.ring_pairs(12, FixedRandom(), rewire=0.0)
    assert len(pairs) == 24 and set(S.make_instance("ring", 12, seed=1).weighted_degrees()) <= {3, 4, 5, 6}


def test_verbund_has_the_given_number_of_links_between_every_two_regions():
    for links in (1, 3, 5):
        inst = S.make_instance("verbund", 36, 6.0, links, "unit", 2)
        sizes = S.region_sizes(36)
        bounds = [0, sizes[0], sizes[0] + sizes[1], 36]
        region = lambda v: next(i for i in range(3) if bounds[i] <= v < bounds[i + 1])   # noqa: E731
        between = {}
        for u, v in inst.pairs:
            if region(u) != region(v):
                key = (region(u), region(v))
                between[key] = between.get(key, 0) + 1
        assert between == {(0, 1): links, (0, 2): links, (1, 2): links}


def test_region_sizes_split_the_network_evenly():
    assert S.region_sizes(10) == [4, 3, 3] and S.region_sizes(9) == [3, 3, 3] and sum(S.region_sizes(47)) == 47


def test_textbook_network_by_hand():
    inst = S.make_instance("textbook", 99, weights="random", seed=5)
    assert inst.n == 8 and inst.m == 14 and inst.total_weight == 14 and inst.labels == S.TEXTBOOK_LABELS and inst.name(0) == "A" and inst.name(7) == "H"
    assert A.stoer_wagner(inst.n, inst.edges).value == 2 and inst.weighted_degrees() == [5, 3, 3, 3, 4, 4, 3, 3]


@pytest.mark.parametrize("kind", list(C.KINDS))
@pytest.mark.parametrize("weights", list(C.WEIGHTS))
def test_every_kind_gives_a_simple_connected_network_that_is_deterministic(kind, weights):
    for seed in (1, 2, 3):
        inst = S.make_instance(kind, 24, 4.0, 2, weights, seed)
        assert _simple_connected(inst) and inst.xy.shape == (inst.n, 2) and abs(inst.xy).max() < 10
        again = S.make_instance(kind, 24, 4.0, 2, weights, seed)
        assert again.edges == inst.edges and (again.xy == inst.xy).all()
        if weights == "unit" or kind == "textbook":
            assert all(w == 1 for _u, _v, w in inst.edges)
    if kind not in ("textbook", "grid", "cycle"):
        assert S.make_instance(kind, 24, 4.0, 2, weights, 1).edges != S.make_instance(kind, 24, 4.0, 2, weights, 2).edges


def test_the_network_size_follows_the_setting_except_for_the_grid_and_the_textbook():
    for kind in ("cycle", "tree", "random", "ring", "scalefree", "verbund"):
        assert S.make_instance(kind, 37, 4.0, 2, "unit", 1).n == 37
    assert S.make_instance("grid", 37).n == 36 and S.make_instance("textbook", 37).n == 8


def test_cycle_has_n_links_and_tree_has_n_minus_one():
    assert S.make_instance("cycle", 20).m == 20 and S.make_instance("tree", 20, seed=3).m == 19


def test_random_network_has_the_requested_mean_degree():
    inst = S.make_instance("random", 40, 6.0, 2, "unit", 1)
    assert inst.m == 120 and sum(inst.weighted_degrees()) / inst.n == 6.0


def test_unknown_kind_and_tiny_networks_are_rejected():
    with pytest.raises(ValueError):
        S.make_instance("sternfoermig", 10)
    with pytest.raises(ValueError):
        S.make_instance("random", 3)


def test_spring_layout_is_finite_scaled_and_deterministic():
    pairs = S.random_connected(15, 25, S.make_rng(1, 1))
    pos1 = S.spring_layout(15, pairs, S.make_rng(9, 9))
    pos2 = S.spring_layout(15, pairs, S.make_rng(9, 9))
    assert pos1.shape == (15, 2) and (pos1 == pos2).all() and math.isfinite(float(pos1.sum())) and abs(pos1).max() <= 1.0 + 1e-9


def test_random_connected_with_a_fixed_source_is_the_path_and_has_the_documented_size():
    assert S.random_connected(5, 4, FixedRandom()) == [(0, 1), (1, 2), (2, 3), (3, 4)]
    assert len(S.random_connected(10, 3, S.make_rng(1, 1))) == 9 and len(S.random_connected(10, 20, S.make_rng(1, 2))) == 20 and len(S.random_connected(5, 999, S.make_rng(1, 3))) == 10


def test_ensure_connected_joins_every_component_to_location_zero():
    assert S._ensure_connected(6, [(1, 2), (3, 4)]) == [(0, 1), (0, 3), (0, 5), (1, 2), (3, 4)]


def test_instance_properties_and_names():
    inst = S.make_instance("random", 12, 4.0, 2, "random", 5)
    assert inst.n == 12 and inst.m == len(inst.edges) == len(inst.pairs) and inst.name(0) == "1" and inst.name(11) == "12" and inst.total_weight == sum(w for _u, _v, w in inst.edges)
    assert sum(inst.weighted_degrees()) == 2 * inst.total_weight
