"""Test de fumée de l'interface : chaque page s'ouvre sans erreur, avec les deux exemples."""
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(p.name for p in (ROOT / "views").glob("*.py"))


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("example", ["essai_de_jeu", "vide"])
def test_page(page, example):
    from svn_core import examples

    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    from svn_core import Project

    at.session_state["project"] = examples.essai_de_jeu() if example == "essai_de_jeu" else Project()
    at.run()
    at.switch_page(f"views/{page}")
    at.run()
    assert not at.exception, at.exception


def test_page_comparaison_avec_deux_scenarios():
    """La page de comparaison s'affiche avec T0 (scénario A) et T1 (scénario B)."""
    from svn_core import io as svn_io

    d = ROOT / "data" / "examples" / "doughnut"
    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.session_state["project"] = svn_io.load_json((d / "T0_base.json").read_text(encoding="utf-8"))
    at.session_state["compare_b"] = svn_io.load_json(
        (d / "T1_doughnut_global.json").read_text(encoding="utf-8"))
    at.run()
    at.switch_page("views/comparaison.py")
    at.run()
    assert not at.exception, at.exception
    assert len(at.dataframe) >= 3
    assert any("Doughnut" in c.value for c in at.caption)


@pytest.mark.parametrize("page", ["cycles.py", "priorisation.py"])
def test_avertissement_acteur_hors_cycles(page):
    """Avec T1, les pages Cycles et Priorisation (WSO) signalent le Doughnut hors des cycles."""
    from svn_core import io as svn_io

    d = ROOT / "data" / "examples" / "doughnut"
    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.session_state["project"] = svn_io.load_json(
        (d / "T1_doughnut_global.json").read_text(encoding="utf-8"))
    at.run()
    at.switch_page(f"views/{page}")
    at.run()
    assert not at.exception, at.exception
    assert any("Doughnut" in i.value and "aucun cycle" in i.value for i in at.info)
