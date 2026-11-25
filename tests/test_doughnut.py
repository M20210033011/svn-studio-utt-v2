"""Premiers tests d'intégration du Doughnut dans le réseau partiel de référence.

Scénarios (fichiers dans ``data/examples/doughnut/``) :

- T0 : réseau partiel de référence (6 parties prenantes, 15 flux), sans Doughnut ;
- T1 : un nœud « Doughnut » émet 6 exigences notées 0,96 ;
- T2 : « Plancher social » et « Plafond écologique » émettent chacun 3 de ces exigences ;
- T1 bis et T2 bis : expérience complémentaire, avec un retour du projet focal
  vers le Doughnut (ou vers chacun des deux nœuds), noté 0,96.

Les valeurs attendues ont été vérifiées par un calcul indépendant (recherche des
cycles en profondeur, sans ``svn_core``).
"""
import json
from pathlib import Path

import pytest

from reference_network import REFERENCE_PATHS, reference_network
from svn_core import compute_all, find_cycles, outside_cycles
from svn_core import io as svn_io
from svn_core.comparaison import Scenario, compare_critical_paths, compare_indicator

DIR = Path(__file__).resolve().parents[1] / "data" / "examples" / "doughnut"
FILES = {"T0": "T0_base.json", "T1": "T1_doughnut_global.json", "T2": "T2_doughnut_2_noeuds.json",
         "T1bis": "T1_doughnut_global_retour.json", "T2bis": "T2_doughnut_2_noeuds_retour.json"}
DOUGHNUT = {"T0": [], "T1": ["Doughnut"], "T2": ["Plancher social", "Plafond écologique"]}
DOUGHNUT["T1bis"], DOUGHNUT["T2bis"] = DOUGHNUT["T1"], DOUGHNUT["T2"]

WSO_PEREIRA = {"Local government": 0.725, "Population": 0.675, "Press": 0.347,
               "Bus operators": 0.275, "Judiciary": 0.189}
RECUS = {"T0": {"Judiciary": 0.960, "Bus operators": 0.600, "Improvements": 0.592,
                "Local government": 0.3775, "Population": 0.560, "Press": 0.560},
         "T1": {"Judiciary": 0.960, "Bus operators": 0.780, "Improvements": 0.697,
                "Local government": 0.572, "Population": 0.560, "Press": 0.560}}
RECUS["T2"] = RECUS["T1"]
EMIS_PEREIRA = {"Local government": 0.827, "Population": 0.587, "Judiciary": 0.560,
                "Bus operators": 0.440, "Press": 0.440, "Improvements": 0.4375}


def load(t):
    return svn_io.load_json((DIR / FILES[t]).read_text(encoding="utf-8"))


def run(t):
    p = load(t)
    res = find_cycles(p)
    return p, res, compute_all(p, res)


def values(rows):
    return {r.name: r.value for r in rows}


def paths(res, n=None):
    cycles = res.cycles if n is None else res.cycles[:n]
    return [tuple(f.name for f in c.flows) for c in cycles]


# --- T0 est bien le réseau de référence ---------------------------------------------
def test_t0_identique_au_reseau_de_reference():
    a, b = load("T0"), reference_network()
    key = lambda p: sorted((p.name_of(f.source), p.name_of(f.target), f.name, f.score) for f in p.flows)
    assert key(a) == key(b)


# --- Chemins de valeur : T0, T1 et T2 --------------------------------------------------
@pytest.mark.parametrize("t", ["T0", "T1", "T2"])
def test_cycles_inchanges(t):
    _, res, _ = run(t)
    assert len(res.cycles) == 24
    assert round(res.cycles[0].score, 4) == 0.3011
    assert set(paths(res, 10)) == set(REFERENCE_PATHS)
    assert paths(res) == paths(find_cycles(reference_network()))


@pytest.mark.parametrize("t", ["T0", "T1", "T2"])
def test_wso(t):
    p, _, m = run(t)
    wso = values(m["WSO"])
    for name, v in WSO_PEREIRA.items():
        assert wso[name] == pytest.approx(v, abs=5e-4), name
    for name in DOUGHNUT[t]:
        assert wso[name] == 0.0


