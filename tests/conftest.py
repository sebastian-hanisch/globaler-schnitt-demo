"""Gemeinsame Fixtures: die Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Mutationstests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def unit(pairs):
    return tuple((min(u, v), max(u, v), 1) for u, v in pairs)


# Von Hand gerechnete Mini-Netze: Name -> (n, Leitungen, kleinster Schnitt, Zahl der kleinsten Schnitte, davon einzelne Standorte)
MINI = {
    "pfad4": (4, unit([(0, 1), (1, 2), (2, 3)]), 1, 3, 2),
    "kreis5": (5, unit([(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]), 2, 10, 5),
    "vollstaendig4": (4, unit([(a, b) for a in range(4) for b in range(a + 1, 4)]), 3, 4, 4),
    "stern4": (4, unit([(0, 1), (0, 2), (0, 3)]), 1, 3, 3),
    "zwei_werke": (8, unit([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7), (0, 4), (0, 5)]), 2, 1, 0),
    "dreieck_gewichtet": (3, ((0, 1, 3), (1, 2, 2), (0, 2, 1)), 3, 1, 1),                 # Grade 4, 5, 3: der kleinste Schnitt trennt den Standort 2 ab
}


class FixedRandom:
    """Liefert immer fast 1: alle Schlüssel -ln(1 - r) / w sind proportional zu 1 / w, bei gleichen Gewichten gilt die Reihenfolge der Leitungen, Fisher–Yates lässt die Reihenfolge unverändert."""

    def random(self):
        return 0.999999


@pytest.fixture
def mini():
    return MINI


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in gsc_experiments)."""
    import gsc_experiments as ex
    return getattr(ex, name)()
