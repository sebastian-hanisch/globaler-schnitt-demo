"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import gsc_algorithm as A
import gsc_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, pairs):
    xs, ys = [], []
    for u, v in pairs:
        xs += [float(inst.xy[u, 0]), float(inst.xy[v, 0]), None]
        ys += [float(inst.xy[u, 1]), float(inst.xy[v, 1]), None]
    return xs, ys


def _nodes(inst, nodes, color, size, symbol="circle", name=None, show_text=False, hover=None, line_color="white"):
    nodes = list(nodes)
    return go.Scatter(
        x=[float(inst.xy[v, 0]) for v in nodes], y=[float(inst.xy[v, 1]) for v in nodes], mode="markers+text" if show_text else "markers",
        marker=dict(size=size, color=color, symbol=symbol, line=dict(color=line_color, width=1)), text=[inst.name(v) for v in nodes] if show_text else None,
        textfont=dict(size=10, color="#ffffff"), textposition="middle center",
        hovertext=hover or [f"Standort {inst.name(v)}" for v in nodes], hoverinfo="text", name=name, showlegend=name is not None)


def _map_layout(fig, inst, height=470):
    xs, ys = inst.xy[:, 0], inst.xy[:, 1]
    pad = 0.25 * max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), 1.0)
    fig.update_xaxes(visible=False, range=[float(xs.min()) - pad, float(xs.max()) + pad])
    fig.update_yaxes(visible=False, range=[float(ys.min()) - pad, float(ys.max()) + pad], scaleanchor="x", scaleratio=1)
    return _base(fig, height)


def _edge_traces(fig, inst, edges, color, dash=None, scale=1.0, name=None):
    """Eine Linie je Gewicht (Dicke folgt dem Gewicht), damit die Karte Gewichte zeigt."""
    by_w = {}
    for u, v, w in edges:
        by_w.setdefault(w, []).append((u, v))
    first = True
    for w, pairs in sorted(by_w.items()):
        xs, ys = _lines(inst, pairs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=min(1.2 + 1.1 * (w - 1), 8) * scale, dash=dash), hoverinfo="skip", showlegend=name is not None and first, name=name))
        first = False


def build_cut_map(inst, side, title_names=("eine Seite", "die andere Seite")):
    """Karte mit dem Schnitt: die beiden Seiten in zwei Farben, die Leitungen dazwischen rot und gestrichelt."""
    fig = go.Figure()
    s = set(side)
    cross = [(u, v, w) for u, v, w in inst.edges if (u in s) != (v in s)]
    rest = [(u, v, w) for u, v, w in inst.edges if (u in s) == (v in s)]
    _edge_traces(fig, inst, rest, C.COLOR_EDGE)
    _edge_traces(fig, inst, cross, C.COLOR_CUT, dash="dot", scale=1.6, name=f"Schnitt ({sum(w for _u, _v, w in cross)})")
    show_text = inst.n <= 60
    size = 22 if show_text else 11
    fig.add_trace(_nodes(inst, sorted(s), C.COLOR_SIDE_A, size, name=title_names[0], show_text=show_text))
    fig.add_trace(_nodes(inst, [v for v in range(inst.n) if v not in s], C.COLOR_SIDE_B, size, name=title_names[1], show_text=show_text))
    return _map_layout(fig, inst)


def build_phase_map(inst, phase):
    """Eine Phase von Stoer–Wagner: jeder Standort trägt die Nummer, in der seine Gruppe zur Menge A kam; der letzte (rot) wird vom Rest getrennt, der vorletzte (blau) verschmilzt mit ihm."""
    fig = go.Figure()
    members = {rep: grp for rep, grp in phase.groups}
    rank = {rep: i + 1 for i, rep in enumerate(phase.order)}
    group_of = {v: rep for rep, grp in phase.groups for v in grp}
    last = set(members[phase.last])
    before = set(members[phase.before])
    cross = [(u, v, w) for u, v, w in inst.edges if (u in last) != (v in last)]
    rest = [(u, v, w) for u, v, w in inst.edges if (u in last) == (v in last)]
    _edge_traces(fig, inst, rest, C.COLOR_EDGE)
    _edge_traces(fig, inst, cross, C.COLOR_CUT, dash="dot", scale=1.6, name=f"Schnitt der Phase ({phase.cut})")
    show_text = inst.n <= 60
    others = [v for v in range(inst.n) if v not in last and v not in before]
    size = 24 if show_text else 11

    def trace(nodes, color, name, symbol="circle"):
        hover = [f"Standort {inst.name(v)}: Gruppe {rank[group_of[v]]} von {len(phase.order)}, {len(members[group_of[v]])} Standort(e)" for v in nodes]
        t = _nodes(inst, nodes, color, size, symbol, name, False, hover)
        return t
    fig.add_trace(trace(others, C.COLOR_NODE, None))
    fig.add_trace(trace(sorted(before), C.COLOR_SIDE_B, "vorletzte Gruppe (verschmilzt)"))
    fig.add_trace(trace(sorted(last), C.COLOR_CUT, "letzte Gruppe (wird abgetrennt)", "diamond"))
    if show_text:
        for v in range(inst.n):
            fig.add_annotation(x=float(inst.xy[v, 0]), y=float(inst.xy[v, 1]), text=str(rank[group_of[v]]), showarrow=False, font=dict(size=10, color="#14233B" if v in others else "#ffffff"))
    return _map_layout(fig, inst)


