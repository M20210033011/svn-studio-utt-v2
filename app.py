"""SVN Studio — point d'entrée de l'application Streamlit.

Lancer en local :  streamlit run app.py
"""

import streamlit as st

import ui_state

st.set_page_config(
    page_title="SVN Studio",
    page_icon=":material/hub:",
    layout="wide",
    menu_items={"About": "SVN Studio — outil open source d'analyse des Stakeholder Value Networks."},
)

home = st.Page("views/accueil.py", title="Accueil", icon=":material/home:", default=True)
guide = st.Page("views/guide.py", title="Guide méthodologique", icon=":material/menu_book:")
steps = [st.Page(path, title=f"{i + 1}. {title}", icon=icon)
         for i, (path, title, icon, _) in enumerate(ui_state.STEPS)]
compare = st.Page("views/comparaison.py", title="Comparer deux scénarios", icon=":material/compare:")
nav = st.navigation({"Démarrer": [home, guide], "Analyse pas à pas": steps, "Outils": [compare]})

with st.sidebar:
    p = ui_state.project()
    res, _ = ui_state.results()
    with st.container(border=True):
        st.caption("Projet actuel")
        st.markdown(f"**{p.name}**")
        st.caption(f"{len(p.stakeholders)} parties prenantes · {len(p.flows)} flux · "
                   f"{len(res.cycles)}{'+' if res.truncated else ''} cycles")
        st.progress(ui_state.progress(), text="Modèle prêt" if ui_state.progress() == 1
                    else "Modèle en préparation")
        text, page, icon = ui_state.next_action()
        st.page_link(page, label=text, icon=icon)
    st.caption(":material/save: Les données restent dans cet onglet. Exportez le projet en JSON "
               "(étape 1) pour le garder.")

ui_state.show_flash()
nav.run()
