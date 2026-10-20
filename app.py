"""Globaler Min-Cut: Stoer–Wagner und Karger - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Reihe „Schnitte und Zusammenhang“: Was ist der kleinste Schnitt des ganzen Netzes, und wie oft muss man würfeln? Stoer–Wagner (Phasen, Verschmelzen) gegen Karger (zufällige Kontraktion,
Erfolgswahrscheinlichkeit, Wiederholungen), dazu die Zahl und die Gestalt aller kleinsten Schnitte.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import gsc_algorithm as A
import gsc_constants as C
import gsc_evaluation as ev
import gsc_experiments as ex
from gsc_layout import dunkles_design, kopf_css
from gsc_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from gsc_visualization import (
    build_contraction_map,
    build_cost,
    build_cut_map,
    build_exact,
    build_karger_histogram,
    build_karger_rates,
    build_mincut_map,
    build_phase_cuts,
    build_phase_map,
    build_reps,
    build_success_curve,
    build_trivial,
)

st.set_page_config(page_title="Globaler Min-Cut: Stoer–Wagner und Karger – Sebastian Hanisch", layout="wide")

_i, _dec = ev._i, ev._dec


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


@st.cache_data(show_spinner=False, max_entries=8)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _exactness():
    return ex.exactness_rows()


@st.cache_data(show_spinner=False)
def _trivial():
    return ex.trivial_rows()


@st.cache_data(show_spinner=False)
def _karger():
    return ex.karger_rows(), ex.cycle_rows()


@st.cache_data(show_spinner=False)
def _repetitions():
    return ex.repetition_rows()


@st.cache_data(show_spinner=False)
def _cost():
    return ex.cost_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gsc_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("✂️ Globaler Min-Cut: Stoer–Wagner und Karger")
st.markdown(
    """
**Was ist der kleinste Schnitt des ganzen Netzes, und wie oft muss man würfeln?** Ein **Schnitt** teilt die Standorte in zwei Seiten; sein Wert ist die Summe der Gewichte der Leitungen dazwischen. Der **kleinste Schnitt** sagt, wie viel man
mindestens kappen muss, damit das Netz zerfällt. Das **Verfahren von Stoer und Wagner** findet ihn **exakt** in n − 1 Phasen (stärkste Bindung zuerst, dann die letzten beiden verschmelzen). Das **Verfahren von Karger** würfelt:
Es zieht zufällige Leitungen zusammen, bis zwei Gruppen übrig sind. Ein einzelner Lauf trifft einen bestimmten kleinsten Schnitt nur mit Wahrscheinlichkeit **mindestens 2 / (n (n − 1))**, darum wiederholt man; wie pessimistisch diese Schranke ist, zeigen die Experimente.

Auffällig: In den Modellnetzen trennt der kleinste Schnitt meist nur **einen einzelnen Standort** ab (der Mindestgrad genügt dann), und bei Netzen aus Regionen ist er eine echte Teilung. Die Zahl der kleinsten Schnitte reicht von 1 bis **C(n, 2)** (Kreis).

