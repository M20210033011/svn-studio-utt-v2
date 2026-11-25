# SVN Studio

Outil open source d'analyse des **Stakeholder Value Networks (SVN)** : parties prenantes, flux de
valeur, cycles de valeur et indicateurs de priorisation. Utilisable pour tout projet, quel que soit
le domaine, sans installation ni programmation.

- Construire un réseau de parties prenantes reliées par des flux de valeur notés de 0 à 1.
- Trouver tous les cycles qui partent du projet central et y reviennent ; score d'un cycle =
  produit des scores de ses flux.
- Classer parties prenantes et flux : WSO, WOO, WIO, WVFO (fondés sur les cycles) et influence
  moyenne par les flux émis, reçus, ou les deux.
- Importer et exporter en JSON, en CSV et au format `.dat` de MatrixPath.

## Pour commencer

- **Utiliser l'outil** : ouvrir l'application en ligne, puis suivre le
  [guide méthodologique](docs/guide_methodologique.md) (aussi disponible dans le menu de l'outil).
- **Comprendre ou modifier le code** : [explication du code](docs/explication_du_code.md).

## Lancer en local

```
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```
pip install pytest
pytest
```

Les tests vérifient que les résultats sont identiques à ceux de l'outil MatrixPath sur l'exemple
pédagogique et retrouvent les chemins critiques d'un réseau de référence publié.

## Licence

MIT — voir [LICENSE](LICENSE).
