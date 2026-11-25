import pandas as pd
import streamlit as st

import ui_state
from svn_core.model import CATEGORIES, Flow, is_valid_score, new_id

STEP = 2
p = ui_state.project()
ui_state.header(STEP, "Les **flux de valeur** sont les flèches du réseau. Un flux `Source → Cible` "
                "signifie que la source **fournit** une valeur à la cible (argent, information, service, "
                "soutien…). Le **score**, entre 0 et 1, mesure l'importance de cette valeur pour la cible.")

if len(p.stakeholders) < 2:
    ui_state.empty_state("Il faut au moins deux parties prenantes avant de créer des flux.",
                         ui_state.STEPS[1][0], "Aller aux parties prenantes")
    ui_state.footer_nav(STEP)
    st.stop()

names = [s.name for s in p.stakeholders]
by_name = {s.name: s.id for s in p.stakeholders}

# --- Ajout rapide -----------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### :material/add_link: Ajouter un flux")
    with st.form("add_flow", clear_on_submit=True, border=False):
        c1, c2, c3 = st.columns([2, 2, 3])
        src = c1.selectbox("Source (fournit)", names, index=None, placeholder="Choisir…")
        dst = c2.selectbox("Cible (reçoit)", names, index=None, placeholder="Choisir…")
        fname = c3.text_input("Nom du flux", placeholder="ex. Subventions")
        c4, c5, c6 = st.columns([3, 2, 2])
        score = c4.slider("Score", 0.0, 1.0, 0.5, 0.01,
                          help="Importance de cette valeur pour la cible : 0 = aucune, 1 = essentielle.")
        cat = c5.selectbox("Catégorie", CATEGORIES, index=CATEGORIES.index("Autre"))
        c6.markdown("&nbsp;")
        ok = c6.form_submit_button("Ajouter le flux", type="primary", use_container_width=True)
    if ok:
        if not src or not dst or not fname.strip():
            st.error("Choisissez une source, une cible et donnez un nom au flux.")
        elif src == dst:
            st.error("La source et la cible doivent être différentes.")
        else:
            p.flows.append(Flow(new_id("f"), by_name[src], by_name[dst], fname.strip(), score, cat))
            ui_state.touch()
            ui_state.flash(f"Flux « {fname.strip()} » ajouté.")
            st.rerun()

    with st.expander("Aide au choix du score (deux questions)", icon=":material/calculate:"):
        st.caption("Score proposé = bénéfice × préjudice si le flux manque, sur cinq niveaux. "
                   "C'est une aide à la saisie, pas une méthode de questionnaire.")
        a, b, c = st.columns([2, 2, 1])
        ben = a.select_slider("Bénéfice pour la cible", [0.11, 0.19, 0.33, 0.57, 0.98], value=0.57,
                              format_func=lambda v: {0.11: "très faible", 0.19: "faible", 0.33: "moyen",
                                                     0.57: "fort", 0.98: "très fort"}[v])
        harm = b.select_slider("Préjudice si le flux manque", [0.11, 0.33, 0.55, 0.78, 0.98], value=0.55,
                               format_func=lambda v: {0.11: "très faible", 0.33: "faible", 0.55: "moyen",
                                                      0.78: "fort", 0.98: "très fort"}[v])
        c.metric("Score", ui_state.fmt(ben * harm, 2))

# --- Tableau éditable ---------------------------------------------------------------
st.markdown("#### Liste des flux")
st.caption("Modifiez directement les cellules, puis cliquez **Enregistrer**. Une ligne incorrecte "
           "bloque l'enregistrement et le message indique laquelle.")
cat_filter = st.pills("Filtrer par catégorie", CATEGORIES, selection_mode="multi", key="flow_cat_filter")
df = pd.DataFrame([{"id": f.id, "Source": p.name_of(f.source), "Cible": p.name_of(f.target),
                    "Nom du flux": f.name, "Score": float(f.score), "Catégorie": f.category,
                    "Description": f.description} for f in p.flows],
                  columns=["id", "Source", "Cible", "Nom du flux", "Score", "Catégorie", "Description"])
hidden = pd.DataFrame(columns=df.columns)
if cat_filter:
    hidden = df[~df["Catégorie"].isin(cat_filter)]
    df = df[df["Catégorie"].isin(cat_filter)]
    st.caption(f"{len(df)} flux affichés sur {len(df) + len(hidden)}. Les flux masqués ne sont pas modifiés.")

with st.form("flows", border=False):
    edited = st.data_editor(
        df, num_rows="dynamic", hide_index=True, use_container_width=True,
        column_order=["Source", "Cible", "Nom du flux", "Score", "Catégorie", "Description"],
        column_config={
            "Source": st.column_config.SelectboxColumn(options=names, required=True, help="Qui fournit"),
            "Cible": st.column_config.SelectboxColumn(options=names, required=True, help="Qui reçoit"),
            "Nom du flux": st.column_config.TextColumn(required=True),
            "Score": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.01,
                                                   format="%.2f", required=True, help="Entre 0 et 1"),
            "Catégorie": st.column_config.SelectboxColumn(options=CATEGORIES, default="Autre"),
        })
    submitted = st.form_submit_button("Enregistrer les modifications", type="primary",
                                      icon=":material/save:")

if submitted:
    errors, new = [], []
    old = {f.id: f for f in p.flows}
    for n, r in enumerate(edited.to_dict("records"), start=1):
        src, dst, name, score = r["Source"], r["Cible"], r["Nom du flux"], r["Score"]
        name = "" if pd.isna(name) else str(name).strip()
        if (pd.isna(src) or src == "") and (pd.isna(dst) or dst == "") and not name:
            continue  # ligne vide
        if src not in by_name or dst not in by_name or not name:
            errors.append(f"Ligne {n} : source, cible et nom sont obligatoires.")
            continue
        if src == dst:
            errors.append(f"Ligne {n} : la source et la cible doivent être différentes.")
            continue
        if not is_valid_score(score):
            errors.append(f"Ligne {n} : le score doit être compris entre 0 et 1.")
            continue
        fid = r["id"] if isinstance(r["id"], str) and r["id"] in old else new_id("f")
        cat = r["Catégorie"] if r["Catégorie"] in CATEGORIES else "Autre"
        desc = "" if pd.isna(r["Description"]) else str(r["Description"])
        new.append(Flow(fid, by_name[src], by_name[dst], name, float(score), cat, desc))
    if errors:
        st.error("Rien n'a été enregistré :\n\n" + "\n\n".join(errors), icon=":material/error:")
    else:
        kept_hidden = [old[i] for i in hidden["id"] if i in old]
        p.flows = new + kept_hidden
        ui_state.touch()
        ui_state.flash(f"{len(p.flows)} flux enregistrés.")
        st.rerun()

ui_state.footer_nav(STEP)
