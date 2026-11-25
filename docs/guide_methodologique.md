# Guide méthodologique — SVN Studio

Ce guide permet à une personne qui découvre l'outil de **mener une analyse seule** :
construire un Stakeholder Value Network (SVN), calculer les cycles de valeur et classer les
parties prenantes et les flux. Il s'applique à tout projet, quel que soit le domaine.
Comptez environ 20 minutes, exemple compris.

**Sommaire**

1. À quoi sert l'outil
2. Préparer ses données
3. Pas à pas dans l'application
4. Refaire l'exemple pédagogique
5. Formules
6. Vérifier l'outil soi-même
7. Limites et questions fréquentes

---

## 1. À quoi sert l'outil

Un **SVN** représente un projet et ses parties prenantes comme un réseau :

- les **parties prenantes** sont les nœuds (usagers, mairie, opérateurs, etc.) ;
- les **flux de valeur** sont des flèches orientées : `A → B` veut dire « A fournit une valeur à B »
  (de l'argent, une information, un service, un soutien politique…) ;
- chaque flux a un **score entre 0 et 1** : l'importance de cette valeur pour celui qui la reçoit ;
- le **projet central** (ou acteur focal) est le projet que l'on étudie.

L'outil calcule :

- les **cycles de valeur** : les chemins qui partent du projet central et y reviennent. Un cycle
  montre comment la valeur que le projet donne finit par lui revenir. Son score est le produit des
  scores de ses flux. Les cycles les plus forts sont les **chemins critiques** ;
- des **indicateurs de priorisation** : WSO, WOO, WIO, WVFO (fondés sur les cycles) et l'influence
  moyenne (moyenne des scores des flux, sans les cycles).

> Les scores décrivent le modèle construit. Ce ne sont pas des probabilités de réussite, et leur
> qualité dépend entièrement de la qualité des scores saisis.

---

## 2. Préparer ses données

Avant d'ouvrir l'outil, préparez trois choses.

**a) La liste des parties prenantes**, avec un nom unique pour chacune. Choisissez le projet
central parmi elles.

**b) La liste des flux**, une ligne par flux :

| origine | destination | nom | score | categorie |
|---|---|---|---|---|
| Projet | Population | Qualité du service | 0,57 | Performance |
| Population | Mairie | Soutien et impôts | 0,33 | Économique |
| Mairie | Projet | Décision et financement | 0,57 | Économique |

- `origine` fournit la valeur, `destination` la reçoit. **Le sens compte** : inverser un flux change
  les cycles.
- Deux flux différents peuvent relier les mêmes parties prenantes (flux parallèles) : écrivez deux lignes.
- `categorie` est facultative : Technologique, Économique, Social, Environnemental, Performance,
  Gestion ou Autre.

**c) L'origine des scores.** Notez comment chaque score a été obtenu. Une pratique courante est de
faire noter chaque flux par celui qui le **reçoit**, par exemple sur deux questions (satisfaction du
besoin et importance de la source), puis de regrouper les réponses de plusieurs personnes par la
**médiane**. Si vous estimez les scores vous-même, indiquez-le dans vos résultats.

**Format du fichier.** Un fichier **CSV** ou **TXT** (texte), une ligne par flux, avec en première
ligne les noms des colonnes. Dans Excel : *Fichier › Enregistrer sous › CSV UTF-8* ou *Texte
(séparateur : tabulation)*.

- Séparateur `;`, tabulation, `,` ou `|` : il est **détecté automatiquement**.
- Score écrit `0,57` ou `0.57`.
- Noms de colonnes anglais `source;target;name;score` aussi acceptés.
- Un fichier sans en-tête à 4 colonnes `nom;source;cible;score` (format `input_edge.dat` de
  MatrixPath) est aussi reconnu.

Un modèle rempli se télécharge à l'étape 1 de l'application (« Format attendu »).

---

## 3. Pas à pas dans l'application

