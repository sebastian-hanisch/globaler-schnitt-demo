"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen; Permalink-Grenzen."""

import gsc_constants as C
import gsc_evaluation as ev
import gsc_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        assert preset["kind"] in C.KINDS and preset["weights"] in C.WEIGHTS and preset["runs"] in C.RUNS, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.DEG_MIN <= preset["deg"] <= C.DEG_MAX and C.LINKS_MIN <= preset["links"] <= C.LINKS_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_the_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_every_choice_field_is_listed():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert {spec.url_param for spec in P.SETTING_SPECS.values()} == {"kind", "n", "deg", "links", "weights", "seed", "runs"}
    assert set(P.CHOICES) == {"kind_select", "weights_select", "runs_select"} and P.CHOICES["runs_select"] == C.RUNS


def test_every_kind_has_a_name_a_help_text_and_a_regler_note_and_every_weight_a_name():
    assert set(C.KIND_NAMES) == set(C.KIND_HELP) == set(C.KIND_REGLER) == set(C.KINDS) and set(C.WEIGHT_NAMES) == set(C.WEIGHTS)


def test_the_experiment_grid_uses_only_known_kinds_and_sizes_inside_the_regler_range():
    assert all(kind in C.KINDS and kind != "textbook" for kind, _deg in C.EX_KINDS)
    assert C.N_MIN <= C.EX_N <= C.BRUTE_N and all(C.N_MIN <= n <= C.N_MAX for n in C.EX_COST_NS) and C.EX_COST_SEEDS <= len(C.SWEEP_SEEDS)
    assert 0 < C.CONFIDENCE < 1 and C.DEFAULT_RUNS in C.RUNS
