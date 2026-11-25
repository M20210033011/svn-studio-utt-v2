"""Moteur de calcul de SVN Studio, indépendant de l'interface.

Utilisable dans un notebook :

>>> from svn_core import examples, find_cycles, compute_all
>>> p = examples.essai_de_jeu()
>>> res = find_cycles(p)
>>> len(res.cycles)
6
"""

from . import comparaison, examples
from .cycles import Cycle, CycleResult, find_cycles, outside_cycles
from .metrics import METRICS, compute_all
from .model import Flow, Project, Stakeholder

__all__ = ["Project", "Stakeholder", "Flow", "Cycle", "CycleResult", "find_cycles",
           "compute_all", "METRICS", "examples", "outside_cycles", "comparaison"]
