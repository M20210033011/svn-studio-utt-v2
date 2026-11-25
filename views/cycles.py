import pandas as pd
import streamlit as st

import ui_state

STEP = 4
p = ui_state.project()
res, _ = ui_state.results()
ui_state.header(STEP, "Un **cycle de valeur** part du projet central, passe par d'autres parties prenantes "
                "(chacune une seule fois) et revient au projet central. Son **score** est le **produit** "
                "des scores de ses flux. Les premiers cycles du classement sont les **chemins critiques**.")

if not p.focal:
    ui_state.empty_state("Choisissez d'abord le projet central.", ui_state.STEPS[1][0],
                         "Aller aux parties prenantes")
    ui_state.footer_nav(STEP)
    st.stop()
if not res.cycles:
    ui_state.empty_state("Aucun cycle : aucun chemin de flux ne revient au projet central. Vérifiez le "
                         "sens des flux (source → cible).", ui_state.STEPS[2][0], "Aller aux flux")
    ui_state.footer_nav(STEP)
    st.stop()
if res.truncated:
    st.warning(f"Réseau très grand : seuls les {len(res.cycles)} cycles les plus forts sont listés.",
               icon=":material/warning:")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cycles", len(res.cycles), border=True)
c2.metric("Somme des scores", ui_state.fmt(res.total), border=True,
          help="Dénominateur des indicateurs WSO, WOO et WIO.")
c3.metric("Meilleur cycle", ui_state.fmt(res.cycles[0].score), border=True)
c4.metric("Longueur moyenne", ui_state.fmt(sum(c.length for c in res.cycles) / len(res.cycles), 1),
          border=True, help="Nombre moyen de flux par cycle.")

ui_state.outside_cycles_notice()

with st.expander("Filtrer", icon=":material/filter_list:"):
    f1, f2, f3 = st.columns(3)
    min_score = f1.number_input("Score minimal", 0.0, 1.0, 0.0, 0.01, format="%.3f")
    lengths = sorted({c.length for c in res.cycles})
    max_len = f2.select_slider("Longueur maximale", lengths, value=lengths[-1]) if len(lengths) > 1 \
        else lengths[0]
    must = f3.multiselect("Passe par", [s.id for s in p.stakeholders if s.id != p.focal],
                          format_func=p.name_of)

rows, kept = [], []
for i, c in enumerate(res.cycles):
    if c.score < min_score or c.length > max_len or any(m not in c.nodes for m in must):
        continue
    kept.append(c)
    rows.append({"Rang": i + 1, "Score": c.score,
                 "Part du total": c.score / res.total if res.total else 0,
                 "Cycle": " → ".join(p.name_of(n) for n in c.nodes),
                 "Flux": " | ".join(f.name for f in c.flows), "Longueur": c.length})

st.caption(f"{len(kept)} cycle(s) affiché(s). **Cliquez sur une ligne** pour voir le détail du calcul.")
event = st.dataframe(
    pd.DataFrame(rows), hide_index=True, use_container_width=True, on_select="rerun",
    selection_mode="single-row", key="cycles_table",
    column_config={
        "Rang": st.column_config.NumberColumn(width="small"),
        "Score": st.column_config.ProgressColumn(min_value=0.0, max_value=res.cycles[0].score,
                                                 format="%.4f"),
        "Part du total": st.column_config.NumberColumn(format="percent"),
        "Longueur": st.column_config.NumberColumn(width="small", help="Nombre de flux"),
    })

sel = event.selection.rows if event and event.selection else []
if sel and sel[0] < len(kept):
    c = kept[sel[0]]
    with st.container(border=True):
        st.markdown(f"#### Cycle n° {rows[sel[0]]['Rang']} · score {ui_state.fmt(c.score, 6)}")
        steps = pd.DataFrame([{"Étape": k + 1, "De": p.name_of(f.source), "Vers": p.name_of(f.target),
                               "Flux": f.name, "Score": f.score} for k, f in enumerate(c.flows)])
        st.dataframe(steps, hide_index=True, use_container_width=True,
                     column_config={"Score": st.column_config.NumberColumn(format="%.2f")})
        st.markdown("Calcul : " + " × ".join(ui_state.fmt(f.score, 2) for f in c.flows)
                    + f" = **{ui_state.fmt(c.score, 6)}**")

ui_state.footer_nav(STEP)
