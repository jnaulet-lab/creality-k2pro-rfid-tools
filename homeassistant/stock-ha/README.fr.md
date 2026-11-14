# Option B : stock de filament dans Home Assistant (sans Spoolman)

[English version](README.md) · [Retour au guide principal](../../README.fr.md)

Connais ton stock de filament restant avec Home Assistant seul : `imprimante → Home Assistant`, rien d'autre.

> **Choisis A ou B, pas les deux.** Cette option partage des assistants, des capteurs, un compteur et un identifiant d'automation avec l'[option A (Spoolman)](../spoolman/README.fr.md). N'installe que l'une des deux.

## Pourquoi cette option
La chaîne imprimante → SpoolmanSync (sur un NAS) → Home Assistant → Spoolman peut être complexe et sensible aux mises à jour, et Spoolman ne peut pas savoir laquelle de plusieurs bobines identiques est en service. Si ton besoin réel est de connaître ton stock restant, cette option est plus simple.

## Fonctionnement
- **Un compteur en grammes par référence de filament**, pas par bobine physique. La clé est le code matière lu sur la puce (attribut `rfid`) plus la couleur (`color_hex`). Pour une bobine sans puce, la clé se compose du matériau, du nom et de la couleur saisis sur l'écran de l'imprimante.
- **À chaque changement de slot et en fin d'impression**, l'automation relève la longueur de filament consommée et appelle un petit script Python (`stock_filament.py`, bibliothèque standard uniquement). Le script la convertit en grammes (filament 1,75 mm, densité par matériau ; ordre de grandeur : 1 m de PLA ≈ 3 g) et la retire du compteur.
- **Calcul par delta, pas par utility_meter.** Le capteur `used_material_length` est cumulatif sur une impression. L'automation stocke une référence (`input_number.k2pro_creality_last_used_length`) et ne débite que la différence. Au démarrage d'une impression, la référence est remise à 0.
- Cette automation réutilise la logique de suivi (changement de slot, fin d'impression, imprimante hors ligne) et le capteur `Active Tray` généré à l'origine pour SpoolmanSync. C'est pourquoi les entités gardent leur préfixe `spoolmansync_*` : elles correspondent à la configuration réellement testée. **Seul le capteur `Active Tray` est requis** ; le capteur `Filament Usage` et l'`utility_meter` sont spécifiques à l'option A et ne doivent pas être installés.
- **Données :** `/config/stock/stock_filament.json`, avec une copie `.bak` du dernier état valide avant chaque écriture. Chaque opération est aussi journalisée dans `stock_filament_log.csv` (séparateur `;`, virgule décimale, ouvrable dans Excel).
- **`sensor.stock_filament`** (intégration `command_line`) expose le tout. Son état est le nombre de références ; **`-1` signifie que le fichier JSON est illisible**. Il est actualisé après chaque action et toutes les heures.

## Tableau de bord
![Tableau de bord du stock dans Home Assistant](../../docs/images/ha-stock-dashboard.jpg)

- **Grille de pastilles :** une carte par filament, avec sa couleur réelle, son nom et le poids restant. « ⚠️ à saisir » s'affiche tant que le poids réel n'a pas été renseigné. Les filaments récemment utilisés apparaissent en premier.
- **Recherche et filtres :** champ de recherche texte, filtre par matière (PLA, PETG…) et masquage des bobines vides.
- **Sélection et ajustement :** on clique une pastille pour la sélectionner (badge vert), puis on saisit le poids et on appuie sur *Fixer (pesée)* ou *Ajouter (achat)*. Aucune saisie technique.
- **Seuil d'alerte :** un champ dédié (`input_number.stock_filament_seuil_alerte`) déclenche une notification persistante quand une référence passe sous le seuil. 0 = alertes désactivées.
- Les assistants (sélection, recherche, filtre, grammes, seuil) sont déclarés dans `configuration.yaml`, une automation gère l'alerte et deux scripts exécutent les boutons.

**À propos de l'affichage de la couleur.** Une pastille en HTML/CSS (`<span style="...">`) ne s'affichait pas dans la carte Markdown, vraisemblablement parce que Home Assistant filtre les styles inline. La solution est la même que celle des cartes Mushroom des slots du CFS : une petite image SVG intégrée (`data:image/svg+xml`) colorée avec le code couleur. La pastille emoji n'est plus utilisée dans le dashboard, mais reste disponible dans les attributs `dot` / `option` de `sensor.stock_filament` pour d'autres usages.

## Testé avec
Home Assistant OS 18.5 et Creality WebSocket Integration ([ha_creality_ws](https://github.com/3dg1luk43/ha_creality_ws)) 0.9.10, sur une K2 Pro avec CFS. Les chemins supposent `/config`, et le script est lancé par `shell_command` avec `python3`. Cartes requises : `auto-entities` et `mushroom`.

## Installation
1. Copie [`stock/stock_filament.py`](stock/stock_filament.py) dans `/config/stock/` (crée le dossier).
2. Ajoute à ton `configuration.yaml` les blocs de [`configuration_extrait.yaml`](configuration_extrait.yaml), en remplaçant `k2pro_creality` par le préfixe des entités de ton imprimante. Fusionne-les avec tes blocs `template:`, `input_number:` et `utility_meter:` existants ; `input_text:`, `input_select:`, `input_boolean:`, `shell_command:` et `command_line:` sont nouveaux. L'`utility_meter` et le capteur `Filament Usage` sont un héritage de SpoolmanSync : ils ne sont pas lus par l'automation de l'option B, mais sont conservés pour compatibilité. Tu peux les supprimer si tu n'as jamais installé l'option A.
3. Ajoute les **deux** automations de [`automations_extrait.yaml`](automations_extrait.yaml) (débit et alerte de stock bas), les deux scripts de [`scripts_extrait.yaml`](scripts_extrait.yaml) (ou crée-les dans l'interface : Paramètres > Automatisations et scènes > Scripts > Modifier en YAML) et la vue de tableau de bord de [`dashboard_extrait.yaml`](dashboard_extrait.yaml) (à coller dans la liste `views:` de ton tableau de bord, avec l'éditeur de configuration brut).
4. Vérifie la configuration (Outils de développement > YAML), puis **redémarre** Home Assistant. Un simple rechargement ne suffit pas pour `shell_command`, `command_line` et les nouveaux assistants.
5. **Teste sans imprimer**, dans Outils de développement > Actions : lance `shell_command.stock_filament_debit` avec `key: test_ffffff`, `label: Test PLA #ffffff`, `material: PLA` et `length_cm: 1000` (≈ -30 g), puis `homeassistant.update_entity` sur `sensor.stock_filament`. La pastille doit apparaître dans la grille.
6. **Supprime l'entrée de test.** Lance `shell_command.stock_filament_remove` avec `query: Test PLA #ffffff`, puis `homeassistant.update_entity` sur `sensor.stock_filament`. Si tu n'as pas encore saisi de vrai stock, tu peux aussi simplement supprimer `/config/stock/stock_filament.json` (l'historique reste dans le CSV). **Ne modifie pas le JSON à la main** : une virgule en trop le rend illisible.

## Utilisation
Une référence n'apparaît qu'à sa première consommation, avec un stock à 0 qui passe en négatif et la mention « ⚠️ à saisir ». Clique la pastille, saisis le poids réel de la bobine et appuie sur *Fixer (pesée)*. Ensuite, chaque impression le fait baisser automatiquement. Appuie sur *Ajouter (achat)* après l'achat d'une nouvelle bobine.

> **Pas de valeur initiale sur le champ « Grammes ».** Il démarre à 0 et rien n'est validé tant que tu n'as pas saisi un poids. C'est voulu : cela évite de faire croire à un stock de 1000 g fictif avant la première pesée.

## Dépannage
- **Journaux « Command failed (with return code 1): python3 /config/stock/stock_filament.py dump » et « Empty reply found when expecting JSON data » :** `stock_filament.json` est invalide, typiquement après une modification manuelle (virgule en trop, accolade manquante). Corrige la syntaxe, restaure la copie `.bak`, ou supprime le fichier si tu n'as pas encore saisi ton stock (l'historique reste dans le CSV). Avec la version actuelle du script, le capteur affiche `-1` au lieu de produire une erreur, et les commandes d'écriture ne modifient rien.
- **La grille de pastilles reste vide :** aucune consommation n'a encore été enregistrée, ou le script n'est pas à jour (mets-le à jour avant l'automation).
- **Les boutons *Fixer* / *Ajouter* ne font rien :** aucune pastille n'est sélectionnée. Clique d'abord une pastille (badge vert), puis saisis le poids et appuie sur le bouton. Vérifie aussi l'identifiant des scripts créés via l'interface (Paramètres > Scripts) : les fichiers fournis utilisent `script.stock_filament_fixer_le_stock` et `script.stock_filament_ajouter_au_stock`.
- **L'alerte de stock bas ne se déclenche pas :** vérifie que le seuil (`input_number.stock_filament_seuil_alerte`) est supérieur à 0, et que le filament a bien un stock saisi (`tracked: true`). Le seuil s'applique aux références dont le stock a déjà été pesé.

## Limites
- Le suivi est **par référence, pas par bobine** : on sait combien on en a en tout, pas quelle bobine est la plus vide.
- La précision dépend de la longueur de filament déclarée par l'imprimante : pèse une bobine de temps en temps pour recaler.
- Une bobine sans puce sur le support externe est identifiée par son matériau, son nom et sa couleur saisis à l'écran. Si tu les modifies d'une fois sur l'autre, cela crée une nouvelle référence.
- Le JSON inline généré par `auto-entities` peut casser si un nom de filament contient une apostrophe ou un guillemet. Évite ces caractères dans les noms de bobines.
- L'alerte de stock bas utilise des notifications persistantes. Pour recevoir aussi une notification sur ton téléphone, décommente le bloc `notify.mobile_app_*` dans `automations_extrait.yaml`.

## Fichiers
| Fichier | Rôle |
|---|---|
| `configuration_extrait.yaml` | Assistants, capteur `Active Tray`, `shell_command`, `command_line` |
| `automations_extrait.yaml` | Débit du stock (changement de slot, fin d'impression, imprimante hors ligne) et alerte de stock bas |
| `scripts_extrait.yaml` | Boutons *Fixer le stock* et *Ajouter au stock* |
| `dashboard_extrait.yaml` | Vue `Filaments` avec la grille de pastilles et la carte d'ajustement |
| `stock/stock_filament.py` | Script du compteur (`debit`, `set`, `add`, `remove`, `dump`) |

Voir le [CHANGELOG](../../CHANGELOG.md) pour connaître l'historique des modifications.
