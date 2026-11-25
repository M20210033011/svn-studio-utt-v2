"""Modèle de données d'un projet SVN (Stakeholder Value Network).

Un projet contient :
- des parties prenantes (les nœuds du réseau) ;
- des flux de valeur orientés (les arêtes) : ``source -> target`` signifie
  « valeur fournie par la source à la cible », avec un score entre 0 et 1 ;
- un projet central (``focal``) : le nœud d'où partent et où reviennent les cycles.

Le format JSON est le même que celui de l'ancienne version HTML de SVN Studio,
ce qui permet de réimporter les sauvegardes existantes.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field

COLORS = ["#298ca6", "#8059b9", "#d58a45", "#2b967f", "#bf6573",
          "#637fa9", "#a58042", "#538f8e", "#a86fba"]

TYPES = ["Projet central", "Bénéficiaire", "Institution publique", "Partenaire",
         "Fournisseur", "Équipe interne", "Communauté", "Financeur",
         "Régulateur", "Autre"]

CATEGORIES = ["Technologique", "Économique", "Social", "Environnemental",
              "Performance", "Gestion", "Autre"]

# Limites reprises de la version HTML (protection contre les fichiers énormes).
MAX_STAKEHOLDERS = 250
MAX_FLOWS = 1200


def new_id(prefix: str) -> str:
    """Identifiant court et unique, par exemple ``s_3f9a1c2b``."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Stakeholder:
    id: str
    name: str
    type: str = "Autre"
    description: str = ""
    color: str = COLORS[0]


@dataclass
class Flow:
    id: str
    source: str          # identifiant de la partie prenante qui fournit la valeur
    target: str          # identifiant de la partie prenante qui la reçoit
    name: str
    score: float         # entre 0 et 1
    category: str = "Autre"
    description: str = ""


@dataclass
class Project:
    name: str = "Mon projet SVN"
    description: str = ""
    focal: str | None = None
    stakeholders: list[Stakeholder] = field(default_factory=list)
    flows: list[Flow] = field(default_factory=list)
    version: int = 1

    # --- accès pratiques -------------------------------------------------
    def stakeholder(self, sid: str | None) -> Stakeholder | None:
        return next((s for s in self.stakeholders if s.id == sid), None)

    def name_of(self, sid: str | None) -> str:
        s = self.stakeholder(sid)
        return s.name if s else "?"

    def find_by_name(self, name: str) -> Stakeholder | None:
        key = name.strip().lower()
        return next((s for s in self.stakeholders if s.name.strip().lower() == key), None)

    def add_stakeholder(self, name: str, type: str = "Autre", description: str = "") -> Stakeholder:
        s = Stakeholder(id=new_id("s"), name=name.strip(), type=type, description=description,
                        color=COLORS[len(self.stakeholders) % len(COLORS)])
        self.stakeholders.append(s)
        return s

    def find_or_add(self, name: str, description: str = "") -> Stakeholder:
        return self.find_by_name(name) or self.add_stakeholder(name, description=description)

    def valid_flows(self) -> list[Flow]:
        """Flux utilisables dans les calculs (extrémités existantes, score dans [0, 1])."""
        ids = {s.id for s in self.stakeholders}
        return [f for f in self.flows
                if f.source in ids and f.target in ids and f.source != f.target
                and is_valid_score(f.score)]

    # --- (dé)sérialisation ------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "focal": self.focal,
            "stakeholders": [asdict(s) for s in self.stakeholders],
            "flows": [asdict(f) for f in self.flows],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Project":
        errors = validate_dict(d)
        if errors:
            raise ValueError(" ; ".join(errors))
        stakeholders = [Stakeholder(id=str(s["id"]), name=str(s["name"]),
                                    type=str(s.get("type") or "Autre"),
                                    description=str(s.get("description") or ""),
                                    color=str(s.get("color") or COLORS[i % len(COLORS)]))
                        for i, s in enumerate(d["stakeholders"])]
        flows = [Flow(id=str(f.get("id") or new_id("f")), source=str(f["source"]),
                      target=str(f["target"]), name=str(f.get("name") or ""),
                      score=float(f["score"]), category=str(f.get("category") or "Autre"),
                      description=str(f.get("description") or ""))
                 for f in d["flows"]]
        p = cls(name=str(d["name"]), description=str(d.get("description") or ""),
                focal=d.get("focal"), stakeholders=stakeholders, flows=flows,
                version=int(d.get("version") or 1))
        if p.focal and not p.stakeholder(p.focal):
            p.focal = stakeholders[0].id if stakeholders else None
        return p


def is_valid_score(x) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return 0.0 <= v <= 1.0


def validate_dict(d) -> list[str]:
    """Contrôles faits à l'import d'un JSON (mêmes règles que la version HTML)."""
    if not isinstance(d, dict) or not isinstance(d.get("name"), str) \
            or not isinstance(d.get("stakeholders"), list) or not isinstance(d.get("flows"), list):
        return ["Ce fichier JSON ne correspond pas à un projet SVN Studio valide."]
    if len(d["stakeholders"]) > MAX_STAKEHOLDERS or len(d["flows"]) > MAX_FLOWS:
        return [f"Projet trop grand (max. {MAX_STAKEHOLDERS} parties prenantes, {MAX_FLOWS} flux)."]
    ids = [s.get("id") for s in d["stakeholders"] if isinstance(s, dict)]
    if len(ids) != len(d["stakeholders"]) or any(not i or not s.get("name")
                                                 for i, s in zip(ids, d["stakeholders"])):
        return ["Chaque partie prenante doit avoir un identifiant et un nom."]
    if len(set(ids)) != len(ids):
        return ["Des identifiants de parties prenantes sont en double."]
    idset = set(ids)
    for f in d["flows"]:
        if not isinstance(f, dict) or f.get("source") not in idset or f.get("target") not in idset \
                or f.get("source") == f.get("target") or not is_valid_score(f.get("score")):
            return ["Le fichier contient des flux invalides (extrémité inconnue, boucle sur soi-même "
                    "ou score hors de [0, 1])."]
    return []
