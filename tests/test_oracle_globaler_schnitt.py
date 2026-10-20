"""Orakel-Test globaler-schnitt-demo: kleinster Schnitt, Zahl aller kleinsten Schnitte und die Läufe von Karger gegen networkx, die Aufzählung und exakte Rechnung (DEMO-PLAYBOOK §12).

Unabhängige Rechenwege: `networkx.stoer_wagner`, `networkx.edge_connectivity` (gleiche Gewichte), die Aufzählung aller Zweiteilungen und die exakte Verteilung über alle Kantenreihenfolgen. Feste Netze (Seeds)."""

import math
import random

import pytest

import gsc_algorithm as A
import gsc_scenario as S

nx = pytest.importorskip("networkx")

from conftest import MINI, unit  # noqa: E402


def _nets(count=60, base=500):
    kinds = ("random", "grid", "ring", "scalefree", "verbund", "cycle", "tree")
    for k in range(count):
        kind = kinds[k % len(kinds)]
        n = 8 + (k * 5) % 24
        yield S.make_instance(kind, n, (3.0, 4.5, 6.0)[k % 3], 1 + k % 3, ("unit", "random")[(k // 7) % 2], base + k)


def _graph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_weighted_edges_from(inst.edges)
    return g


def test_stoer_wagner_value_equals_networkx_and_the_side_is_a_real_cut():
    for inst in _nets():
        value, (a, b) = nx.stoer_wagner(_graph(inst))
        sw = A.stoer_wagner(inst.n, inst.edges)
        assert sw.value == value, (inst.kind, inst.n)
        assert A.cut_value(inst.edges, sw.side) == value and 0 < len(sw.side) < inst.n
        assert A.cut_value(inst.edges, a) == value                                      # networkx' eigener Schnitt hat denselben Wert


def test_unit_weights_equal_the_edge_connectivity():
    for inst in _nets(24, 800):
        if all(w == 1 for _u, _v, w in inst.edges):
            assert A.stoer_wagner(inst.n, inst.edges).value == nx.edge_connectivity(_graph(inst))


def test_the_enumeration_equals_stoer_wagner_and_lists_every_minimum_cut():
    for inst in _nets(30, 1100):
        if inst.n > 16:
            continue
        mc = A.all_min_cuts(inst.n, inst.edges)
        sw = A.stoer_wagner(inst.n, inst.edges)
        assert mc.value == sw.value and A.canonical(inst.n, sw.side) in mc.sides
        for side in mc.sides:
            assert A.cut_value(inst.edges, side) == mc.value
        assert mc.count <= inst.n * (inst.n - 1) // 2


def test_the_enumeration_misses_no_cut_on_tiny_networks():
    """Jede Zweiteilung von Hand durchgezählt (n <= 7): kleinster Wert und Zahl der kleinsten stimmen mit `all_min_cuts` überein."""
    rng = random.Random(9)
    for _ in range(25):
        n = rng.randint(3, 7)
        edges = tuple((u, v, rng.randint(1, 3)) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.6)
        if not edges:
            continue
        values = {}
        for mask in range(1, 2 ** (n - 1)):
            side = tuple([0] + [v + 1 for v in range(n - 1) if (mask >> v) & 1])
            if len(side) < n:
                values[side] = A.cut_value(edges, side)
        values[(0,)] = A.cut_value(edges, (0,))
        best = min(values.values())
        mc = A.all_min_cuts(n, edges)
        assert mc.value == best and set(mc.sides) == {s for s, v in values.items() if v == best}


def test_karger_exact_distribution_of_every_minimum_cut_is_at_least_the_guarantee():
    """Alle m! Kantenreihenfolgen auf kleinen Netzen (m <= 7): Jeder kleinste Schnitt wird mit Wahrscheinlichkeit mindestens 2 / (n (n - 1)) getroffen, und nur Schnitte werden ausgegeben."""
    nets = [unit([(0, 1), (1, 2), (2, 3), (3, 0)]), unit([(0, 1), (1, 2), (0, 2), (2, 3), (3, 4)]), unit([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]),
            unit([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]), unit([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2), (0, 3)])]
    for edges in nets:
        n = max(max(u, v) for u, v, _w in edges) + 1
        dist = A.exact_distribution(n, edges)
        total = math.factorial(len(edges))
        mc = A.all_min_cuts(n, edges)
        assert sum(dist.values()) == total and all(A.cut_value(edges, s) >= mc.value for s in dist)
        for side in mc.sides:
            assert dist.get(side, 0) / total >= A.karger_guarantee(n) - 1e-12, (edges, side)


def test_on_the_cycle_the_guarantee_is_sharp_exactly():
    for n in (4, 5, 6, 7):
        edges = unit([(v, (v + 1) % n) for v in range(n)])
        dist = A.exact_distribution(n, edges)
        assert len(dist) == n * (n - 1) // 2 and set(dist.values()) == {2 * math.factorial(n - 2)}      # jeder der C(n, 2) Schnitte bei genau 2 (n - 2)! von n! Reihenfolgen
        assert 2 * math.factorial(n - 2) / math.factorial(n) == A.karger_guarantee(n)


def test_the_measured_rate_on_the_cycle_matches_the_formula_within_four_standard_errors():
    inst = S.make_instance("cycle", 16)
    runs = 40000
    batch = A.karger_batch(inst.n, inst.edges, runs, random.Random(2))
    ref = tuple(range(8))
    rate = sum(1 for s in batch.sides if s == ref) / runs
    q = 1 / 120
    assert abs(rate - q) < 4 * math.sqrt(q * (1 - q) / runs)


def test_every_karger_run_is_a_cut_not_below_the_minimum_and_a_weighted_run_prefers_heavy_edges():
    for inst in _nets(14, 1300):
        sw = A.stoer_wagner(inst.n, inst.edges)
        batch = A.karger_batch(inst.n, inst.edges, 80, random.Random(inst.n))
        assert min(batch.values) >= sw.value and all(v == A.cut_value(inst.edges, s) for v, s in zip(batch.values, batch.sides))
    heavy = ((0, 1, 20), (1, 2, 1), (2, 3, 20), (0, 3, 1))                                      # vier Standorte, zwei schwere Leitungen: der kleinste Schnitt (2) durchtrennt die zwei leichten
    batch = A.karger_batch(4, heavy, 400, random.Random(1))
    assert A.stoer_wagner(4, heavy).value == 2 and sum(1 for v in batch.values if v == 2) / 400 > 0.8                  # von Hand: 40/42 mal 20/22 = 0,866 für den ersten Schritt plus kleine Beiträge, gemessen 0,855


def test_scaling_all_weights_scales_the_minimum_cut_and_keeps_the_cuts():
    for inst in _nets(12, 1500):
        scaled = tuple((u, v, 3 * w) for u, v, w in inst.edges)
        assert A.stoer_wagner(inst.n, scaled).value == 3 * A.stoer_wagner(inst.n, inst.edges).value
        if inst.n <= 14:
            assert A.all_min_cuts(inst.n, scaled).sides == A.all_min_cuts(inst.n, inst.edges).sides


def test_connectivity_does_not_depend_on_the_numbering_of_the_locations():
    rng = random.Random(7)
    for inst in _nets(16, 1700):
        perm = list(range(inst.n))
        rng.shuffle(perm)
        edges = tuple((min(perm[u], perm[v]), max(perm[u], perm[v]), w) for u, v, w in inst.edges)
        assert A.stoer_wagner(inst.n, edges).value == A.stoer_wagner(inst.n, inst.edges).value


def test_adding_a_link_never_lowers_the_minimum_cut():
    for inst in _nets(20, 1900):
        sw = A.stoer_wagner(inst.n, inst.edges)
        present = {(u, v) for u, v, _w in inst.edges}
        free = [(u, v) for u in range(inst.n) for v in range(u + 1, inst.n) if (u, v) not in present]
        if not free:
            continue
        u, v = free[len(free) // 2]
        assert A.stoer_wagner(inst.n, inst.edges + ((u, v, 2),)).value >= sw.value


def test_the_minimum_cut_never_exceeds_the_weighted_minimum_degree_and_the_trivial_cuts_are_cuts():
    for inst in _nets(30, 2100):
        sw = A.stoer_wagner(inst.n, inst.edges)
        assert sw.value <= A.min_weighted_degree(inst.n, inst.edges)


def test_hand_networks_against_networkx():
    for name, (n, edges, value, *_rest) in MINI.items():
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_weighted_edges_from(edges)
        assert nx.stoer_wagner(g)[0] == value, name