Le menu de gauche a deux parties : **Démarrer** (accueil et ce guide) et **Analyse pas à pas**
(les étapes 1 à 6, dans l'ordre). En bas de chaque page, les liens *Précédent* et *Suivant* mènent
à l'étape voisine. L'encadré **Projet actuel**, en haut à gauche, montre l'avancement du modèle et
la prochaine chose à faire.

Les données restent dans l'onglet du navigateur : **exportez le projet en JSON** avant de le fermer.

### Étape 1 — Ouvrir un projet

Page **Accueil**, partie « Démarrer », trois choix :

- **Découvrir avec un exemple** : choisissez l'exemple puis cliquez **Charger l'exemple**.
- **Importer vos données** : cliquez **Importer un fichier**. Sur la page **1. Importer / exporter**,
  gardez *Tableau de flux (CSV, TXT)*, choisissez votre fichier. L'outil affiche un **aperçu** :
  nombre de flux et de parties prenantes lus, séparateur détecté, lignes ignorées et leur raison.
  Choisissez « Créer un nouveau projet » ou « Les ajouter au projet actuel », puis **Importer**.
- **Partir de zéro** : cliquez **Créer un projet vide**.

Pour reprendre un travail sauvegardé : page 1, choix *Projet sauvegardé (JSON)*. Si le projet
actuel a été modifié, l'outil demande une confirmation avant de le remplacer.

La liste « Votre modèle est-il prêt ? » de l'accueil indique ce qui manque ; chaque point non fait
est un lien vers la page où le faire.

### Étape 2 — Vérifier les parties prenantes et le projet central

Page **2. Parties prenantes**.

- **Projet central**, en haut : choisissez le projet ou l'organisation étudié. Après un import,
  c'est par défaut la première partie prenante du fichier : **vérifiez-le**.
- **Ajouter une partie prenante** ouvre un petit formulaire (nom, profil, description).
- Le tableau se modifie directement ; cliquez **Enregistrer les modifications**. Pour supprimer,
  cochez la ligne puis utilisez l'icône corbeille. Les flux d'une partie prenante supprimée sont
  retirés.
- Le nom et le contexte du projet se modifient dans « Nom et contexte du projet ».

### Étape 3 — Vérifier les flux et leurs scores

Page **3. Flux de valeur**.

- **Ajouter un flux** : choisissez la source (qui fournit) et la cible (qui reçoit), donnez un nom,
  réglez le score avec le curseur, puis **Ajouter le flux**.
- **Aide au choix du score** : deux questions (bénéfice pour la cible, préjudice si le flux manque)
  proposent un score. C'est une aide à la saisie, pas une méthode de questionnaire.
- **Liste des flux** : modifiez les cellules puis **Enregistrer les modifications**. Les boutons de
  catégorie filtrent la liste. Si une ligne est incorrecte (score hors de [0, 1], source = cible,
  nom vide), rien n'est enregistré et le message indique la ligne.

### Étape 4 — Lire la carte du réseau

Page **4. Carte du réseau**. Le réseau est dessiné automatiquement ; le projet central (★) est au
milieu. L'épaisseur d'une flèche suit son score ; survolez-la pour lire le flux. À droite :

- **Disposition** : projet au centre, ou automatique ;
- **Mettre en évidence** un cycle ou une partie prenante : ses flux passent en orange, le reste
  s'estompe.

L'icône appareil photo du graphique enregistre l'image en PNG. La carte s'adapte au thème clair
ou sombre de l'application.

### Étape 5 — Lire les cycles de valeur

Page **5. Cycles de valeur**. En haut : nombre de cycles, somme des scores, meilleur cycle et
longueur moyenne. Le tableau liste tous les cycles, du plus fort au plus faible : rang, score,
part du total, chemin, flux parcourus et longueur.

- **Cliquez sur une ligne** : le détail du cycle s'affiche, flux par flux, avec le calcul
  (`0,57 × 0,33 × 0,57 = 0,107217`).
- **Filtrer** : score minimal, longueur maximale, ou cycles qui passent par une partie prenante.

Les premiers cycles sont les chemins critiques.

### Étape 6 — Choisir un indicateur et l'interpréter

Page **6. Priorisation**. Choisissez d'abord la famille (*Fondés sur les cycles* ou *Influence
moyenne*), puis l'indicateur. La page affiche la question à laquelle il répond, sa formule,
l'élément en tête, puis un **Graphique** et un **Tableau** (onglets).

| Indicateur | Question |
|---|---|
| WSO | Quelles parties prenantes participent aux cycles les plus forts ? |
| WOO | Quels flux émis par le projet ouvrent les cycles les plus forts ? |
| WIO | Quels flux reçus par le projet ferment les cycles les plus forts ? |
| WVFO | Quels flux reviennent le plus dans les cycles forts ? |
| Influence (émis) | Quelle valeur moyenne une partie prenante fournit-elle ? |
| Influence (reçus) | Quelle valeur moyenne une partie prenante reçoit-elle ? |
| Influence (émis + reçus) | Quelle est la valeur moyenne de tous ses échanges ? |

WSO et l'influence moyenne ne mesurent pas la même chose : la première dépend des cycles, la
seconde seulement des flux d'une partie prenante. Ne les présentez pas comme un même indicateur.

### Étape 7 — Exporter les résultats

Page **1. Importer / exporter**, onglet **Exporter** :

