import pandas as pd
import streamlit as st

import ui_state
from svn_core.model import COLORS, TYPES, Stakeholder, new_id

STEP = 1
p = ui_state.project()
ui_state.header(STEP, "Les **parties prenantes** sont les nœuds du réseau : les personnes, groupes "
                "ou organisations qui donnent ou reçoivent de la valeur.")

# --- Projet central -------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### :material/my_location: Projet central")
    st.caption("Le point de départ et d'arrivée de tous les cycles de valeur : le projet ou "
               "l'organisation que vous étudiez.")
    if p.stakeholders:
        ids = [s.id for s in p.stakeholders]
        idx = ids.index(p.focal) if p.focal in ids else 0
        focal = st.selectbox("Projet central", ids, index=idx, format_func=p.name_of,
                             label_visibility="collapsed")
        if focal != p.focal:
            p.focal = focal
            ui_state.touch()
            ui_state.flash(f"Projet central : {p.name_of(focal)}.")
            st.rerun()
    else:
        st.caption("Ajoutez d'abord des parties prenantes ci-dessous.")

# --- Ajout rapide -----------------------------------------------------------------
with st.popover("Ajouter une partie prenante", icon=":material/person_add:"):
    with st.form("add_stakeholder", clear_on_submit=True, border=False):
        name = st.text_input("Nom *", placeholder="ex. Mairie")
        typ = st.selectbox("Profil", TYPES, index=TYPES.index("Autre"))
        desc = st.text_input("Description", placeholder="facultatif")
        if st.form_submit_button("Ajouter", type="primary"):
            if not name.strip():
                st.error("Le nom est obligatoire.")
            elif p.find_by_name(name):
                st.error("Une partie prenante porte déjà ce nom.")
            else:
                s = p.add_stakeholder(name, typ, desc)
                if not p.focal:
                    p.focal = s.id
                ui_state.touch()
                ui_state.flash(f"« {s.name} » ajoutée.")
                st.rerun()

# --- Tableau éditable ---------------------------------------------------------------
st.markdown("#### Liste des parties prenantes")
st.caption("Cliquez sur une cellule pour la modifier. Pour supprimer une ligne, cochez-la à gauche puis "
           "utilisez l'icône corbeille. Les changements sont appliqués quand vous cliquez **Enregistrer**.")
df = pd.DataFrame([{"id": s.id, "Nom": s.name, "Profil": s.type, "Description": s.description}
                   for s in p.stakeholders], columns=["id", "Nom", "Profil", "Description"])
with st.form("stakeholders", border=False):
    edited = st.data_editor(
        df, num_rows="dynamic", hide_index=True, use_container_width=True,
        column_order=["Nom", "Profil", "Description"],
        column_config={"Nom": st.column_config.TextColumn(required=True, help="Nom unique"),
                       "Profil": st.column_config.SelectboxColumn(options=TYPES, default="Autre"),
                       "Description": st.column_config.TextColumn(width="large")})
    submitted = st.form_submit_button("Enregistrer les modifications", type="primary",
                                      icon=":material/save:")

if submitted:
    rows = edited.dropna(subset=["Nom"])
    rows = rows[rows["Nom"].astype(str).str.strip() != ""]
    names = rows["Nom"].astype(str).str.strip().str.lower()
    if names.duplicated().any():
        st.error("Deux parties prenantes ont le même nom. Chaque nom doit être unique.")
    else:
        old = {s.id: s for s in p.stakeholders}
        new = []
        for i, r in enumerate(rows.to_dict("records")):
            sid = r["id"] if isinstance(r["id"], str) and r["id"] in old else new_id("s")
            color = old[sid].color if sid in old else COLORS[i % len(COLORS)]
            profil = r["Profil"] if isinstance(r["Profil"], str) and r["Profil"] else "Autre"
            desc = "" if pd.isna(r["Description"]) else str(r["Description"])
            new.append(Stakeholder(sid, str(r["Nom"]).strip(), profil, desc, color))
        kept = {s.id for s in new}
        removed = len([f for f in p.flows if f.source not in kept or f.target not in kept])
        p.stakeholders = new
        p.flows = [f for f in p.flows if f.source in kept and f.target in kept]
        if p.focal not in kept:
            p.focal = new[0].id if new else None
        ui_state.touch()
        ui_state.flash("Parties prenantes enregistrées."
                       + (f" {removed} flux liés à des parties prenantes supprimées ont été retirés."
                          if removed else ""))
        st.rerun()

with st.expander("Nom et contexte du projet", icon=":material/edit:"):
    with st.form("project_meta", border=False):
        name = st.text_input("Nom du projet", p.name)
        desc = st.text_area("Contexte", p.description)
        if st.form_submit_button("Enregistrer"):
            p.name, p.description = name.strip() or p.name, desc
            ui_state.flash("Projet renommé.")
            st.rerun()

ui_state.footer_nav(STEP)
