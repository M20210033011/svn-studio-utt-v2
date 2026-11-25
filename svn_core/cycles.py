"""Recherche des cycles de valeur autour du projet central.

Définition :

- un **cycle de valeur** est une suite de flux qui part du projet central,
  passe par d'autres parties prenantes **au plus une fois chacune** (cycle simple)
  et revient au projet central ;
- le **score d'un cycle** est le **produit** des scores de ses flux.

Exemple : Projet --0,57--> Population --0,33--> Mairie --0,57--> Projet
donne 0,57 × 0,33 × 0,57 = 0,107217.

Si deux flux différents relient les mêmes parties prenantes (flux parallèles),
chacun donne un cycle distinct.

Algorithme : exploration « meilleur d'abord » avec une file de priorité.
Comme tous les scores sont ≤ 1, un chemin ne peut que perdre de la valeur en
s'allongeant ; les cycles sortent donc de la file du plus fort au plus faible.
Si le réseau est trop grand, on s'arrête après ``max_cycles`` cycles : on garde
alors les plus importants, et ``truncated`` vaut ``True``.
"""

from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass

from .model import Flow, Project

DEFAULT_MAX_CYCLES = 12_000
MAX_FRONTIER = 2_000_000


@dataclass(frozen=True)
class Cycle:
    nodes: tuple[str, ...]   # identifiants, commence et finit par le projet central
    flows: tuple[Flow, ...]  # flux parcourus dans l'ordre
    score: float             # produit des scores des flux

    @property
    def length(self) -> int:
        return len(self.flows)


@dataclass
class CycleResult:
    cycles: list[Cycle]
    truncated: bool

    @property
    def total(self) -> float:
        """Somme des scores de tous les cycles (dénominateur de WSO, WOO, WIO)."""
        return sum(c.score for c in self.cycles)


def find_cycles(project: Project, max_cycles: int = DEFAULT_MAX_CYCLES) -> CycleResult:
    focal = project.focal
    if not focal or not project.stakeholder(focal):
        return CycleResult([], False)

    adjacency: dict[str, list[Flow]] = {s.id: [] for s in project.stakeholders}
    for f in project.valid_flows():
        adjacency[f.source].append(f)

    counter = itertools.count()  # départage les égalités dans la file (ordre d'insertion)
    # heapq est un tas minimum : on stocke -score pour sortir le plus grand d'abord.
    heap = [(-1.0, next(counter), False, focal, (focal,), ())]
    cycles: list[Cycle] = []
    truncated = False

    while heap:
        neg_score, _, done, current, nodes, flows = heapq.heappop(heap)
        score = -neg_score
        if done:
            cycles.append(Cycle(nodes, flows, score))
            if len(cycles) >= max_cycles:
                truncated = bool(heap)
                break
            continue
        for edge in adjacency.get(current, []):
            new_score = score * float(edge.score)
            if edge.target == focal:
                heapq.heappush(heap, (-new_score, next(counter), True, focal,
                                      nodes + (focal,), flows + (edge,)))
            elif edge.target not in nodes:
                if len(heap) >= MAX_FRONTIER:
                    truncated = True
                    continue
                heapq.heappush(heap, (-new_score, next(counter), False, edge.target,
                                      nodes + (edge.target,), flows + (edge,)))

    cycles.sort(key=lambda c: -c.score)
    return CycleResult(cycles, truncated)


def outside_cycles(project: Project, res: CycleResult) -> list[tuple[str, str]]:
    """Parties prenantes (hors projet central) qui n'apparaissent dans aucun cycle, avec la raison.

    Un cycle doit entrer dans chaque partie prenante qu'il traverse et en ressortir.
    Une partie prenante qui ne reçoit aucun flux, ou qui n'en émet aucun, ne peut donc
    appartenir à aucun cycle : son WSO vaut 0, quels que soient les scores de ses flux.
    C'est le cas, par exemple, d'un acteur qui ne fait qu'émettre des exigences.

    Renvoie une liste de couples (identifiant, raison).
    """
    if res.truncated:
        return []  # liste incomplète des cycles : on ne peut pas conclure
    flows = project.valid_flows()
    in_cycle = {n for c in res.cycles for n in c.nodes}
    out = []
    for s in project.stakeholders:
        if s.id == project.focal or s.id in in_cycle:
            continue
        receives = any(f.target == s.id for f in flows)
        emits = any(f.source == s.id for f in flows)
        if not receives and not emits:
            reason = "n'a aucun flux"
        elif not receives:
            reason = "ne reçoit aucun flux (elle ne fait qu'émettre)"
        elif not emits:
            reason = "n'émet aucun flux (elle ne fait que recevoir)"
        else:
            reason = "aucun chemin ne la relie au projet central dans les deux sens"
        out.append((s.id, reason))
    return out