- **Télécharger le projet (JSON)** : la sauvegarde à garder, réimportable ;
- **Tableaux (Excel)** : CSV des flux, des parties prenantes, des cycles et des indicateurs ;
- **Autres outils** : `input_vertex.dat` et `input_edge.dat` pour l'outil MatrixPath (voir partie 6).

### Outil — Comparer deux scénarios

Menu **Outils › Comparer deux scénarios**. Le scénario A est le projet actuel ; le scénario B est un
projet JSON importé sur cette page. La page met côte à côte les chiffres clés (nombre de cycles,
meilleur cycle), un indicateur au choix (WSO, influence moyenne, WOO, WIO, WVFO) avec l'écart
B − A, et les 10 chemins critiques de chaque scénario avec leur rang dans l'autre. Les parties
prenantes et les flux sont rapprochés par leur **nom** : gardez les mêmes noms dans les deux
fichiers. Une case vide signifie que l'élément n'existe pas dans ce scénario.

Exemple : ouvrez `T0_base.json` à l'étape 1, puis importez `T1_doughnut_global.json` comme
scénario B (dossier `data/examples/doughnut/` du dépôt).

---

## 4. Refaire l'exemple pédagogique

**Objectif.** Vérifier, sur un petit réseau connu, que l'on sait utiliser l'outil et lire ses
résultats. Si vous obtenez les valeurs ci-dessous, la démarche est bien suivie.

**Données.** Un réseau de transport collectif : 4 parties prenantes (*Projet*, *Population*,
*Mairie*, *Opérateurs*), 8 flux, projet central *Projet*. Le fichier est aussi fourni dans
`data/examples/modele_flux.csv`.

| origine | destination | nom | score |
|---|---|---|---|
| Projet | Population | Qualité du service | 0,57 |
| Population | Mairie | Soutien et impôts | 0,33 |
| Mairie | Projet | Décision et financement | 0,57 |
| Projet | Opérateurs | Passagers | 0,44 |
| Opérateurs | Projet | Investissement flotte | 0,56 |
| Population | Opérateurs | Billets | 0,57 |
| Opérateurs | Mairie | Respect du contrat | 0,19 |
| Mairie | Opérateurs | Subventions | 0,33 |

**Démarche.**

1. Page **Accueil**, choisissez *Exemple pédagogique (transport collectif)*, cliquez
   **Charger l'exemple**. (Ou importez le CSV ci-dessus à l'étape **1. Importer / exporter**,
   puis choisissez *Projet* comme projet central à l'étape 2.)
2. Vérifiez : 4 parties prenantes, 8 flux, projet central *Projet*.
3. Page **Cycles de valeur** : l'outil trouve **6 cycles**, pour une somme des scores de 0,6532.
4. Page **Priorisation** : comparez avec les valeurs attendues.

**Cycles attendus.**

| Rang | Cycle | Calcul | Score |
|---|---|---|---|
| 1 | Projet → Opérateurs → Projet | 0,44 × 0,56 | 0,246400 |
| 2 | Projet → Population → Opérateurs → Projet | 0,57 × 0,57 × 0,56 | 0,181944 |
| 3 | Projet → Population → Mairie → Projet | 0,57 × 0,33 × 0,57 | 0,107217 |
| 4 | Projet → Opérateurs → Mairie → Projet | 0,44 × 0,19 × 0,57 | 0,047652 |
| 5 | Projet → Population → Opérateurs → Mairie → Projet | 0,57 × 0,57 × 0,19 × 0,57 | 0,035187 |
| 6 | Projet → Population → Mairie → Opérateurs → Projet | 0,57 × 0,33 × 0,33 × 0,56 | 0,034761 |

**Indicateurs attendus.**

| Partie prenante | WSO | Influence (émis) | Influence (reçus) | Influence (émis + reçus) |
|---|---|---|---|---|
| Opérateurs | 0,8358 | 0,3750 | 0,4467 | 0,4180 |
| Population | 0,5498 | 0,4500 | 0,5700 | 0,4900 |
| Mairie | 0,3442 | 0,4500 | 0,2600 | 0,3550 |
| Projet | — | 0,5050 | 0,5650 | 0,5350 |

Le projet central n'a pas de WSO : il est dans tous les cycles par définition.

## 5. Formules

Notations : `C` = ensemble des cycles, `s(c)` = score du cycle `c`, `S = Σ s(c)` = somme des scores
de tous les cycles.

**Score d'un cycle** = produit des scores de ses flux.
Exemple : Projet → Population → Mairie → Projet = 0,57 × 0,33 × 0,57 = **0,107217**.

