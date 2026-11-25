import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_state
from svn_core import METRICS, outside_cycles
from svn_core import io as svn_io
from svn_core.comparaison import Scenario, compare_critical_paths, compare_indicator, summary

st.title("Comparer deux scénarios")
st.markdown(
    "Mettez côte à côte deux versions d'un même réseau, par exemple **sans** et **avec** une nouvelle "
    "partie prenante. Le **scénario A** est le projet actuel. Le **scénario B** est un projet JSON "
    "que vous importez ici. Les parties prenantes et les flux sont rapprochés par leur **nom**.")

a_project = ui_state.project()
with st.container(border=True):
    st.markdown("#### :material/upload_file: Scénario B")
    up = st.file_uploader("Projet JSON à comparer au projet actuel", type=["json"], key="up_compare")
    if up:
        try:
            st.session_state.compare_b = svn_io.load_json(svn_io.decode_bytes(up.getvalue()))
        except ValueError as e:
            st.error(f"Fichier non valide : {e}", icon=":material/error:")

b_project = st.session_state.get("compare_b")
if b_project is None:
    ui_state.empty_state("Importez un projet JSON pour le scénario B. Le scénario A est le projet actuel "
                         "(changez-le à l'étape 1 si besoin).", ui_state.STEPS[0][0],
                         "Changer le projet actuel")
    st.stop()

a, b = Scenario.of(a_project), Scenario.of(b_project)

# --- Chiffres clés -------------------------------------------------------------------
st.subheader("Chiffres clés", divider="gray")
sa, sb = summary(a), summary(b)
st.caption(f"**A** : {a_project.name} · **B** : {b_project.name}")
st.dataframe(pd.DataFrame([{"": k, "A": sa[k], "B": sb[k]} for k in sa]),
             hide_index=True, use_container_width=True,
             column_config={c: st.column_config.NumberColumn(format="%.4g") for c in ("A", "B")})
for label, sc in (("A", a), ("B", b)):
    if sc.cycles.truncated:
        st.warning(f"Scénario {label} : réseau très grand, seuls les cycles les plus forts sont gardés.")
    out = outside_cycles(sc.project, sc.cycles)
    if out:
        st.caption(f":material/visibility_off: Scénario {label} · hors de tous les cycles (WSO = 0) : "
                   + " ; ".join(f"{sc.project.name_of(sid)}, {reason}" for sid, reason in out))

# --- Un indicateur ---------------------------------------------------------------------
st.subheader("Indicateur", divider="gray")
LABELS = {"WSO": "WSO", "INFLUENCE_EMIS": "Influence · émis", "INFLUENCE_RECUS": "Influence · reçus",
          "INFLUENCE_GLOBAL": "Influence · émis + reçus", "WOO": "WOO", "WIO": "WIO", "WVFO": "WVFO"}
key = st.segmented_control("Indicateur", list(LABELS), default="WSO", format_func=LABELS.get,
                           key="cmp_metric") or "WSO"
m = METRICS[key]
st.caption(f"{m['title']} · {m['formula']}")
rows = compare_indicator(a, b, key)
if not rows:
    ui_state.empty_state("Aucun élément à comparer avec cet indicateur.")
else:
    df = pd.DataFrame(rows)
    fmt = "percent" if m["unit"] == "pct" else "%.4f"
    tab_table, tab_chart = st.tabs([":material/table: Tableau", ":material/bar_chart: Graphique"])
    with tab_table:
        st.dataframe(df, hide_index=True, use_container_width=True,
                     column_config={c: st.column_config.NumberColumn(format=fmt)
                                    for c in ("A", "B", "Écart (B − A)")})
        st.caption("Case vide : l'élément n'existe pas dans ce scénario.")
    with tab_chart:
        fig = go.Figure()
        for col, color in (("A", "#9aa5b1"), ("B", "#298ca6")):
            fig.add_bar(name=col, y=df["Élément"], x=df[col], orientation="h", marker_color=color,
                        hovertemplate="%{y} : %{x:.4f}<extra>" + col + "</extra>")
        fig.update_layout(barmode="group", yaxis=dict(autorange="reversed", title=None),
                          xaxis=dict(title=None, tickformat=".0%" if m["unit"] == "pct" else ".2f"),
                          height=max(280, 52 * len(df)), margin=dict(l=10, r=30, t=10, b=10),
                          legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

# --- Chemins critiques -------------------------------------------------------------------
st.subheader("Chemins critiques", divider="gray")
st.caption("Les 10 meilleurs cycles de chaque scénario, avec leur rang dans l'autre scénario. "
           "Un cycle est identifié par la suite des noms de ses flux. Case vide : cycle absent.")
cp = compare_critical_paths(a, b)
if cp:
    st.dataframe(pd.DataFrame(cp), hide_index=True, use_container_width=True,
                 column_config={"Score A": st.column_config.NumberColumn(format="%.4f"),
                                "Score B": st.column_config.NumberColumn(format="%.4f")})
else:
    ui_state.empty_state("Aucun cycle dans les deux scénarios.")
