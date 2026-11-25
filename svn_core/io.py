"""Import et export : JSON (projet complet), CSV (flux), fichiers .dat de MatrixPath."""

from __future__ import annotations

import csv
import io
import json
import unicodedata
from dataclasses import dataclass

from .cycles import CycleResult
from .metrics import Row
from .model import CATEGORIES, Flow, Project, is_valid_score, new_id

# Noms de colonnes acceptés dans un CSV de flux (français ou anglais).
HEADER_ALIASES = {"origine": "source", "destination": "target", "nom": "name",
                  "categorie": "category", "note": "score"}
REQUIRED = ["source", "target", "name", "score"]


# --- JSON -----------------------------------------------------------------
def load_json(text: str) -> Project:
    return Project.from_dict(json.loads(text))


def dump_json(project: Project) -> str:
    return json.dumps(project.to_dict(), ensure_ascii=False, indent=2)


# --- CSV ------------------------------------------------------------------
def _norm(h: str) -> str:
    h = unicodedata.normalize("NFD", h.strip().lower())
    h = "".join(c for c in h if unicodedata.category(c) != "Mn")
    return HEADER_ALIASES.get(h, h)


def _parse_score(raw: str) -> float | None:
    try:
        v = float(str(raw).strip().replace(",", "."))
    except ValueError:
        return None
    return v if is_valid_score(v) else None


def decode_bytes(data: bytes) -> str:
    """Décode un fichier texte : UTF-8 (avec ou sans BOM), sinon Windows-1252 (Excel français)."""
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Encodage du fichier non reconnu.")


def detect_delimiter(first_line: str) -> str:
    """Séparateur le plus fréquent dans la première ligne parmi ; tabulation , |"""
    counts = {d: first_line.count(d) for d in (";", "\t", ",", "|")}
    best = max(counts, key=lambda d: counts[d])
    return best if counts[best] else ";"


@dataclass
class ParsedTable:
    """Résultat de la lecture d'un fichier de flux, avant import (pour l'aperçu)."""
    rows: list[dict]              # lignes valides : source, target, name, score, category, description
    errors: list[tuple[int, str]]  # (numéro de ligne dans le fichier, raison)
    delimiter: str
    has_header: bool


def parse_flows_table(text: str) -> ParsedTable:
    """Lit un tableau de flux (CSV, TXT, TSV ou .dat MatrixPath).

    - Avec en-tête : colonnes origine;destination;nom;score (ou source;target;name;score),
      facultatives categorie;description.
    - Sans en-tête : 4 colonnes nom;source;cible;score (format input_edge.dat de MatrixPath).
    Le séparateur (; tabulation , |) est détecté automatiquement.
    """
    text = text.lstrip("\ufeff")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("Le fichier est vide.")
    delim = detect_delimiter(lines[0])
    raw = [r for r in csv.reader(io.StringIO("\n".join(lines)), delimiter=delim)]
    headers = [_norm(h) for h in raw[0]]
    has_header = all(h in headers for h in REQUIRED)
    if has_header:
        body = raw[1:]
        records = [{h: (r[i].strip() if i < len(r) else "") for i, h in enumerate(headers)} for r in body]
        start = 2
    elif len(raw[0]) >= 4 and _parse_score(raw[0][3]) is not None:
        records = [{"name": r[0].strip(), "source": r[1].strip(), "target": r[2].strip(),
                    "score": r[3].strip()} if len(r) >= 4 else {} for r in raw]
        start = 1
    else:
        raise ValueError("Colonnes non reconnues. Le fichier doit avoir l'en-tête "
                         "origine;destination;nom;score (ou source;target;name;score), "
                         "ou 4 colonnes sans en-tête nom;source;cible;score.")
    rows, errors = [], []
    for n, o in enumerate(records, start=start):
        if not o.get("source") or not o.get("target") or not o.get("name"):
            errors.append((n, "origine, destination ou nom manquant"))
            continue
        if o["source"].strip().lower() == o["target"].strip().lower():
            errors.append((n, "origine et destination identiques"))
            continue
        score = _parse_score(o.get("score", ""))
        if score is None:
            errors.append((n, f"score invalide « {o.get('score', '')} » (attendu entre 0 et 1)"))
            continue
        cat = o.get("category", "")
        rows.append({"source": o["source"], "target": o["target"], "name": o["name"], "score": score,
                     "category": cat if cat in CATEGORIES else "Autre",
                     "description": o.get("description", "")})
    if not rows and not errors:
        raise ValueError("Le fichier ne contient aucune ligne de données.")
    return ParsedTable(rows, errors, delim, has_header)