Das ist das zweite Stück der Reihe **Schnitte und Zusammenhang**. Den Zusammenhang über disjunkte Wege zeigt **menger-demo**; Max-Flow = Min-Cut für ein Paar **edmonds-karp-demo**; alle Paare auf einmal **gomory-hu-demo**.
Weiter unten: die Experimente **🔬**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So findet man den kleinsten Schnitt", expanded=True):
    st.markdown(
        """
1. **Schnitt:** Eine Zweiteilung der Standorte; der Wert ist die Summe der Gewichte der Leitungen zwischen den Seiten. Der **kleinste Schnitt** ist der kleinste Wert über alle Zweiteilungen (2^(n−1) − 1 Möglichkeiten).
2. **Stoer–Wagner, eine Phase:** Man startet an einem Standort und fügt immer den Standort hinzu, der die **stärkste Bindung** an die schon gewählten hat. Der letzte Standort hat eine Bindung b; der Schnitt, der ihn allein vom Rest trennt, ist der **Schnitt der Phase** (Wert b).
3. **Verschmelzen:** Die letzten beiden Standorte der Phase werden zu einem; die nächste Phase läuft auf dem kleineren Netz. Nach n − 1 Phasen ist der **kleinste Schnitt der Phasen** der kleinste Schnitt des Netzes (exakt).
4. **Karger, ein Lauf:** Man zieht die Leitungen in zufälliger Reihenfolge zusammen (Leitungen innerhalb einer Gruppe werden übersprungen), bis zwei Gruppen übrig sind; der Wert dazwischen ist ein Schnitt, nie kleiner als der kleinste.
5. **Warum wiederholen:** Ein Lauf trifft einen bestimmten kleinsten Schnitt mit Wahrscheinlichkeit mindestens 2 / (n (n − 1)); nach r Läufen ist mit Wahrscheinlichkeit 1 − (1 − 2 / (n (n − 1)))^r mindestens einer dabei.

| Begriff | Bedeutung |
|---|---|
| **Schnitt** | Zweiteilung der Standorte; Wert = Gewicht der Leitungen zwischen den Seiten |
| **Kleinster Schnitt** | kleinster Wert über alle Zweiteilungen (globaler Min-Cut) |
| **Trivial** | der Schnitt trennt nur einen einzelnen Standort ab (sein gewichteter Grad) |
| **Bindung** | Summe der Gewichte der Leitungen eines Standorts zu den schon gewählten |
| **Schnitt der Phase** | Wert, der den letzten Standort einer Phase vom Rest trennt |
| **Kontraktion** | zwei Gruppen zu einer zusammenziehen (Karger: eine zufällige Leitung) |
| **Matrixzugriff / Kantenprüfung** | Zähleinheit bei Stoer–Wagner (Bindung aktualisieren) / bei Karger (angesehene Leitung) |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    kind = st.selectbox("Art des Netzes", list(C.KINDS), format_func=C.KIND_NAMES.get, key="kind_select", help=C.KIND_HELP.get(st.session_state.get("kind_select", C.DEFAULT_KIND), ""))
    n = st.slider("Standorte n", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte das Netz hat (das Gitter rundet auf ein Quadrat). Die Aufzählung aller Schnitte läuft bis 16 Standorte.")
    deg = st.slider("Mittlerer Grad", *bounds("deg_slider"), key="deg_slider", step=0.5, help="Leitungen je Standort im Mittel; wirkt beim Zufallsnetz und innerhalb der Regionen des Verbundnetzes.")
    links = st.slider("Leitungen zwischen je zwei Regionen", *bounds("links_slider"), key="links_slider", help="Wirkt nur beim Verbundnetz.")
    weights = st.selectbox("Gewichte der Leitungen", list(C.WEIGHTS), format_func=C.WEIGHT_NAMES.get, key="weights_select", help="Alle Leitungen gleich stark oder zufällig 1 bis 5 (Kapazität).")
    seed = st.number_input("Zufalls-Seed des Netzes", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Netz erzeugen", width="stretch", on_click=randomize_seed)
    st.caption(C.KIND_REGLER[kind])
    st.markdown("**Karger**")
    runs = st.selectbox("Zahl der Läufe", list(C.RUNS), format_func=_i, key="runs_select", help="Wie oft die zufällige Kontraktion wiederholt wird.")

sync_query_params({"kind_select": kind, "n_slider": int(n), "deg_slider": float(deg), "links_slider": int(links), "weights_select": weights, "seed_input": int(seed), "runs_select": int(runs)})

settings = ev.Settings(kind, int(n), float(deg), int(links), weights, int(seed), int(runs))
with st.spinner("Rechne Stoer–Wagner und die Läufe von Karger..."):
    a = _analysis(settings)
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{settings.kind}_{settings.n}_{settings.deg}_{settings.links}_{settings.weights}_{settings.seed}_{settings.runs}"
inst = a.inst
names = [inst.name(v) for v in range(a.n)]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{C.KIND_NAMES[kind]} mit {_i(a.n)} Standorten und {_i(a.m)} Leitungen (Gesamtgewicht {_i(inst.total_weight)}). Standorte sind ab 1 nummeriert (das Lehrbeispiel hat Buchstaben). Ein Lauf ist eine zufällige Kontraktion.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kleinster Schnitt", _i(a.value), delta=f"{a.value - a.degree_cut:+d} gegen kleinsten Standort" if a.value != a.degree_cut else "gleich dem kleinsten Standort", delta_color="normal" if a.value != a.degree_cut else "off")
m2.metric("Kleinster einzelner Standort", _i(a.degree_cut), delta="gewichteter Mindestgrad", delta_color="off")
m3.metric("Seite des Schnitts", f"{len(a.side)} | {len(a.other_side)}", delta="trennt einen Standort ab" if a.trivial else "echte Teilung", delta_color="off")
m4.metric("Ein Lauf von Karger trifft", f"{ev._pct(a.success_rate)} %", delta=f"Schranke {ev._prob(a.guarantee)}", delta_color="off")

tab_sw, tab_karger, tab_all = st.tabs(["✂️ Stoer–Wagner", "🎲 Karger", "🧮 Alle kleinsten Schnitte"])

# --- Tab 1: Stoer–Wagner -------------------------------------------------------------------------------------------------------------------

with tab_sw:
    k_phase = st.slider("Phase", 1, len(a.sw.phases), a.sw.best_phase + 1, key=f"phase_{signature}", help="Die Phase, deren Ordnung und Schnitt gezeigt werden (vorbelegt: die erste Phase mit dem kleinsten Schnitt).")
    phase = a.sw.phases[k_phase - 1]
    so_far = min(p.cut for p in a.sw.phases[:k_phase])
    p1, p2, p3 = st.columns(3)
    p1.metric("Schnitt der Phase", _i(phase.cut), delta="Bindung des letzten Standorts", delta_color="off")
    p2.metric("Kleinster bisher", _i(so_far), delta=f"nach {k_phase} von {len(a.sw.phases)} Phasen", delta_color="off")
    p3.metric("Gruppen in dieser Phase", _i(len(phase.order)), delta=f"{_i(phase.steps)} Matrixzugriffe", delta_color="off")
    last_names = ", ".join(names[v] for v in phase.last_group)
    before_names = ", ".join(names[v] for v in dict(phase.groups)[phase.before])
    st.markdown(f"**Phase {k_phase}:** Die Gruppe {{{last_names}}} kommt zuletzt zur Menge A, mit Bindung {_i(phase.cut)}: Der Schnitt, der sie vom Rest trennt, hat den Wert {_i(phase.cut)}. "
                f"Danach verschmilzt sie mit der vorletzten Gruppe {{{before_names}}}." + (" **Das ist der kleinste Schnitt des Netzes.**" if k_phase - 1 == a.sw.best_phase else ""))
    st.plotly_chart(build_phase_map(inst, phase), width="stretch", key="chart_phase")
    st.caption("Die Zahl am Standort gibt an, als wievielte Gruppe er in dieser Phase zur Menge A kam. Rot: die letzte Gruppe (wird abgetrennt), blau: die vorletzte (verschmilzt mit ihr); gestrichelt der Schnitt der Phase, dicke Leitungen haben hohes Gewicht.")
    members = dict(phase.groups)
    st.dataframe(pd.DataFrame([{"Reihenfolge": i + 1, "Gruppe": "{" + ", ".join(names[v] for v in members[rep]) + "}", "Bindung an A": b} for i, (rep, b) in enumerate(zip(phase.order, phase.bindings))]),
                 hide_index=True, width="stretch")
    st.plotly_chart(build_phase_cuts(a.sw), width="stretch", key="chart_phase_cuts")
    st.caption("Schnitt der Phase je Phase; der kleinste (zuerst gefundene) ist rot und ist der kleinste Schnitt des Netzes.")
    st.markdown("**Der kleinste Schnitt:**")
    st.plotly_chart(build_cut_map(inst, a.side), width="stretch", key="chart_cut")
    st.caption(f"Seite {{{', '.join(names[v] for v in a.side)}}} gegen den Rest; Wert {_i(a.value)}, Aufwand {_i(a.sw.steps)} Matrixzugriffe in {len(a.sw.phases)} Phasen.")

# --- Tab 2: Karger -------------------------------------------------------------------------------------------------------------------------

with tab_karger:
    c1, c2 = st.columns(2)
    run_no = c1.number_input("Lauf Nr.", 1, a.runs, 1, step=1, key=f"run_{signature}", help="Welcher der Läufe als Ablauf gezeigt wird.")
    contracted = a.batch.contracted[int(run_no) - 1]
    k_step = c2.slider("Kontraktionen", 0, len(contracted), len(contracted), key=f"step_{signature}_{int(run_no)}", help="Wie viele Leitungen schon zusammengezogen sind.")
    run = A.KargerRun(a.batch.values[int(run_no) - 1], a.batch.sides[int(run_no) - 1], contracted, 0)
    hit = run.value == a.value
    q1, q2, q3 = st.columns(3)
    q1.metric("Wert dieses Laufs", _i(run.value), delta="trifft einen kleinsten Schnitt" if hit else f"{run.value - a.value:+d} gegen den kleinsten", delta_color="off" if hit else "normal")
    q2.metric("Erfolgsrate eines Laufs", f"{ev._pct(a.success_rate, 1)} %", delta=f"{_i(a.hits)} von {_i(a.runs)} Läufen", delta_color="off")
    q3.metric("Läufe bis 99 %", _i(a.reps_measured) if a.reps_measured else "–", delta=f"Schranke {_i(a.reps_bound)}", delta_color="off")
    st.plotly_chart(build_contraction_map(inst, run, k_step), width="stretch", key="chart_contraction")
    st.caption("Jede Farbe ist eine Gruppe; dicke dunkle Leitungen sind schon zusammengezogen. Nach der letzten Kontraktion sind zwei Gruppen übrig, die gestrichelten roten Leitungen dazwischen sind der gefundene Schnitt.")
    h1, h2 = st.columns(2)
    h1.markdown("**Was die Läufe finden:**")
    h1.plotly_chart(build_karger_histogram(a.batch, a.value), width="stretch", key="chart_hist")
    h2.markdown("**Wie schnell man sicher ist:**")
    h2.plotly_chart(build_success_curve(a.success_rate, a.guarantee, a.reps_bound), width="stretch", key="chart_curve")
    st.caption(f"Links: Anteil der {_i(a.runs)} Läufe je Schnittwert (grün: der kleinste Wert {_i(a.value)}). Rechts: Wahrscheinlichkeit, nach r Läufen mindestens einen kleinsten Schnitt gefunden zu haben, gemessen gegen die Schranke 2 / (n (n − 1)) = {ev._prob(a.guarantee)} je Lauf; "
               f"mittlere Kosten eines Laufs {_dec(a.mean_steps)} Kantenprüfungen.")

# --- Tab 3: Alle kleinsten Schnitte --------------------------------------------------------------------------------------------------------

with tab_all:
    if a.mincuts is None:
        st.info(f"Die Aufzählung aller Schnitte (2^(n − 1) Zweiteilungen) läuft bis {C.BRUTE_N} Standorte. Verkleinern Sie das Netz, um alle kleinsten Schnitte zu sehen.")
    else:
        mc = a.mincuts
        r1, r2, r3 = st.columns(3)
        r1.metric("Kleinste Schnitte", _i(mc.count), delta=f"Wert {_i(mc.value)}", delta_color="off")
        r2.metric("davon ein einzelner Standort", _i(mc.trivial), delta=f"{_i(mc.count - mc.trivial)} echte Teilung" + ("" if mc.count - mc.trivial == 1 else "en"), delta_color="off")
        r3.metric("Obergrenze C(n, 2)", _i(a.n * (a.n - 1) // 2), delta="Karger: höchstens so viele", delta_color="off")
        st.plotly_chart(build_mincut_map(inst, mc), width="stretch", key="chart_mincuts")
        st.caption("Leitungen nach der Zahl der kleinsten Schnitte, die sie enthalten: je dicker und röter, desto mehr. Gibt es nur einen kleinsten Schnitt, sind es genau dessen Leitungen.")
        st.dataframe(pd.DataFrame([{"Seite mit " + names[0]: "{" + ", ".join(names[v] for v in side) + "}", "Standorte": len(side), "Art": "einzelner Standort" if A.is_trivial(a.n, side) else "echte Teilung",
                                    "Leitungen": len(A.cut_edges(inst.edges, side))} for side in mc.sides[:60]]), hide_index=True, width="stretch")
        if mc.count > 60:
            st.caption(f"Die ersten 60 von {_i(mc.count)} kleinsten Schnitten.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie klein ist der kleinste Schnitt, und wie sicher findet ihn das Würfeln?")
_show(ev.verdict_question(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

with st.spinner("Rechne die Experimente (einmalig, einige Sekunden)..."):
    rows_x, rows_t, (rows_k, rows_c), rows_r, rows_cost = _exactness(), _trivial(), _karger(), _repetitions(), _cost()

st.subheader("🔬 Experiment 1: Stimmen die Verfahren mit der Aufzählung aller Schnitte überein?")
st.caption(f"{len(rows_x)} Netztypen mit je {len(C.SWEEP_SEEDS)} festen Netzen mit {C.EX_N} Standorten; Stoer–Wagner und je {C.EX_RUNS} Läufe von Karger gegen die Aufzählung aller 2^(n − 1) − 1 Schnitte.")
st.plotly_chart(build_exact(rows_x), width="stretch", key="chart_exact")
_show(ev.verdict_exact(rows_x))

st.subheader("🔬 Experiment 2: Wie oft ist der kleinste Schnitt ein einzelner Standort?")
st.caption(f"Anteil der Netze, in denen jeder kleinste Schnitt nur einen Standort abtrennt, bei gleichen und bei zufälligen Gewichten ({C.EX_N} Standorte, {len(C.SWEEP_SEEDS)} Netze je Typ).")
st.plotly_chart(build_trivial(rows_t), width="stretch", key="chart_trivial")
_show(ev.verdict_trivial(rows_t))

st.subheader("🔬 Experiment 3: Wie pessimistisch ist die Schranke von Karger?")
st.caption(f"Erfolgsrate eines Laufs (gleiche Gewichte, {C.EX_N} Standorte, je {C.EX_RUNS} Läufe auf {len(C.SWEEP_SEEDS)} Netzen je Typ) gegen die Schranke; auf dem Kreis rechnet die Demo die Schranke exakt nach.")
st.plotly_chart(build_karger_rates(rows_k), width="stretch", key="chart_karger")
_show(ev.verdict_karger(rows_k, rows_c))

st.subheader("🔬 Experiment 4: Wie viele Läufe braucht man für 99 % Sicherheit?")
st.caption("Aus der gemessenen Erfolgsrate je Netz: Zahl der Läufe, nach denen mit 99 % Wahrscheinlichkeit mindestens ein kleinster Schnitt gefunden ist; Median der Netze und schlechtestes Netz gegen die Schranke.")
st.plotly_chart(build_reps(rows_r), width="stretch", key="chart_reps")
_show(ev.verdict_repetitions(rows_r))

st.subheader("🔬 Experiment 5: Was kostet Stoer–Wagner gegen Karger?")
st.caption("Zufallsnetz mit mittlerem Grad 5 bei 20, 40 und 80 Standorten (vier Netze je Größe, 300 Läufe je Netz): Läufe von Karger bis 99 % Sicherheit, gemessen und nach der Schranke.")
st.plotly_chart(build_cost(rows_cost), width="stretch", key="chart_cost")
_show(ev.verdict_cost(rows_cost))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Ungerichtetes Netz** | Für gerichtete Netze ist der kleinste Schnitt ein anderes Problem (Fluss von s nach t); die Demo rechnet nur ungerichtete Netze. | edmonds-karp-demo |
| **Ein globaler Schnitt, nicht alle Paare** | Den kleinsten Schnitt für jedes Paar liefert der Gomory–Hu-Baum; hier gibt es einen Wert für das ganze Netz. | gomory-hu-demo |
| **Zusammenhang über Wege** | Wie viele disjunkte Wege zwei Standorte verbinden, rechnet menger-demo; ein Schnitt zählt Leitungen, nicht Standorte. | menger-demo |
| **Kleiner Schnitt heißt nicht ausgewogen** | Der kleinste Schnitt trennt meist nur einen Standort ab; wer ein Netz in große Teile teilen will, braucht eine Bedingung an die Größe der Seiten. | - |
| **Nur die einfache Kontraktion** | Verbesserte Varianten (rekursive Kontraktion) und die schnellsten Verfahren der Theorie stehen nur als Einordnung in der Formulierung. | - |
| **Synthetische Netze, bis 80 Standorte** | Reale Netze haben andere Strukturen; Aufwand in Matrixzugriffen und Kantenprüfungen gezählt, nicht in Sekunden. Die Aufzählung aller Schnitte läuft bis 16 Standorte. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein ungerichteter Graph $G = (V, E)$ mit $n = |V|$ Standorten und Leitungsgewichten $w_e \ge 0$. Ein **Schnitt** ist eine Zweiteilung $(S, V \setminus S)$ mit $\emptyset \ne S \subsetneq V$; sein Wert ist

$$w(S) = \sum_{\{u,v\} \in E,\ u \in S,\ v \notin S} w_{uv}.$$

**Kleinster Schnitt (globaler Min-Cut).**

$$\lambda(G) = \min_{\emptyset \ne S \subsetneq V} w(S) \le \min_{v \in V} w(\{v\}).$$

**Stoer–Wagner.** In einer Phase wird $A$ aus einem Startstandort aufgebaut; als nächster kommt der Standort $v \notin A$ mit der stärksten Bindung $w(A, v) = \sum_{u \in A} w_{uv}$. Sind $s$ der vorletzte und $t$ der letzte Standort, so ist der Schnitt der Phase $w(\{t\})$ auf dem aktuellen (verschmolzenen) Netz, und es gilt

$$\lambda(G) = \min\bigl( w(\{t\}),\ \lambda(G / \{s, t\}) \bigr),$$

weil $w(\{t\})$ ein kleinster Schnitt zwischen $s$ und $t$ ist: Trennt ein kleinster Schnitt des Netzes $s$ und $t$, ist $w(\{t\})$ schon so klein wie er; lässt er beide auf derselben Seite, bleibt er im verschmolzenen Netz erhalten. Nach $n - 1$ Phasen ist $\lambda(G)$ der kleinste Schnitt der Phasen.

**Karger.** Eine Leitung wird mit Wahrscheinlichkeit proportional zu ihrem Gewicht gewählt und ihre Endpunkte werden verschmolzen, bis zwei Gruppen übrig sind. Für einen **bestimmten** kleinsten Schnitt $C^*$ gilt: Solange noch $k$ Gruppen übrig sind, hat jede Gruppe mindestens das Gewicht $\lambda$ (sonst gäbe es einen kleineren Schnitt), also ist das Gesamtgewicht mindestens $k \lambda / 2$ und

$$\Pr[\text{$C^*$ überlebt} ] \ \ge\ \prod_{k=3}^{n} \Bigl(1 - \frac{2}{k}\Bigr) = \frac{2}{n (n - 1)}.$$

Daraus folgt: Es gibt höchstens $\binom{n}{2}$ kleinste Schnitte (Summe der Wahrscheinlichkeiten höchstens 1), und der Kreis erreicht die Schranke. **Wiederholungen.** Für Sicherheit $1 - \delta$ genügen

$$r \ge \frac{\ln \delta}{\ln\bigl(1 - 2 / (n (n - 1))\bigr)} \quad \text{Läufe.}$$

**Literatur.** M. Stoer, F. Wagner: *A simple min-cut algorithm*, Journal of the ACM 44 (4), 1997, S. 585–591. D. R. Karger: *Global min-cuts in RNC, and other ramifications of a simple min-cut algorithm*, Proceedings of the Fourth Annual ACM-SIAM Symposium on Discrete Algorithms, 1993, S. 21–30. D. R. Karger, C. Stein: *A new approach to the minimum cut problem*, Journal of the ACM 43 (4), 1996, S. 601–640. Stand der Technik nur als Einordnung, ohne Zahlen der Originale: deterministische Verfahren in nahezu linearer Zeit für einfache Graphen (Kawarabayashi und Thorup, 2015), verbessert von Henzinger, Rao und Wang (2017), und für gewichtete Graphen in Zeit $m^{1+o(1)}$ (Li, 2021).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