def build_phase_cuts(sw):
    """Schnitt der Phase je Phase; der kleinste (erste) ist der kleinste Schnitt des Netzes."""
    xs = list(range(1, len(sw.phases) + 1))
    colors = [C.COLOR_CUT if i == sw.best_phase else C.COLOR_NODE for i in range(len(sw.phases))]
    fig = go.Figure(go.Bar(x=xs, y=[p.cut for p in sw.phases], marker_color=colors, hovertemplate="Phase %{x}: Schnitt %{y}<extra></extra>", showlegend=False))
    fig.update_xaxes(title_text="Phase", dtick=1 if len(xs) <= 20 else None)
    fig.update_yaxes(title_text="Schnitt der Phase")
    return _base(fig, 300)


def contraction_state(n, edges, contracted, k):
    """Gruppen nach den ersten k Kontraktionen: (Vertreter-Feld als Liste, Gruppen als Mengen)."""
    parent = list(range(n))
    for i in contracted[:k]:
        u, v, _w = edges[i]
        ru, rv = A._find(parent, u), A._find(parent, v)
        if ru != rv:
            parent[rv] = ru
    groups = {}
    for v in range(n):
        groups.setdefault(A._find(parent, v), []).append(v)
    return parent, list(groups.values())


def build_contraction_map(inst, run, k):
    """Ein Lauf von Karger nach k Kontraktionen: jede Gruppe eine Farbe, zusammengezogene Leitungen dick, am Ende der Schnitt rot."""
    fig = go.Figure()
    _parent, groups = contraction_state(inst.n, inst.edges, run.contracted, k)
    done = k >= len(run.contracted)
    contracted = {run.contracted[i] for i in range(min(k, len(run.contracted)))}
    group_of = {v: gi for gi, g in enumerate(groups) for v in g}
    inner = [(u, v, w) for i, (u, v, w) in enumerate(inst.edges) if i in contracted]
    between = [(u, v, w) for i, (u, v, w) in enumerate(inst.edges) if i not in contracted and group_of[u] != group_of[v]]
    same = [(u, v, w) for i, (u, v, w) in enumerate(inst.edges) if i not in contracted and group_of[u] == group_of[v]]
    _edge_traces(fig, inst, same, C.COLOR_EDGE)
    _edge_traces(fig, inst, between, C.COLOR_CUT if done else C.COLOR_EDGE, dash="dot" if done else None, scale=1.6 if done else 1.0, name=f"Schnitt ({run.value})" if done else None)
    _edge_traces(fig, inst, inner, "#14233B", scale=1.8)
    show_text = inst.n <= 60
    size = 22 if show_text else 11
    for gi, g in enumerate(sorted(groups, key=lambda g: g[0])):
        fig.add_trace(_nodes(inst, g, C.COLOR_GROUPS[gi % len(C.COLOR_GROUPS)], size, show_text=show_text))
    return _map_layout(fig, inst)


def build_karger_histogram(batch, best):
    """Wie oft liefert ein Lauf welchen Schnittwert? Der kleinste Wert ist grün."""
    counts = {}
    for v in batch.values:
        counts[v] = counts.get(v, 0) + 1
    xs = sorted(counts)
    fig = go.Figure(go.Bar(x=[str(x) for x in xs], y=[100 * counts[x] / batch.runs for x in xs], marker_color=[C.COLOR_BAR3 if x == best else C.COLOR_NODE for x in xs],
                           text=[f"{100 * counts[x] / batch.runs:.0f} %" for x in xs], textposition="outside", cliponaxis=False, showlegend=False))
    fig.update_xaxes(title_text="Wert des gefundenen Schnitts")
    fig.update_yaxes(title_text="Anteil der Läufe (%)", range=[0, 118])
    return _base(fig, 320)


def build_success_curve(p, guarantee, reps_bound):
    """Wahrscheinlichkeit, nach r Läufen mindestens einen kleinsten Schnitt gefunden zu haben: gemessen (aus der Erfolgsrate eines Laufs) und garantiert (aus der Schranke)."""
    top = max(10, int(reps_bound * 1.1))
    xs = sorted(set([1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711]) | {reps_bound})
    xs = [x for x in xs if x <= top]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100 * (1 - (1 - p) ** r) for r in xs], mode="lines+markers", name="gemessene Erfolgsrate", line=dict(color=C.COLOR_BAR3, width=3), hovertemplate="%{x} Läufe: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * (1 - (1 - guarantee) ** r) for r in xs], mode="lines+markers", name="Schranke 2 / (n (n − 1))", line=dict(color=C.COLOR_BAR2, width=3, dash="dash"),
                             hovertemplate="%{x} Läufe: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Läufe (logarithmisch)", type="log")
    fig.update_yaxes(title_text="mindestens ein kleinster Schnitt gefunden (%)", range=[0, 105])
    return _base(fig, 340)


