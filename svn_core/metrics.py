"""Indicateurs de priorisation.

Deux familles d'indicateurs, qui ne répondent pas à la même question :

1. **Indicateurs fondés sur les cycles**.
   Ils mesurent la part du score cumulé des cycles qui passe par un élément.
   Notons ``C`` l'ensemble des cycles et ``s(c)`` le score d'un cycle.

   - WSO (Weighted Stakeholder Occurrence), pour une partie prenante ``v`` ≠ projet central :
     ``WSO(v) = Σ s(c) pour les cycles c qui passent par v  /  Σ s(c) sur tous les cycles``
   - WOO (Weighted Output Occurrence), pour un flux ``e`` qui SORT du projet central :
     ``WOO(e) = Σ s(c) pour les cycles dont e est le premier flux  /  Σ s(c)``
   - WIO (Weighted Input Occurrence), pour un flux ``e`` qui ENTRE dans le projet central :
     ``WIO(e) = Σ s(c) pour les cycles dont e est le dernier flux  /  Σ s(c)``
   - WVFO (Weighted Value Flow Occurrence), pour tout flux ``e`` :
     ``WVFO(e) = Σ s(c) pour les cycles contenant e  /  Σ_e' Σ s(c) pour les cycles contenant e'``
     (le dénominateur est donc Σ s(c) × longueur(c), et les WVFO somment à 1).

2. **Influence moyenne** : moyenne arithmétique des scores des flux d'une partie
   prenante, calculée directement sur les flux, **sans les cycles**.

   - ``émis``  : moyenne des scores des flux qui SORTENT de la partie prenante ;
   - ``reçus`` : moyenne des scores des flux qui ENTRENT dans la partie prenante ;
   - ``global``: moyenne des scores de tous les flux émis ET reçus (chaque flux compte une fois).

   Une partie prenante sans flux du type considéré reçoit 0 par convention.
   Le projet central est inclus dans ce classement.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cycles import CycleResult
from .model import Project


@dataclass
class Row:
    id: str
    name: str
    value: float
    count: int | None = None     # nombre de flux pris en compte (influence moyenne)
    total: float | None = None   # somme des scores (influence moyenne)


def _ratio(num: float, den: float) -> float:
    return num / den if den else 0.0


def _sorted(rows: list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r: -r.value)


def wso(project: Project, res: CycleResult) -> list[Row]:
    total = res.total
    return _sorted([
        Row(s.id, s.name, _ratio(sum(c.score for c in res.cycles if s.id in c.nodes[:-1]), total))
        for s in project.stakeholders if s.id != project.focal
    ])


def woo(project: Project, res: CycleResult) -> list[Row]:
    total = res.total
    return _sorted([
        Row(f.id, f.name, _ratio(sum(c.score for c in res.cycles if c.flows[0].id == f.id), total))
        for f in project.valid_flows() if f.source == project.focal
    ])


def wio(project: Project, res: CycleResult) -> list[Row]:
    total = res.total
    return _sorted([
        Row(f.id, f.name, _ratio(sum(c.score for c in res.cycles if c.flows[-1].id == f.id), total))
        for f in project.valid_flows() if f.target == project.focal
    ])


def wvfo(project: Project, res: CycleResult) -> list[Row]:
    flows = project.valid_flows()
    sums = {f.id: sum(c.score for c in res.cycles if any(x.id == f.id for x in c.flows))
            for f in flows}
    den = sum(sums.values())
    return _sorted([Row(f.id, f.name, _ratio(sums[f.id], den)) for f in flows])


def _influence(project: Project, mode: str) -> list[Row]:
    flows = project.valid_flows()
    rows = []
    for s in project.stakeholders:
        if mode == "emis":
            sel = [f for f in flows if f.source == s.id]
        elif mode == "recus":
            sel = [f for f in flows if f.target == s.id]
        else:
            sel = [f for f in flows if f.source == s.id or f.target == s.id]
        tot = sum(float(f.score) for f in sel)
        rows.append(Row(s.id, s.name, _ratio(tot, len(sel)), count=len(sel), total=tot))
    return _sorted(rows)


def influence_emis(project: Project) -> list[Row]:
    return _influence(project, "emis")


def influence_recus(project: Project) -> list[Row]:
    return _influence(project, "recus")


def influence_global(project: Project) -> list[Row]:
    return _influence(project, "global")


METRICS = {
    "WSO": {
        "title": "WSO · Importance des parties prenantes",
        "question": "Quelle part du score cumulé des cycles passe par chaque partie prenante "
                    "(hors projet central) ?",
        "formula": "Somme des scores des cycles passant par la partie prenante ÷ somme des scores de tous les cycles",
        "unit": "pct", "cycles": True,
    },
    "WOO": {
        "title": "WOO · Sorties cruciales du projet",
        "question": "Quels flux émis par le projet central ouvrent les cycles les plus importants ?",
        "formula": "Somme des scores des cycles qui commencent par ce flux ÷ somme des scores de tous les cycles",
        "unit": "pct", "cycles": True,
    },
    "WIO": {
        "title": "WIO · Entrées cruciales du projet",
        "question": "Quels flux reçus par le projet central ferment les cycles les plus importants ?",
        "formula": "Somme des scores des cycles qui finissent par ce flux ÷ somme des scores de tous les cycles",
        "unit": "pct", "cycles": True,
    },
    "WVFO": {
        "title": "WVFO · Importance des flux de valeur",
        "question": "Quels flux apparaissent le plus dans les cycles importants ?",
        "formula": "Somme des scores des cycles contenant ce flux ÷ somme de ces sommes pour tous les flux",
        "unit": "pct", "cycles": True,
    },
    "INFLUENCE_EMIS": {
        "title": "Influence moyenne · flux émis",
        "question": "En moyenne, quelle valeur une partie prenante fournit-elle aux autres ?",
        "formula": "Somme des scores des flux émis ÷ nombre de flux émis",
        "unit": "num", "cycles": False,
    },
    "INFLUENCE_RECUS": {
        "title": "Influence moyenne · flux reçus",
        "question": "En moyenne, quelle valeur une partie prenante reçoit-elle des autres ?",
        "formula": "Somme des scores des flux reçus ÷ nombre de flux reçus",
        "unit": "num", "cycles": False,
    },
    "INFLUENCE_GLOBAL": {
        "title": "Influence moyenne · flux émis et reçus",
        "question": "En moyenne, quelle est la valeur de tous les échanges d'une partie prenante ?",
        "formula": "Somme des scores des flux émis et reçus ÷ nombre total de ces flux",
        "unit": "num", "cycles": False,
    },
}


def compute_all(project: Project, res: CycleResult) -> dict[str, list[Row]]:
    return {
        "WSO": wso(project, res),
        "WOO": woo(project, res),
        "WIO": wio(project, res),
        "WVFO": wvfo(project, res),
        "INFLUENCE_EMIS": influence_emis(project),
        "INFLUENCE_RECUS": influence_recus(project),
        "INFLUENCE_GLOBAL": influence_global(project),
    }