@pytest.mark.parametrize("t", ["T1", "T2"])
def test_doughnut_hors_cycles(t):
    p, res, _ = run(t)
    out = {p.name_of(sid): reason for sid, reason in outside_cycles(p, res)}
    assert set(out) == set(DOUGHNUT[t])
    assert all("ne reçoit aucun flux" in r for r in out.values())


def test_aucun_acteur_hors_cycles_dans_t0():
    p, res, _ = run("T0")
    assert outside_cycles(p, res) == []


# --- Influence moyenne (méthode de Lalevée) --------------------------------------------
@pytest.mark.parametrize("t", ["T0", "T1", "T2"])
def test_influence_emise(t):
    _, _, m = run(t)
    rows = m["INFLUENCE_EMIS"]
    emis = values(rows)
    for name, v in EMIS_PEREIRA.items():
        assert emis[name] == pytest.approx(v, abs=5e-4), name
    for name in DOUGHNUT[t]:
        assert emis[name] == pytest.approx(0.96)
    # le ou les nœuds Doughnut occupent les premières places
    assert {r.name for r in rows[:len(DOUGHNUT[t])]} == set(DOUGHNUT[t])


@pytest.mark.parametrize("t", ["T0", "T1", "T2"])
def test_influence_recue(t):
    _, _, m = run(t)
    recus = values(m["INFLUENCE_RECUS"])
    for name, v in RECUS[t].items():
        assert recus[name] == pytest.approx(v, abs=5e-4), name


def test_t1_egal_t2_pour_les_acteurs_du_reseau_de_reference():
    _, _, m1 = run("T1")
    _, _, m2 = run("T2")
    pereira = set(EMIS_PEREIRA)
    for key in m1:
        v1 = {k: v for k, v in values(m1[key]).items() if k in pereira}
        v2 = {k: v for k, v in values(m2[key]).items() if k in pereira}
        assert v1 == pytest.approx(v2), key


# --- Expérience complémentaire : retour vers le Doughnut ------------------------------
@pytest.mark.parametrize("t", ["T1bis", "T2bis"])
def test_retour(t):
    p, res, m = run(t)
    assert len(res.cycles) == 36
    assert round(res.cycles[0].score, 4) == 0.9216            # Improvements → Doughnut → Improvements
    wso = values(m["WSO"])
    expected = 0.673 if t == "T1bis" else 0.336
    for name in DOUGHNUT[t]:
        assert wso[name] == pytest.approx(expected, abs=5e-4), name
    # le Doughnut est dans les 10 meilleurs cycles, qui ne sont plus ceux de la référence
    ids = {s.id for s in p.stakeholders if s.name in DOUGHNUT[t]}
    assert all(ids & set(c.nodes) for c in res.cycles[:10])
    assert not set(paths(res, 10)) & set(REFERENCE_PATHS)
    assert outside_cycles(p, res) == []


# --- Module de comparaison ---------------------------------------------------------------
def test_comparaison_t0_t1():
    a, b = Scenario.of(load("T0")), Scenario.of(load("T1"))
    rows = {r["Élément"]: r for r in compare_indicator(a, b, "INFLUENCE_RECUS")}
    assert rows["Bus operators"]["A"] == pytest.approx(0.600)
    assert rows["Bus operators"]["B"] == pytest.approx(0.780)
    assert rows["Bus operators"]["Écart (B − A)"] == pytest.approx(0.180)
    assert rows["Doughnut"]["A"] is None and rows["Doughnut"]["Écart (B − A)"] is None
    cp = compare_critical_paths(a, b)
    assert len(cp) == 10 and all(r["Rang A"] == r["Rang B"] for r in cp)


def test_fichiers_json_valides():
    for f in FILES.values():
        d = json.loads((DIR / f).read_text(encoding="utf-8"))
        assert d["focal"] == "s1" and all(0 <= x["score"] <= 1 for x in d["flows"])
