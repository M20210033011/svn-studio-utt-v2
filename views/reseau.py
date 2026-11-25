import math

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

import ui_state

STEP = 3
p = ui_state.project()
res, _ = ui_state.results()
ui_state.header(STEP, "Le réseau est dessiné automatiquement à partir de vos données. Le projet central "
                "est au centre ; l'épaisseur d'une flèche suit son score. Survolez une flèche pour lire "
                "le flux.")

if not p.stakeholders:
    ui_state.empty_state("Aucune partie prenante pour l'instant.", ui_state.STEPS[0][0],
                         "Importer des données ou charger un exemple")
    ui_state.footer_nav(STEP)
    st.stop()

# Couleurs adaptées au thème clair ou sombre de l'application.
dark = getattr(getattr(st.context, "theme", None), "type", "light") == "dark"
TEXT = "#f2f4f7" if dark else "#14202c"
LABEL_BG = "rgba(38,39,48,0.92)" if dark else "rgba(255,255,255,0.92)"
LABEL_BORDER = "#4a5361" if dark else "#d5dce2"
EDGE = "#7fb6c9" if dark else "#5b8fa3"
MUTED = "#3d4450" if dark else "#d5dce2"
ACCENT = "#f0a35e" if dark else "#d58a45"
NODE_LINE = "#0e1117" if dark else "#ffffff"

graph_col, ctrl_col = st.columns([3, 1], gap="large")
with ctrl_col:
    with st.container(border=True):
        st.markdown("**Affichage**")
        layout = st.radio("Disposition", ["Projet au centre", "Automatique"], key="net_layout",
                          help="« Automatique » place les nœuds très liés près les uns des autres.")
        show_scores = st.toggle("Scores sur les flèches", value=True, key="net_scores")
    with st.container(border=True):
        st.markdown("**Mettre en évidence**")
        mode = st.radio("Élément", ["Rien", "Un cycle", "Une partie prenante"], key="net_mode",
                        label_visibility="collapsed")
        highlight_flows: set[str] = set()
        highlight_nodes: set[str] = set()
        if mode == "Un cycle":
            if res.cycles:
                i = st.selectbox("Cycle", range(min(50, len(res.cycles))),
                                 format_func=lambda k: f"n° {k + 1} · score {ui_state.fmt(res.cycles[k].score)}")
                c = res.cycles[i]
                highlight_flows = {f.id for f in c.flows}
                highlight_nodes = set(c.nodes)
                st.caption(" → ".join(p.name_of(n) for n in c.nodes))
            else:
                st.caption("Aucun cycle dans ce réseau.")
        elif mode == "Une partie prenante":
            sid = st.selectbox("Partie prenante", [s.id for s in p.stakeholders], format_func=p.name_of)
            highlight_flows = {f.id for f in p.valid_flows() if sid in (f.source, f.target)}
            highlight_nodes = {sid}
            st.caption(f"{sum(f.source == sid for f in p.valid_flows())} flux émis · "
                       f"{sum(f.target == sid for f in p.valid_flows())} flux reçus")

G = nx.MultiDiGraph()
G.add_nodes_from(s.id for s in p.stakeholders)
for f in p.valid_flows():
    G.add_edge(f.source, f.target, key=f.id)

others = [s.id for s in p.stakeholders if s.id != p.focal]
if layout == "Projet au centre" and p.focal:
    pos = {p.focal: (0.0, 0.0)}
    for i, sid in enumerate(others):
        a = 2 * math.pi * i / max(1, len(others)) + math.pi / 2
        pos[sid] = (math.cos(a), math.sin(a))
else:
    pos = nx.spring_layout(nx.Graph(G), seed=42)
    pos = {k: (float(v[0]), float(v[1])) for k, v in pos.items()}