def build_mincut_map(inst, mincuts):
    """Alle kleinsten Schnitte: Leitungen nach der Zahl der kleinsten Schnitte, die sie enthalten (dicker und röter = in mehr Schnitten)."""
    fig = go.Figure()
    counts = {}
    for side in mincuts.sides:
        for u, v in A.cut_edges(inst.edges, side):
            counts[(u, v)] = counts.get((u, v), 0) + 1
    top = max(counts.values()) if counts else 1
    free = [(u, v, w) for u, v, w in inst.edges if (u, v) not in counts]
    _edge_traces(fig, inst, free, C.COLOR_EDGE)
    for level in sorted(set(counts.values())):
        pairs = [(u, v) for (u, v), c in counts.items() if c == level]
        xs, ys = _lines(inst, pairs)
        share = level / top
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=f"rgba(209,73,91,{0.35 + 0.65 * share:.2f})", width=2 + 6 * share), hoverinfo="skip", name=f"in {level} von {mincuts.count} kleinsten Schnitten"))
    show_text = inst.n <= 60
    fig.add_trace(_nodes(inst, range(inst.n), C.COLOR_NODE, 22 if show_text else 11, show_text=False, line_color="#8a9a9c"))
    if show_text:
        for v in range(inst.n):
            fig.add_annotation(x=float(inst.xy[v, 0]), y=float(inst.xy[v, 1]), text=inst.name(v), showarrow=False, font=dict(size=9, color="#14233B"))
    return _map_layout(fig, inst)


# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------


def build_exact(rows):
    ys = [round(100 * (r["checks"] - r["wrong"]) / r["checks"]) if r["checks"] else 0 for r in rows]
    fig = go.Figure(go.Bar(x=[r["label"] for r in rows], y=ys, marker_color=C.COLOR_BAR, text=[f"{y} %" for y in ys], textposition="outside", cliponaxis=False, showlegend=False))
    fig.update_yaxes(title_text="Prüfungen ohne Abweichung (%)", range=[0, 118])
    return _base(fig)


def build_trivial(rows):
    labels = []
    for r in rows:
        if r["label"] not in labels:
            labels.append(r["label"])
    fig = go.Figure()
    for weights, color in (("unit", C.COLOR_BAR), ("random", C.COLOR_BAR2)):
        part = {r["label"]: r for r in rows if r["weights"] == weights}
        fig.add_trace(go.Bar(x=labels, y=[round(100 * part[l]["all_trivial"] / part[l]["nets"]) for l in labels], name=C.WEIGHT_NAMES[weights], marker_color=color, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Netze, in denen jeder kleinste Schnitt ein Standort ist (%)", range=[0, 105])
    return _base(fig)


def build_karger_rates(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[round(100 * r["mean_rate"], 1) for r in rows], name="ein Lauf trifft einen kleinsten Schnitt (Mittel)", marker_color=C.COLOR_BAR3, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.add_trace(go.Bar(x=labels, y=[round(100 * r["mean_fixed"], 2) for r in rows], name="ein Lauf trifft genau den Schnitt von Stoer–Wagner", marker_color=C.COLOR_BAR, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.add_hline(y=100 * rows[0]["guarantee"], line=dict(color=C.COLOR_CUT, dash="dash"), annotation_text="Schranke 2 / (n (n − 1))", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Erfolgsrate eines Laufs (%)", range=[0, 105])
    return _base(fig)


def build_reps(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[r["median"] or 0 for r in rows], name="gemessen, Median der Netze", marker_color=C.COLOR_BAR3, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_trace(go.Bar(x=labels, y=[r["worst"] or 0 for r in rows], name="gemessen, schlechtestes Netz", marker_color=C.COLOR_BAR2, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_hline(y=rows[0]["bound"], line=dict(color=C.COLOR_CUT, dash="dash"), annotation_text=f"Schranke {rows[0]['bound']}", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Läufe für 99 % Sicherheit")
    return _base(fig)


def build_cost(rows):
    xs = [f"{r['n']} Standorte" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[r["reps"] if r["reps"] is not None else 0.5 for r in rows], name="gemessen (Mittel)", marker_color=C.COLOR_BAR3, text=[f"{r['reps']:.1f}".replace(".", ",") if r["reps"] is not None else "?" for r in rows],
                         textposition="outside", cliponaxis=False))
    fig.add_trace(go.Bar(x=xs, y=[r["bound_reps"] for r in rows], name="Schranke", marker_color=C.COLOR_BAR2, text=[f"{r['bound_reps']:,}".replace(",", ".") for r in rows], textposition="outside", cliponaxis=False))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Läufe von Karger für 99 % Sicherheit (logarithmisch)", type="log")
    return _base(fig)
