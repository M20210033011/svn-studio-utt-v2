import pandas as pd
import plotly.express as px
import streamlit as st

import ui_state
from svn_core import METRICS
from svn_core import io as svn_io

STEP = 5
p = ui_state.project()
res, metrics = ui_state.results()
ui_state.header(STEP, "Deux familles d'indicateurs, qui ne répondent **pas** à la même question. "
                "Ces scores décrivent le modèle ; ce ne sont pas des probabilités de réussite.")

FAMILIES = {
    "Fondés sur les cycles": ["WSO", "WOO", "WIO", "WVFO"],
    "Influence moyenne": ["INFLUENCE_EMIS", "INFLUENCE_RECUS", "INFLUENCE_GLOBAL"],
}
LABELS = {"WSO": "WSO · parties prenantes", "WOO": "WOO · sorties du projet",
          "WIO": "WIO · entrées du projet", "WVFO": "WVFO · flux",
          "INFLUENCE_EMIS": "Émis", "INFLUENCE_RECUS": "Reçus", "INFLUENCE_GLOBAL": "Émis + reçus"}

family = st.segmented_control("Famille d'indicateurs", list(FAMILIES), default=list(FAMILIES)[0],
                              key="prio_family") or list(FAMILIES)[0]
key = st.segmented_control("Indicateur", FAMILIES[family], default=FAMILIES[family][0],
                           format_func=LABELS.get, key=f"prio_{family}") or FAMILIES[family][0]
m, rows = METRICS[key], metrics[key]

with st.container(border=True):
    st.markdown(f"#### {m['title']}")
    st.markdown(f":material/help: **Question :** {m['question']}")
    st.markdown(f":material/function: **Formule :** {m['formula']}")
    if family == "Fondés sur les cycles":
        st.caption("Calculé à partir des cycles de valeur (étape 5).")
        if key == "WSO":
            ui_state.outside_cycles_notice()
    else:
        st.caption("Calculé directement sur les flux, sans les cycles. Une partie prenante sans flux de ce "
                   "type reçoit 0. Le projet central est inclus.")

if m["cycles"] and not res.cycles:
    ui_state.empty_state("Cet indicateur demande au moins un cycle revenant au projet central.",
                         ui_state.STEPS[2][0], "Aller aux flux")
    ui_state.footer_nav(STEP)
    st.stop()
if not rows:
    ui_state.empty_state("Aucun élément à classer avec cet indicateur.")
    ui_state.footer_nav(STEP)
    st.stop()

df = pd.DataFrame([{"Rang": i + 1, "Élément": r.name, "Valeur": r.value,
                    **({"Nb de flux": r.count, "Somme des scores": r.total} if r.count is not None else {})}
                   for i, r in enumerate(rows)])
top = rows[0]
st.markdown(f"**En tête :** {top.name} "
            f"({ui_state.pct(top.value) if m['unit'] == 'pct' else ui_state.fmt(top.value)})")

tab_chart, tab_table = st.tabs([":material/bar_chart: Graphique", ":material/table: Tableau"])
with tab_chart:
    fig = px.bar(df, x="Valeur", y="Élément", orientation="h",
                 text=df["Valeur"].map(ui_state.pct if m["unit"] == "pct" else ui_state.fmt))
    fig.update_traces(marker_color="#298ca6", textposition="outside", cliponaxis=False,
                      hovertemplate="%{y} : %{x:.4f}<extra></extra>")
    fig.update_layout(yaxis=dict(autorange="reversed", title=None),
                      xaxis=dict(title=None, tickformat=".0%" if m["unit"] == "pct" else ".2f"),
                      height=max(260, 44 * len(df)), margin=dict(l=10, r=50, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
with tab_table:
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_config={"Valeur": st.column_config.NumberColumn(
                     format="percent" if m["unit"] == "pct" else "%.4f"),
                     "Somme des scores": st.column_config.NumberColumn(format="%.4f")})
    st.download_button("Télécharger tous les indicateurs (CSV)", svn_io.indicators_csv(metrics),
                       "indicateurs.csv", "text/csv", icon=":material/download:")

ui_state.footer_nav(STEP)