**WSO** (Weighted Stakeholder Occurrence) d'une partie prenante `v` (hors projet central)
= somme des `s(c)` des cycles qui passent par `v`, divisée par `S`.
Exemple : WSO de Population = (0,181944 + 0,107217 + 0,035187 + 0,034761) ÷ 0,653161 = **0,5498**.

**WOO** (Weighted Output Occurrence) d'un flux émis par le projet central
= somme des `s(c)` des cycles qui **commencent** par ce flux, divisée par `S`.

**WIO** (Weighted Input Occurrence) d'un flux reçu par le projet central
= somme des `s(c)` des cycles qui **finissent** par ce flux, divisée par `S`.

**WVFO** (Weighted Value Flow Occurrence) d'un flux `e`
= somme des `s(c)` des cycles qui contiennent `e`, divisée par la somme de cette quantité sur tous
les flux (ce qui revient à `Σ s(c) × longueur(c)`). Les WVFO somment à 100 %.

**Influence moyenne**, calculée directement sur les flux, sans les cycles :

- *émis* = moyenne des scores des flux qui sortent de la partie prenante ;
- *reçus* = moyenne des scores des flux qui entrent ;
- *émis + reçus* = moyenne des scores de tous ses flux (chaque flux compte une fois).

Exemple : les Opérateurs émettent *Investissement flotte* (0,56) et *Respect du contrat* (0,19),
donc influence (émis) = (0,56 + 0,19) ÷ 2 = **0,375**.

Une partie prenante sans flux du type considéré reçoit 0. Le projet central est inclus.

## 6. Vérifier l'outil soi-même

**Comparaison avec MatrixPath.** L'outil MatrixPath 2.0, un logiciel indépendant d'analyse SVN,
peut servir de référence.

1. Chargez l'*Exemple pédagogique* ; page **1. Importer / exporter**, onglet **Exporter**, téléchargez `input_vertex.dat` et
   `input_edge.dat`.
2. Placez-les dans le dossier `matrix-path/input/` de MatrixPath et lancez `MatrixPath2.0.jar`
   avec *Projet* comme acteur focal.
3. Comparez `FocalInfoCycle`, `FocalInfoVertex` (WSO) et `FocalInfoEdge` (WVFO) avec les pages
   Cycles et Priorisation. Les 6 cycles, les WSO et les WVFO sont identiques (écart < 10⁻¹²).

**Tests automatiques.** Ces comparaisons sont écrites dans le dossier `tests/` du dépôt et relancées
à chaque modification du code. Pour les lancer sur votre ordinateur :

```
pip install -r requirements.txt pytest
pytest
```

Les tests vérifient l'exemple pédagogique contre MatrixPath, un réseau de référence publié, les
formules de l'influence moyenne et des cas limites (flux parallèles, réseau sans cycle, scores nuls, import et
export). Ils rejouent aussi les premiers tests d'intégration du Doughnut (`tests/test_doughnut.py`,
fichiers dans `data/examples/doughnut/`).

---

## 7. Limites et questions fréquentes

**Aucun cycle n'apparaît.** Il faut au moins un chemin qui revient au projet central. Vérifiez le
sens des flux et le choix du projet central. L'influence moyenne reste calculable.

**Une partie prenante a un WSO nul.** Un cycle doit entrer dans chaque partie prenante qu'il
traverse et en ressortir. Une partie prenante qui ne reçoit aucun flux (elle ne fait qu'émettre,
par exemple des exigences) ou qui n'en émet aucun ne fait partie d'aucun cycle : son WSO vaut 0,
quels que soient ses scores. Les pages Cycles et Priorisation (WSO) l'indiquent. L'influence
moyenne, calculée sans les cycles, la prend en compte.

**Le sens des flèches.** Ici `source → cible` = valeur fournie par la source à la cible. Certaines
études décrivent plutôt un besoin exprimé par une partie prenante. Vérifiez la convention avant
d'importer des données venant d'ailleurs.

**Gros réseaux.** Le nombre de cycles croît très vite. Au-delà de 12 000 cycles, l'outil garde les
plus forts et affiche un avertissement : les indicateurs sont alors approchés.

**Mes données ont disparu.** Les données vivent dans la session du navigateur. Exportez toujours le
JSON, puis réimportez-le.

**Reprendre une sauvegarde.** Étape 1, choix *Projet sauvegardé (JSON)*.

**Fichier mal lu.** L'aperçu de l'étape 1 indique le séparateur détecté et la raison de chaque ligne
ignorée. Vérifiez la première ligne (noms des colonnes) et que les scores sont entre 0 et 1.

**Thème clair ou sombre.** Menu ⋮ en haut à droite › *Settings* › *Theme*.
