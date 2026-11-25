"""Jeu de données de référence externe, utilisé seulement pour la validation automatique.

Réseau partiel (6 parties prenantes, 15 flux) reconstruit à partir des 10 chemins
critiques publiés dans un article de la littérature SVN. Il n'apparaît pas dans
l'application ; il sert à vérifier que le calcul des cycles retrouve un résultat publié.
"""

from svn_core.examples import _build
from svn_core.model import Project

def reference_network() -> Project:
    """Réseau partiel reconstruit à partir des 10 chemins critiques publiés.

    La publication ne donne pas tous ses flux : on reconstruit seulement les 15 flux
    qui composent les 10 chemins critiques, avec les scores publiés.
    """
    return _build(
        "Réseau de référence — réseau partiel",
        "Reconstruction des 10 chemins critiques publiés (6 parties prenantes, 15 flux).",
        [("Improvements", "Projet central", "Improvements in Public Transportation (projet focal)."),
         ("Population", "Bénéficiaire", "Usagers et habitants."),
         ("Local government", "Institution publique", "Gouvernement local."),
         ("Bus operators", "Partenaire", "Opérateurs de bus."),
         ("Judiciary", "Régulateur", "Pouvoir judiciaire."),
         ("Press", "Autre", "Presse.")],
        [("Better quality", "Improvements", "Population", 0.56, "Performance"),
         ("Taxes", "Population", "Local government", 0.56, "Économique"),
         ("Political support", "Population", "Local government", 0.44, "Social"),
         ("Increased fare revenues", "Population", "Bus operators", 0.76, "Économique"),
         ("Decision making", "Local government", "Improvements", 0.96, "Gestion"),
         ("Funding for infrastructure", "Local government", "Improvements", 0.56, "Économique"),
         ("Competitive tendering", "Local government", "Judiciary", 0.96, "Gestion"),
         ("Enforcement", "Judiciary", "Improvements", 0.56, "Gestion"),
         ("Attracting passengers", "Improvements", "Bus operators", 0.44, "Social"),
         ("Funds for fleet and technology", "Bus operators", "Improvements", 0.56, "Technologique"),
         ("Political support (operators)", "Bus operators", "Improvements", 0.32, "Social"),
         ("Improved political capital", "Improvements", "Local government", 0.19, "Social"),
         ("Project information", "Improvements", "Press", 0.56, "Autre"),
         ("Public opinion", "Press", "Local government", 0.32, "Social"),
         ("Information on changes", "Press", "Population", 0.56, "Autre")],
        "Improvements",
    )


# Les 10 chemins critiques publiés :
# suite des noms de flux -> (nom du chemin, score publié).
REFERENCE_PATHS = {
    ("Better quality", "Taxes", "Decision making"): ("CP1", 0.3011),
    ("Attracting passengers", "Funds for fleet and technology"): ("CP2", 0.2464),
    ("Better quality", "Increased fare revenues", "Funds for fleet and technology"): ("CP3", 0.2383),
    ("Better quality", "Political support", "Decision making"): ("CP4", 0.2365),
    ("Better quality", "Taxes", "Funding for infrastructure"): ("CP5", 0.1824),
    ("Improved political capital", "Decision making"): ("CP6", 0.1756),
    ("Project information", "Public opinion", "Decision making"): ("CP7", 0.1720),
    ("Project information", "Information on changes", "Taxes", "Decision making"): ("CP8", 0.1686),
    ("Better quality", "Taxes", "Competitive tendering", "Enforcement"): ("CP9", 0.1686),
    ("Attracting passengers", "Political support (operators)"): ("CP10", 0.1408),
}

