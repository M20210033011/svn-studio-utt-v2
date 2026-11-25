"""Jeux de données de référence, utilisés par l'application et par les tests."""

from __future__ import annotations

from .model import COLORS, Flow, Project, Stakeholder


def _build(name, description, actors, flows, focal_name) -> Project:
    """actors = [(nom, profil, description)], flows = [(nom, source, cible, score, catégorie)]."""
    stakeholders = [Stakeholder(id=f"s{i}", name=n, type=t, description=d, color=COLORS[i % len(COLORS)])
                    for i, (n, t, d) in enumerate(actors)]
    ids = {s.name: s.id for s in stakeholders}
    fl = [Flow(id=f"f{i + 1}", source=ids[s], target=ids[t], name=n, score=sc, category=c)
          for i, (n, s, t, sc, c) in enumerate(flows)]
    return Project(name=name, description=description, focal=ids[focal_name],
                   stakeholders=stakeholders, flows=fl)


def essai_de_jeu() -> Project:
    """Exemple pédagogique : réseau de transport collectif (4 parties prenantes, 8 flux).

    """
    return _build(
        "SVN — Exemple pédagogique",
        "Exemple pédagogique : analyse d'un réseau de transport collectif réunissant quatre "
        "parties prenantes et huit flux de valeur.",
        [("Projet", "Projet central", "Projet de transport collectif chargé de coordonner le service."),
         ("Population", "Bénéficiaire", "Usagers et habitants bénéficiant du service."),
         ("Mairie", "Institution publique", "Administration municipale et décisions de financement."),
         ("Opérateurs", "Partenaire", "Exploitants responsables de la réalisation du service de transport.")],
        [("Qualité du service", "Projet", "Population", 0.57, "Performance"),
         ("Soutien et impôts", "Population", "Mairie", 0.33, "Économique"),
         ("Décision et financement", "Mairie", "Projet", 0.57, "Économique"),
         ("Passagers", "Projet", "Opérateurs", 0.44, "Social"),
         ("Investissement flotte", "Opérateurs", "Projet", 0.56, "Technologique"),
         ("Billets", "Population", "Opérateurs", 0.57, "Économique"),
         ("Respect du contrat", "Opérateurs", "Mairie", 0.19, "Gestion"),
         ("Subventions", "Mairie", "Opérateurs", 0.33, "Économique")],
        "Projet",
    )


EXAMPLES = {
    "Exemple pédagogique (transport collectif)": essai_de_jeu,
}
