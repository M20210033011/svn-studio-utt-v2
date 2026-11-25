"""Exemple pédagogique : résultats de référence, confirmés par l'outil MatrixPath.

Les valeurs attendues viennent des fichiers de résultats de MatrixPath 2.0
(FocalInfoCycle / FocalInfoVertex / FocalInfoEdge.Projet.Projet.4.txt).
"""
import pytest

from svn_core import compute_all, examples, find_cycles

MIT_CYCLES = [  # (noms des flux, score MatrixPath)
    (("Passagers", "Investissement flotte"), 0.24640000000000004),
    (("Qualité du service", "Billets", "Investissement flotte"), 0.181944),
    (("Qualité du service", "Soutien et impôts", "Décision et financement"), 0.10721699999999998),
    (("Passagers", "Respect du contrat", "Décision et financement"), 0.047652),
    (("Qualité du service", "Billets", "Respect du contrat", "Décision et financement"), 0.03518667),
    (("Qualité du service", "Soutien et impôts", "Subventions", "Investissement flotte"), 0.03476088),
]
MIT_WSO = {"Population": 0.5498013466979903, "Mairie": 0.34419799236190857,
           "Opérateurs": 0.8358489348445801}
MIT_WVFO = {"Qualité du service": 0.2014036281626795, "Soutien et impôts": 0.07962734429699746,
            "Décision et financement": 0.1065914512224477, "Passagers": 0.164917097263466,
            "Investissement flotte": 0.25972927420369785, "Billets": 0.12177628386568204,
            "Respect du contrat": 0.04645951395523976, "Subventions": 0.019495407029789524}


@pytest.fixture
def setup():
    p = examples.essai_de_jeu()
    res = find_cycles(p)
    return p, res, compute_all(p, res)


def test_six_cycles_identiques_a_matrixpath(setup):
    _, res, _ = setup
    assert not res.truncated
    got = [(tuple(f.name for f in c.flows), c.score) for c in res.cycles]
    assert len(got) == 6
    for (names, score), (exp_names, exp_score) in zip(got, MIT_CYCLES):
        assert names == exp_names
        assert score == pytest.approx(exp_score, abs=1e-12)


def test_somme_des_scores(setup):
    assert setup[1].total == pytest.approx(0.65316055, abs=1e-12)


def test_wso_identique_a_matrixpath(setup):
    rows = {r.name: r.value for r in setup[2]["WSO"]}
    assert rows == pytest.approx(MIT_WSO, abs=1e-12)


def test_wvfo_identique_a_matrixpath(setup):
    rows = {r.name: r.value for r in setup[2]["WVFO"]}
    assert rows == pytest.approx(MIT_WVFO, abs=1e-12)
    assert sum(rows.values()) == pytest.approx(1.0)


def test_woo_wio(setup):
    woo = {r.name: r.value for r in setup[2]["WOO"]}
    wio = {r.name: r.value for r in setup[2]["WIO"]}
    total = 0.65316055
    assert woo["Passagers"] == pytest.approx((0.2464 + 0.047652) / total)
    assert woo["Qualité du service"] == pytest.approx(1 - woo["Passagers"])
    assert wio["Investissement flotte"] == pytest.approx((0.2464 + 0.181944 + 0.03476088) / total)
    assert sum(woo.values()) == pytest.approx(1.0)
    assert sum(wio.values()) == pytest.approx(1.0)


def test_influence_moyenne(setup):
    emis = {r.name: r.value for r in setup[2]["INFLUENCE_EMIS"]}
    recus = {r.name: r.value for r in setup[2]["INFLUENCE_RECUS"]}
    glob = {r.name: r.value for r in setup[2]["INFLUENCE_GLOBAL"]}
    # flux émis par le Projet : 0,57 et 0,44 ; reçus : 0,57 et 0,56
    assert emis["Projet"] == pytest.approx((0.57 + 0.44) / 2)
    assert recus["Projet"] == pytest.approx((0.57 + 0.56) / 2)
    assert glob["Projet"] == pytest.approx((0.57 + 0.44 + 0.57 + 0.56) / 4)
    # Opérateurs émettent 0,56 et 0,19 ; reçoivent 0,44, 0,57 et 0,33
    assert emis["Opérateurs"] == pytest.approx(0.375)
    assert recus["Opérateurs"] == pytest.approx((0.44 + 0.57 + 0.33) / 3)
    assert glob["Opérateurs"] == pytest.approx((0.56 + 0.19 + 0.44 + 0.57 + 0.33) / 5)
