import json

import pytest

from svn_core import Flow, Project, Stakeholder, compute_all, examples, find_cycles
from svn_core import io as svn_io
from reference_network import reference_network


def two_nodes(flows):
    p = Project(name="t", focal="a", stakeholders=[Stakeholder("a", "A"), Stakeholder("b", "B")])
    p.flows = [Flow(f"f{i}", s, t, f"n{i}", sc) for i, (s, t, sc) in enumerate(flows)]
    return p


def test_flux_paralleles_donnent_deux_cycles():
    p = two_nodes([("a", "b", 0.5), ("a", "b", 0.4), ("b", "a", 1.0)])
    assert sorted(c.score for c in find_cycles(p).cycles) == [0.4, 0.5]


def test_sans_cycle_influence_reste_calculable():
    p = two_nodes([("a", "b", 0.5)])
    res = find_cycles(p)
    m = compute_all(p, res)
    assert res.cycles == [] and res.total == 0
    assert all(r.value == 0 for r in m["WSO"] + m["WVFO"])
    assert {r.name: r.value for r in m["INFLUENCE_EMIS"]} == {"A": 0.5, "B": 0.0}
    assert {r.name: r.value for r in m["INFLUENCE_RECUS"]} == {"A": 0.0, "B": 0.5}


def test_scores_nuls_sans_division_par_zero():
    p = two_nodes([("a", "b", 0.0), ("b", "a", 0.0)])
    m = compute_all(p, find_cycles(p))
    assert all(r.value == 0 for rows in m.values() for r in rows)


def test_direction_compte():
    p = two_nodes([("a", "b", 0.5), ("a", "b", 0.5)])
    assert find_cycles(p).cycles == []


def test_flux_invalides_ignores():
    p = two_nodes([("a", "b", 1.5), ("b", "a", 0.5), ("a", "zz", 0.5)])
    assert len(p.valid_flows()) == 1


def test_troncature():
    p = reference_network()
    res = find_cycles(p, max_cycles=5)
    assert res.truncated and len(res.cycles) == 5
    full = find_cycles(p)
    assert [c.score for c in res.cycles] == [c.score for c in full.cycles[:5]]


def test_json_aller_retour():
    p = examples.essai_de_jeu()
    q = svn_io.load_json(svn_io.dump_json(p))
    assert q.to_dict() == p.to_dict()


def test_json_invalide():
    d = examples.essai_de_jeu().to_dict()
    d["flows"][0]["score"] = 2
    with pytest.raises(ValueError):
        svn_io.load_json(json.dumps(d))


def test_csv_import_accents_virgule_decimale():
    p = Project(name="csv")
    txt = "﻿origine;destination;nom;score;catégorie\nÉtat;Région;Aide;0,5;Économique\nRégion;État;Retour;0.25;X\nA;A;boucle;0.3;\n"
    added, skipped = svn_io.import_flows_csv(p, txt)
    assert (added, skipped) == (2, 1)
    assert [s.name for s in p.stakeholders] == ["État", "Région"]
    assert p.flows[0].score == 0.5 and p.flows[0].category == "Économique"
    assert p.focal == p.stakeholders[0].id


def test_csv_export_reimport_identique():
    p = examples.essai_de_jeu()
    q = Project(name="x")
    svn_io.import_flows_csv(q, svn_io.flows_csv(p))
    q.focal = q.find_by_name("Projet").id
    assert [c.score for c in find_cycles(q).cycles] == [c.score for c in find_cycles(p).cycles]


def test_mit_dat_aller_retour():
    p = examples.essai_de_jeu()
    q = svn_io.import_mit_edge_dat(svn_io.mit_edge_dat(p), focal_name="Projet")
    assert [c.score for c in find_cycles(q).cycles] == [c.score for c in find_cycles(p).cycles]


def test_txt_tabulation():
    p = Project(name="txt")
    txt = "source\ttarget\tname\tscore\nA\tB\tAide\t0.5\nB\tA\tRetour\t0,4\n"
    assert svn_io.import_flows_csv(p, txt) == (2, 0)


def test_txt_sans_entete_format_matrixpath():
    t = svn_io.parse_flows_table("Aide;A;B;0.5\nRetour;B;A;0.4\n")
    assert not t.has_header and len(t.rows) == 2 and t.rows[0]["source"] == "A"


def test_separateur_barre_verticale_et_erreurs_signalees():
    t = svn_io.parse_flows_table("origine|destination|nom|score\nA|B|x|0.5\nA|B|y|2\nA||z|0.1\n")
    assert t.delimiter == "|" and len(t.rows) == 1
    assert [n for n, _ in t.errors] == [3, 4]


def test_encodage_windows_1252():
    data = "origine;destination;nom;score\nÉtat;Région;Aide;0,5\n".encode("cp1252")
    assert svn_io.parse_flows_table(svn_io.decode_bytes(data)).rows[0]["source"] == "État"


def test_colonnes_inconnues():
    with pytest.raises(ValueError):
        svn_io.parse_flows_table("a;b\n1;2\n")
