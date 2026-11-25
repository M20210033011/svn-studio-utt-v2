# Explication du code

Ce document explique comment le code est organisé, pour pouvoir le lire, le modifier et l'étendre
(par exemple pour ajouter un nouvel indicateur ou de nouvelles règles de calcul).

## Vue d'ensemble

Le code est séparé en deux couches :

| Couche | Dossier | Rôle | Dépend de Streamlit ? |
|---|---|---|---|
| Moteur de calcul | `svn_core/` | Données, cycles, indicateurs, import/export | Non |
| Interface | `app.py`, `ui_state.py`, `views/` | Pages web, formulaires, graphiques | Oui |

Le moteur ne connaît pas l'interface : on peut l'utiliser seul dans un notebook Jupyter ou un
script, et les tests le vérifient sans ouvrir de navigateur.

```
svn-studio/
├── app.py                  # point d'entrée Streamlit : menu et barre latérale
├── ui_state.py             # projet en cours (session), cache des calculs, formats d'affichage
├── views/                  # une page de l'interface par fichier
├── svn_core/
│   ├── model.py            # Project, Stakeholder, Flow + validation
│   ├── cycles.py           # recherche des cycles de valeur
│   ├── metrics.py          # WSO, WOO, WIO, WVFO, influence moyenne (émis, reçus, global)
│   ├── io.py               # JSON, CSV, fichiers .dat de MatrixPath
│   ├── comparaison.py      # mise côte à côte de deux scénarios
│   └── examples.py         # exemple pédagogique
├── data/examples/          # les mêmes exemples en JSON et CSV
│   └── doughnut/           # scénarios T0, T1, T2 (et variantes avec retour) des tests Doughnut
├── tests/                  # tests automatiques (pytest)
└── docs/                   # ce document et le guide méthodologique
```

## Le moteur `svn_core`

### `model.py` — les données

- `Stakeholder` : `id`, `name`, `type`, `description`, `color`.
- `Flow` : `id`, `source`, `target` (identifiants de parties prenantes), `name`, `score` (0 à 1),
  `category`, `description`. Convention : `source → target` = valeur fournie par la source.
- `Project` : `name`, `description`, `focal` (identifiant du projet central), listes
  `stakeholders` et `flows`.
- `Project.valid_flows()` renvoie seulement les flux utilisables (extrémités existantes,
  source ≠ cible, score dans [0, 1]). **Tous les calculs passent par cette fonction.**
- `to_dict()` / `from_dict()` lisent et écrivent le format JSON, identique à celui de l'ancienne
  version HTML. `validate_dict()` refuse les fichiers incohérents.

### `cycles.py` — les cycles de valeur

`find_cycles(project)` renvoie un `CycleResult` : la liste des `Cycle` (nœuds, flux, score) triée
du plus fort au plus faible, `total` (somme des scores) et `truncated`.

Fonctionnement :

1. On construit, pour chaque partie prenante, la liste des flux qui en sortent.
2. On part du projet central avec un score de 1. À chaque étape, on prolonge le chemin par un flux
   sortant et on multiplie le score par celui du flux.
3. Si le flux revient au projet central, on obtient un cycle. Sinon, on continue, à condition de ne
   pas repasser par une partie prenante déjà visitée (cycle simple).
4. Les chemins sont rangés dans une **file de priorité** (`heapq`) : on prolonge toujours le chemin
   de plus fort score. Comme les scores sont ≤ 1, un chemin ne gagne jamais de valeur en
   s'allongeant ; les cycles sortent donc dans l'ordre décroissant. Si on dépasse 12 000 cycles,
   on s'arrête en ayant gardé les plus forts.

Les flux parallèles (deux flux A → B) sont deux flux distincts dans la liste : ils donnent
naturellement deux cycles différents.

`outside_cycles(project, res)` liste les parties prenantes (hors projet central) qui
n'apparaissent dans aucun cycle, avec la raison : aucun flux reçu, aucun flux émis, ou aucun
chemin vers le projet central. Leur WSO vaut 0. Les pages Cycles et Priorisation l'affichent via
`ui_state.outside_cycles_notice()`. La fonction renvoie une liste vide si la recherche a été
tronquée (on ne peut alors pas conclure).

### `metrics.py` — les indicateurs

Une fonction par indicateur, chacune renvoie une liste de `Row(id, name, value, count, total)`
triée par valeur décroissante :

| Fonction | Formule |
|---|---|
| `wso` | Σ scores des cycles passant par la partie prenante ÷ Σ scores de tous les cycles |
| `woo` | Σ scores des cycles commençant par le flux ÷ Σ scores de tous les cycles |
| `wio` | Σ scores des cycles finissant par le flux ÷ Σ scores de tous les cycles |
| `wvfo` | Σ scores des cycles contenant le flux ÷ somme de ces quantités sur tous les flux |
| `influence_emis` | moyenne des scores des flux sortants |
| `influence_recus` | moyenne des scores des flux entrants |
| `influence_global` | moyenne des scores de tous les flux, entrants et sortants |

`METRICS` contient le titre, la question et la formule affichés dans l'interface.
`compute_all()` calcule tout d'un coup.

### `comparaison.py` — deux scénarios côte à côte