fig = go.Figure()
NODE_R = 0.09  # rayon visuel d'un nœud, en unités du graphique
pair_count: dict = {}
hover_x, hover_y, hover_t = [], [], []
active = bool(highlight_flows) or bool(highlight_nodes)
for f in p.valid_flows():
    (x0, y0), (x1, y1) = pos[f.source], pos[f.target]
    k = pair_count.get((f.source, f.target), 0)
    pair_count[(f.source, f.target)] = k + 1
    # Courbe de Bézier quadratique : sépare les flux aller/retour et les flux parallèles.
    dx, dy = x1 - x0, y1 - y0
    norm = math.hypot(dx, dy) or 1
    off = 0.12 * (1 + k) * norm
    cx, cy = (x0 + x1) / 2 - dy / norm * off, (y0 + y1) / 2 + dx / norm * off
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1,
            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1) for t in [i / 40 for i in range(41)]]
    pts = [q for q in pts if math.hypot(q[0] - x0, q[1] - y0) > NODE_R
           and math.hypot(q[0] - x1, q[1] - y1) > NODE_R * 1.15]
    if len(pts) < 2:
        continue
    on = f.id in highlight_flows
    color = ACCENT if on else (MUTED if active else EDGE)
    width = 1 + 3.5 * float(f.score) + (1.5 if on else 0)
    fig.add_trace(go.Scatter(x=[q[0] for q in pts], y=[q[1] for q in pts], mode="lines",
                             hoverinfo="skip", line=dict(color=color, width=width), showlegend=False))
    (ax, ay), (ex, ey) = pts[-2], pts[-1]
    fig.add_annotation(x=ex, y=ey, ax=ax, ay=ay, xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=width, arrowcolor=color)
    mx, my = pts[len(pts) // 2]
    hover_x.append(mx); hover_y.append(my)
    hover_t.append(f"<b>{f.name}</b><br>{p.name_of(f.source)} → {p.name_of(f.target)}"
                   f"<br>score {ui_state.fmt(f.score, 2)}")
    if show_scores and (not active or on):
        fig.add_annotation(x=mx, y=my, text=ui_state.fmt(f.score, 2), showarrow=False,
                           font=dict(size=10, color=TEXT), bgcolor=LABEL_BG,
                           bordercolor=LABEL_BORDER, borderwidth=1, borderpad=2)

fig.add_trace(go.Scatter(x=hover_x, y=hover_y, mode="markers", marker=dict(size=14, opacity=0),
                         hovertext=hover_t, hoverinfo="text", showlegend=False))
fig.add_trace(go.Scatter(
    x=[pos[s.id][0] for s in p.stakeholders], y=[pos[s.id][1] for s in p.stakeholders],
    mode="markers", hoverinfo="text",
    hovertext=[f"<b>{s.name}</b><br>{s.type}" + ("<br>projet central" if s.id == p.focal else "")
               for s in p.stakeholders],
    marker=dict(size=[56 if s.id == p.focal else 42 for s in p.stakeholders],
                color=[s.color for s in p.stakeholders],
                opacity=[1 if not active or s.id in highlight_nodes else 0.45 for s in p.stakeholders],
                line=dict(color=[ACCENT if s.id in highlight_nodes else NODE_LINE
                                 for s in p.stakeholders], width=3)),
    showlegend=False))
for s in p.stakeholders:
    x, y = pos[s.id]
    fig.add_annotation(x=x, y=y, yshift=-36 if s.id != p.focal else -42,
                       text=f"<b>{s.name}</b>" + (" ★" if s.id == p.focal else ""),
                       showarrow=False, font=dict(size=13, color=TEXT), bgcolor=LABEL_BG,
                       bordercolor=LABEL_BORDER, borderwidth=1, borderpad=3)
fig.update_layout(height=640, margin=dict(l=10, r=10, t=10, b=10),
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                  font=dict(color=TEXT), hoverlabel=dict(font_size=13),
                  xaxis=dict(visible=False, range=[-1.35, 1.35]),
                  yaxis=dict(visible=False, scaleanchor="x", range=[-1.3, 1.3]))
with graph_col:
    st.plotly_chart(fig, use_container_width=True, theme=None,
                    config={"displaylogo": False,
                            "toImageButtonOptions": {"format": "png", "filename": "reseau_svn", "scale": 2}})
    st.caption("★ = projet central. Pour enregistrer l'image : icône appareil photo en haut à droite "
               "du graphique.")

ui_state.footer_nav(STEP)
