# Expérimentations

Prototypes antérieurs au package `terrain_virtuel`, conservés pour référence.

- `version_initiale_terrain.py` : première version, en un seul fichier, du terrain virtuel. Les équipes sont fixées (Dallas et LA Lakers) et un minuteur de 90 s tourne. La valeur du rebond y est calculée par une sigmoïde qui combine la pression adverse et l'importance du contexte. Les résultats sont exportés dans `situations.csv`.
- `random_forest_rebond.py` : génère des situations synthétiques équilibrées (0 à 3 adversaires proches), les étiquette avec la formule sigmoïde, puis entraîne un `RandomForestRegressor` (R² ≈ 0,92).
