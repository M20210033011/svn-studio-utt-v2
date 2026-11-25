import streamlit as st

import ui_state
from svn_core import examples
from svn_core.model import Project

p = ui_state.project()
res, _ = ui_state.results()

st.title("SVN Studio")
st.markdown(
    "Analysez un **Stakeholder Value Network** : les acteurs d'un projet, la valeur qu'ils "
    "échangent et les **cycles de valeur** qui reviennent au projet. Aucune installation, aucune "
    "programmation : il suffit de saisir ou d'importer un tableau de flux.")

# --- 1. Démarrer -----------------------------------------------------------------
st.subheader("Démarrer", divider="gray")
c1, c2, c3 = st.columns(3, gap="medium")
with c1, st.container(border=True, height="stretch"):
    st.markdown("#### :material/school: Découvrir avec un exemple")
    st.caption("Un petit réseau déjà rempli, pour voir chaque écran en 5 minutes.")
    choice = st.selectbox("Exemple", list(examples.EXAMPLES), label_visibility="collapsed")
    if st.button("Charger l'exemple", type="primary", use_container_width=True):
        ui_state.replace_project(examples.EXAMPLES[choice](), "Exemple chargé.")
with c2, st.container(border=True, height="stretch"):
    st.markdown("#### :material/upload_file: Importer vos données")
    st.caption("Un tableau de flux (CSV ou TXT) ou un projet JSON déjà sauvegardé. "
               "Un aperçu est affiché avant l'import.")
    st.page_link(ui_state.STEPS[0][0], label="Importer un fichier", icon=":material/arrow_forward:")
with c3, st.container(border=True, height="stretch"):
    st.markdown("#### :material/edit_note: Partir de zéro")
    st.caption("Créez vos parties prenantes, puis vos flux, directement dans l'outil.")
    if st.button("Créer un projet vide", use_container_width=True):
        ui_state.replace_project(Project(name="Mon projet SVN"), "Projet vide créé.")

# --- 2. La démarche --------------------------------------------------------------
st.subheader("La démarche en 6 étapes", divider="gray")
st.caption("Le menu de gauche suit cet ordre. Chaque page indique l'étape suivante en bas.")
cols = st.columns(3, gap="small")
for i, (path, title, icon, help_text) in enumerate(ui_state.STEPS):
    with cols[i % 3], st.container(border=True, height="stretch"):
        st.page_link(path, label=f"{i + 1}. {title}", icon=icon)
        st.caption(help_text)

# --- 3. Projet en cours ------------------------------------------------------------
st.subheader(f"Projet en cours : {p.name}", divider="gray")
if p.description:
    st.caption(p.description)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Parties prenantes", len(p.stakeholders), border=True)
m2.metric("Flux de valeur", len(p.flows), border=True)
m3.metric("Cycles", f"{len(res.cycles)}{'+' if res.truncated else ''}", border=True,
          help="Chemins qui partent du projet central et y reviennent.")
m4.metric("Projet central", p.name_of(p.focal) if p.focal else "—", border=True)

left, right = st.columns([3, 2], gap="large")
with left:
    st.markdown("**Votre modèle est-il prêt ?**")
    for text, done, page in ui_state.checklist():
        if done:
            st.markdown(f":green[:material/check_circle:] {text}")
        else:
            st.page_link(page, label=text, icon=":material/radio_button_unchecked:")
with right:
    text, page, icon = ui_state.next_action()
    with st.container(border=True):
        st.caption("Prochaine étape")
        st.page_link(page, label=text, icon=icon)
    if res.truncated:
        st.warning("Le réseau est très grand : seuls les cycles les plus importants sont conservés.")
