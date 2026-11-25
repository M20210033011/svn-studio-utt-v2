"""Comparaison de deux scénarios d'un même réseau (par exemple avec et sans Doughnut).

Les deux projets sont des fichiers distincts : leurs identifiants internes peuvent
différer. Les parties prenantes et les flux sont donc rapprochés par leur **nom**
(sans tenir compte des majuscules ni des espaces en début ou fin).

Aucun nouveau calcul n'est introduit : on réutilise ``find_cycles`` et ``compute_all``
sur chaque scénario, puis on met les valeurs côte à côte.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cycles import CycleResult, find_cycles
from .metrics import compute_all
from .model import Project


@dataclass
class Scenario:
    project: Project
    cycles: CycleResult
    metrics: dict

    @classmethod
    def of(cls, project: Project) -> "Scenario":
        res = find_cycles(project)
        return cls(project, res, compute_all(project, res))


def _key(name: str) -> str:
    return name.strip().lower()


def summary(sc: Scenario) -> dict:
    """Chiffres clés d'un scénario."""
    res = sc.cycles
    return {
        "Parties prenantes": len(sc.project.stakeholders),
        "Flux": len(sc.project.valid_flows()),
        "Cycles": len(res.cycles),
        "Meilleur cycle": res.cycles[0].score if res.cycles else 0.0,
        "Somme des scores des cycles": res.total,
    }


def compare_indicator(a: Scenario, b: Scenario, key: str) -> list[dict]:
    """Valeurs d'un indicateur dans les deux scénarios, élément par élément.

    ``key`` est une clé de ``METRICS`` (WSO, INFLUENCE_EMIS, ...). Un élément présent
    dans un seul scénario a la valeur ``None`` dans l'autre (« absent »).
    L'ordre suit le scénario A, puis les éléments propres au scénario B.
    """
    va = {_key(r.name): r for r in a.metrics[key]}
    vb = {_key(r.name): r for r in b.metrics[key]}
    order = list(va) + [k for k in vb if k not in va]
    rows = []
    for k in order:
        ra, rb = va.get(k), vb.get(k)
        x = ra.value if ra else None
        y = rb.value if rb else None
        rows.append({"Élément": (ra or rb).name, "A": x, "B": y,
                     "Écart (B − A)": (y - x) if x is not None and y is not None else None})
    return rows


def path_names(sc: Scenario, n: int | None = 10) -> list[tuple[str, ...]]:
    """Les ``n`` meilleurs cycles, chacun décrit par la suite des noms de ses flux."""
    cycles = sc.cycles.cycles if n is None else sc.cycles.cycles[:n]
    return [tuple(f.name for f in c.flows) for c in cycles]


def compare_critical_paths(a: Scenario, b: Scenario, n: int = 10) -> list[dict]:
    """Rang des ``n`` premiers cycles de chaque scénario, et leur rang dans l'autre scénario."""
    all_a, all_b = path_names(a, None), path_names(b, None)
    score_a = {p: c.score for p, c in zip(all_a, a.cycles.cycles)}
    score_b = {p: c.score for p, c in zip(all_b, b.cycles.cycles)}
    rank_a = {p: i + 1 for i, p in enumerate(all_a)}
    rank_b = {p: i + 1 for i, p in enumerate(all_b)}
    wanted = all_a[:n] + [p for p in all_b[:n] if p not in set(all_a[:n])]
    return [{"Cycle (flux)": " | ".join(p),
             "Rang A": rank_a.get(p), "Score A": score_a.get(p),
             "Rang B": rank_b.get(p), "Score B": score_b.get(p)} for p in wanted]