def read_csv_rows(text: str) -> list[dict]:
    """Compatibilité : lignes valides d'un tableau de flux."""
    return parse_flows_table(text).rows


def add_parsed_flows(project: Project, table: ParsedTable) -> int:
    for o in table.rows:
        src = project.find_or_add(o["source"], "Importé depuis un fichier")
        dst = project.find_or_add(o["target"], "Importé depuis un fichier")
        project.flows.append(Flow(id=new_id("f"), source=src.id, target=dst.id, name=o["name"],
                                  score=o["score"], category=o["category"],
                                  description=o["description"]))
    if not project.focal and project.stakeholders:
        project.focal = project.stakeholders[0].id
    return len(table.rows)


def import_flows_csv(project: Project, text: str) -> tuple[int, int]:
    """Ajoute au projet les flux d'un fichier CSV/TXT. Les parties prenantes absentes sont créées.

    Retourne (nombre de flux importés, nombre de lignes ignorées).
    """
    table = parse_flows_table(text)
    return add_parsed_flows(project, table), len(table.errors)


def _csv(rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    w.writerows(rows)
    return "﻿" + buf.getvalue()  # BOM : Excel ouvre correctement les accents


def flows_csv(p: Project) -> str:
    return _csv([["origine", "destination", "nom", "score", "categorie", "description"]] +
                [[p.name_of(f.source), p.name_of(f.target), f.name, f.score, f.category, f.description]
                 for f in p.flows])


def stakeholders_csv(p: Project) -> str:
    return _csv([["identifiant", "nom", "profil", "description", "central"]] +
                [[s.id, s.name, s.type, s.description, "OUI" if s.id == p.focal else "NON"]
                 for s in p.stakeholders])


def cycles_csv(p: Project, res: CycleResult) -> str:
    return _csv([["rang", "cycle", "score", "longueur", "flux"]] +
                [[i + 1, " → ".join(p.name_of(n) for n in c.nodes), c.score, c.length,
                  " | ".join(f.name for f in c.flows)] for i, c in enumerate(res.cycles)])


def indicators_csv(all_rows: dict[str, list[Row]]) -> str:
    out = [["indicateur", "rang", "element", "valeur", "nb_flux", "somme_scores"]]
    for key, rows in all_rows.items():
        out += [[key, i + 1, r.name, r.value, "" if r.count is None else r.count,
                 "" if r.total is None else r.total] for i, r in enumerate(rows)]
    return _csv(out)


# --- MatrixPath (format .dat) --------------------------------------------
def mit_vertex_dat(p: Project) -> str:
    return "\n".join(s.name for s in p.stakeholders) + "\n"


def mit_edge_dat(p: Project) -> str:
    return "\n".join(f"{f.name};{p.name_of(f.source)};{p.name_of(f.target)};{f.score}"
                     for f in p.flows) + "\n"


def import_mit_edge_dat(text: str, focal_name: str | None = None, name: str = "Import MatrixPath") -> Project:
    """Construit un projet à partir d'un fichier input_edge.dat (nom;source;cible;score)."""
    p = Project(name=name)
    for line in text.lstrip("﻿").splitlines():
        parts = [x.strip() for x in line.split(";")]
        if len(parts) < 4 or not parts[0]:
            continue
        score = _parse_score(parts[3])
        if score is None or parts[1].lower() == parts[2].lower():
            continue
        src, dst = p.find_or_add(parts[1]), p.find_or_add(parts[2])
        p.flows.append(Flow(new_id("f"), src.id, dst.id, parts[0], score))
    focal = p.find_by_name(focal_name) if focal_name else None
    p.focal = focal.id if focal else (p.stakeholders[0].id if p.stakeholders else None)
    return p
