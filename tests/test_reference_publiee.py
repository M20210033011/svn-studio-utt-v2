"""Validation : retrouver les 10 chemins critiques d'un réseau de référence publié.

Écart connu et documenté : les scores de CP5 et CP6 sont inversés par rapport à
la publication (0,1756 calculé pour CP5 contre 0,1824 publié, et l'inverse pour CP6).
Le calcul 0,56 × 0,56 × 0,56 = 0,1756 et 0,19 × 0,96 = 0,1824 montre que
l'inversion vient des étiquettes de la publication, pas de l'outil.
"""
import pytest

from reference_network import REFERENCE_PATHS, reference_network
from svn_core import find_cycles

KNOWN_SWAP = {"CP5": 0.1756, "CP6": 0.1824}


def test_les_10_premiers_cycles_sont_les_10_chemins_critiques():
    res = find_cycles(reference_network())
    top10 = [tuple(f.name for f in c.flows) for c in res.cycles[:10]]
    assert set(top10) == set(REFERENCE_PATHS)


def test_scores_publies():
    res = find_cycles(reference_network())
    by_path = {tuple(f.name for f in c.flows): c.score for c in res.cycles}
    for path, (cp, published) in REFERENCE_PATHS.items():
        expected = KNOWN_SWAP.get(cp, published)
        assert round(by_path[path], 4) == pytest.approx(expected, abs=1e-4), cp


def test_nombre_de_cycles_du_reseau_partiel():
    assert len(find_cycles(reference_network()).cycles) == 24
