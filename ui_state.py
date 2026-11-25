"""Fonctions partagées par les pages Streamlit : projet en cours, calculs mis en cache,
parcours guidé (étapes, en-têtes, navigation) et formats d'affichage."""

from __future__ import annotations

import streamlit as st

from svn_core import compute_all, examples, find_cycles, outside_cycles
from svn_core.model import Project

# --- Parcours ---------------------------------------------------------------
# (fichier de la page, titre, icône, phrase d'aide). L'ordre est celui de la démarche.
STEPS = [
    ("views/donnees.py", "Importer / exporter", ":material/upload_file:",
     "Chargez vos données (fichier CSV, TXT ou JSON) ou un exemple."),
    ("views/parties_prenantes.py", "Parties prenantes", ":material/groups:",
     "Vérifiez les acteurs du réseau et choisissez le projet central."),
    ("views/flux.py", "Flux de valeur", ":material/swap_horiz:",
     "Vérifiez les échanges de valeur entre acteurs et leurs scores."),
    ("views/reseau.py", "Carte du réseau", ":material/hub:",
     "Visualisez le réseau dessiné automatiquement."),
    ("views/cycles.py", "Cycles de valeur", ":material/autorenew:",
     "Lisez les chemins de valeur qui reviennent au projet central."),
    ("views/priorisation.py", "Priorisation", ":material/bar_chart:",
     "Classez les parties prenantes et les flux selon plusieurs indicateurs."),
]


def project() -> Project:
    """Projet en cours, gardé dans la session du navigateur."""
    if "project" not in st.session_state:
        st.session_state.project = examples.essai_de_jeu()
    return st.session_state.project


def set_project(p: Project) -> None:
    st.session_state.project = p
    touch()


def touch() -> None:
    """À appeler après toute modification du projet : les calculs seront refaits."""
    st.session_state.pop("results", None)
    st.session_state["dirty"] = True


def results():
    """(cycles, indicateurs) du projet en cours, recalculés seulement après une modification."""
    if "results" not in st.session_state:
        p = project()
        res = find_cycles(p)
        st.session_state.results = (res, compute_all(p, res))
    return st.session_state.results


# --- Formats ----------------------------------------------------------------
def fmt(x: float, d: int = 4) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def pct(x: float) -> str:
    return f"{100 * x:.1f} %".replace(".", ",")


# --- État d'avancement ------------------------------------------------------
def checklist() -> list[tuple[str, bool, str]]:
    """(tâche, faite ?, page où la faire)."""
    p = project()
    res, _ = results()
    return [("Définir au moins deux parties prenantes", len(p.stakeholders) >= 2, STEPS[1][0]),
            ("Choisir le projet central", p.stakeholder(p.focal) is not None, STEPS[1][0]),
            ("Créer des flux de valeur avec leur score", len(p.valid_flows()) > 0, STEPS[2][0]),
            ("Obtenir au moins un cycle complet", len(res.cycles) > 0, STEPS[2][0])]


def progress() -> float:
    items = checklist()
    return sum(done for _, done, _ in items) / len(items)


def next_action() -> tuple[str, str, str]:
    """(texte, page, icône) de la prochaine chose à faire."""
    for text, done, page in checklist():
        if not done:
            return text, page, ":material/arrow_forward:"
    return "Voir les résultats", STEPS[4][0], ":material/insights:"


# --- Mise en page -----------------------------------------------------------
def header(step: int, intro: str | None = None) -> None:
    """En-tête commun aux pages du parcours : numéro d'étape, titre, aide."""
    path, title, icon, help_text = STEPS[step]
    st.caption(f"Étape {step + 1} sur {len(STEPS)}")
    st.title(title)
    st.markdown(intro or help_text)


def footer_nav(step: int) -> None:
    """Liens « étape précédente / suivante » en bas de page."""
    st.divider()
    left, _, right = st.columns([2, 3, 2])
    if step > 0:
        path, title, icon, _ = STEPS[step - 1]
        left.page_link(path, label=f"Précédent : {title}", icon=":material/arrow_back:")
    if step < len(STEPS) - 1:
        path, title, icon, _ = STEPS[step + 1]
        right.page_link(path, label=f"Suivant : {title}", icon=":material/arrow_forward:")


def empty_state(message: str, page: str | None = None, label: str | None = None) -> None:
    """Message quand il n'y a rien à afficher, avec un lien vers ce qu'il faut faire."""
    with st.container(border=True):
        st.markdown(f":material/info: {message}")
        if page:
            st.page_link(page, label=label or "Y aller", icon=":material/arrow_forward:")


def outside_cycles_notice() -> None:
    """Signale les parties prenantes absentes de tous les cycles (leur WSO vaut 0)."""
    p = project()
    res, _ = results()
    out = outside_cycles(p, res)
    if not out:
        return
    lines = "\n".join(f"- **{p.name_of(sid)}** {reason}." for sid, reason in out)
    st.info(f"{len(out)} partie(s) prenante(s) n'apparaissent dans **aucun cycle**. Leur WSO vaut "
            f"donc 0, quels que soient les scores de leurs flux.\n\n{lines}\n\n"
            "Un cycle doit entrer dans chaque partie prenante qu'il traverse et en ressortir. "
            "Un acteur qui ne fait qu'émettre (par exemple des exigences) reste donc invisible pour "
            "les indicateurs fondés sur les cycles. L'influence moyenne, elle, le prend en compte.",
            icon=":material/visibility_off:")


# --- Messages après rechargement ------------------------------------------------
def flash(msg: str) -> None:
    """Message affiché après le rechargement de la page (st.rerun efface st.success)."""
    st.session_state.flash = msg


def show_flash() -> None:
    msg = st.session_state.pop("flash", None)
    if msg:
        st.toast(msg, icon=":material/check_circle:")


# --- Remplacement du projet, avec confirmation -----------------------------------
@st.dialog("Remplacer le projet actuel ?")
def confirm_replace(new_project: Project, message: str) -> None:
    st.markdown(f"Le projet **{project().name}** sera remplacé par **{new_project.name}**.")
    st.caption("Exportez d'abord le projet actuel en JSON si vous voulez le garder.")
    c1, c2 = st.columns(2)
    if c1.button("Remplacer", type="primary", use_container_width=True):
        set_project(new_project)
        st.session_state["dirty"] = False
        flash(message)
        st.rerun()
    if c2.button("Annuler", use_container_width=True):
        st.rerun()


def replace_project(new_project: Project, message: str) -> None:
    """Remplace directement si le projet actuel n'a pas été modifié, sinon demande confirmation."""
    if st.session_state.get("dirty"):
        confirm_replace(new_project, message)
    else:
        set_project(new_project)
        st.session_state["dirty"] = False
        flash(message)
        st.rerun()