`Scenario.of(project)` calcule les cycles et tous les indicateurs d'un projet.
`compare_indicator(a, b, clé)` renvoie, pour chaque élément, la valeur dans A, dans B et l'écart
(`None` si l'élément est absent d'un scénario). `compare_critical_paths(a, b)` donne les 10
meilleurs cycles de chaque scénario avec leur rang dans l'autre. Les éléments sont rapprochés par
leur nom, car deux fichiers peuvent utiliser des identifiants différents. Aucun nouveau calcul :
on réutilise `find_cycles` et `compute_all`. Page correspondante : `views/comparaison.py`
(menu *Outils*).

### `io.py` — import et export

- `load_json` / `dump_json` : projet complet.
- `decode_bytes` : lit un fichier en UTF-8, ou en Windows-1252 (fichiers Excel français).
- `parse_flows_table` : lit un tableau de flux CSV ou TXT **sans rien modifier** et renvoie un
  `ParsedTable` (lignes valides, lignes rejetées avec leur raison, séparateur détecté). C'est ce
  qui permet l'aperçu avant import. Séparateurs `;`, tabulation, `,`, `|` ; en-têtes français ou
  anglais ; ou 4 colonnes sans en-tête (format `.dat` de MatrixPath).
- `add_parsed_flows` / `import_flows_csv` : ajoutent les flux au projet et créent les parties
  prenantes manquantes.
- `flows_csv`, `stakeholders_csv`, `cycles_csv`, `indicators_csv` : exports CSV (UTF-8 avec BOM
  pour qu'Excel affiche les accents).
- `mit_vertex_dat`, `mit_edge_dat`, `import_mit_edge_dat` : échanges avec l'outil MatrixPath.

## L'interface

- `app.py` déclare les pages (`st.Page`) et le menu (`st.navigation`).
- `ui_state.py` regroupe ce qui est commun aux pages :
    - le projet dans `st.session_state.project` et les résultats en cache dans
      `st.session_state.results` ; **après toute modification du projet, appeler
      `ui_state.touch()`** pour forcer le recalcul ;
    - `STEPS` : la liste ordonnée des étapes (fichier, titre, icône, aide). Le menu, l'accueil et
      les liens *Précédent / Suivant* sont construits à partir d'elle : pour ajouter une étape,
      créer la page dans `views/` et l'ajouter à `STEPS` ;
    - `header()`, `footer_nav()`, `empty_state()` : en-tête, navigation et message « rien à
      afficher » identiques sur toutes les pages ;
    - `checklist()` et `next_action()` : avancement du modèle et prochaine étape conseillée ;
    - `replace_project()` : remplace le projet, avec une fenêtre de confirmation (`st.dialog`) si
      le projet actuel a été modifié ;
    - `flash()` : message affiché (`st.toast`) après le rechargement de la page.
- Chaque fichier de `views/` est une page. Les tableaux éditables sont dans un `st.form` : rien
  n'est modifié avant le clic sur « Enregistrer ». Les ajouts rapides (une partie prenante, un flux)
  passent par de petits formulaires séparés.
- La carte du réseau (`views/reseau.py`) lit le thème actif (`st.context.theme`) pour choisir des
  couleurs lisibles en clair comme en sombre.
- `.streamlit/config.toml` fixe la couleur principale et la taille maximale des fichiers (4 Mo).

## Utiliser le moteur dans un notebook

```python
from svn_core import examples, find_cycles, compute_all

p = examples.essai_de_jeu()
res = find_cycles(p)
for c in res.cycles[:10]:
    print(round(c.score, 4), " → ".join(f.name for f in c.flows))

m = compute_all(p, res)
for row in m["INFLUENCE_GLOBAL"]:
    print(row.name, round(row.value, 4))
```

## Modifier ou étendre

**Ajouter un indicateur.** Écrire la fonction dans `metrics.py`, l'ajouter à `METRICS` et à
`compute_all()`, puis ajouter son libellé dans `views/priorisation.py` (dictionnaire `labels`).
Écrire un test dans `tests/`.

**Ajouter un type de partie prenante particulier** (par exemple un acteur qui représente des
limites ou des contraintes) : sans changer le code, créer la partie prenante et les flux qui la
relient aux autres. Pour des règles de calcul propres à cet acteur, ajouter une fonction dans
`svn_core/`, appelée avant `find_cycles`, et la tester séparément.

**Changer la formule du score d'un cycle** (par exemple une variante qui pondère davantage certains flux) :
modifier la ligne `new_score = score * float(edge.score)` dans `cycles.py`. Attention : l'ordre
« meilleur d'abord » suppose que le score ne peut que baisser en s'allongeant.

**Vérifier qu'on n'a rien cassé.** Lancer `pytest` : les tests comparent les résultats à MatrixPath
et à un réseau de référence publié. Ils sont aussi lancés automatiquement sur GitHub à chaque envoi.

## Lancer en local

```
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Se connecter sur [share.streamlit.io](https://share.streamlit.io) avec le compte GitHub.
2. **Create app** › dépôt du projet, branche `main`, fichier `app.py`.
3. **Deploy**. Le lien obtenu est celui à donner aux utilisateurs. Chaque envoi sur `main`
   met l'application à jour.
