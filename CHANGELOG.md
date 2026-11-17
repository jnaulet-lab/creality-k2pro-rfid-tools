# Changelog

Toutes les modifications notables de ce projet sont consignées ici. / All notable changes to this project are recorded here.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), numérotation de type [SemVer](https://semver.org/lang/fr/) : `x.y.z` (rupture.nouveauté.correction). / Format inspired by Keep a Changelog, SemVer-style numbering: `x.y.z` (breaking.feature.fix).

## [Unreleased] / [À venir]

_Rien pour le moment. / Nothing yet._

## [1.1.4] - 2026-11-17

### Français

**Corrigé**
- **Option B, `delta_cm` robuste à la remise à zéro du compteur** : si `used_material_length` est inférieur à la référence (l'imprimante l'a remis à zéro pour une nouvelle impression), le delta est la valeur courante au lieu d'être forcé à 0. Avant, la consommation du début d'une impression pouvait ne pas être débitée tant que le compteur n'avait pas dépassé l'ancienne référence.
- **Option B, `print_start` calé sur `current_length`** : la référence `input_number.k2pro_creality_last_used_length` prend la valeur courante du capteur au lieu de 0. Avec 0, un changement de slot survenant avant la remise à zéro du compteur par l'imprimante pouvait débiter une seconde fois toute l'impression précédente. Le message de log est ajusté.
- **Option B, identification du filament (`automations_extrait.yaml`)** : les variables `material_code`, `material`, `name`, `color` et `vendor` utilisent `or ''` au lieu de `| default('')`. `state_attr()` renvoie `None` (et non une valeur indéfinie) quand un attribut manque, donc `default('')` ne s'appliquait pas : une bobine sans attribut `rfid` pouvait produire une clé du type `None_<couleur>` et une fausse référence dans le stock.
- **Option B, slot actif des impressions mono-slot** : la branche `print_start` mémorise désormais le slot actif dans `input_number.spoolmansync_k2pro_creality_last_tray`. Auparavant, ce helper n'était mis à jour que lors d'un changement direct de slot : si le capteur `Active Tray` repassait par `unknown` entre deux impressions, un débit de fin d'impression pouvait être imputé à l'ancien slot.
- **Option B, recherche du dashboard** : la recherche texte et le filtre matière font une correspondance littérale (sous-chaîne, insensible à la casse) au lieu d'une expression régulière. Chercher `PLA+HS` ne trouvait pas « PLA+HS », et une parenthèse seule provoquait une erreur de template.
- **Option B, « Masquer les vides »** : seules les bobines suivies (`tracked`) dont le stock est inférieur ou égal à 0 sont masquées. Auparavant, les références « ⚠️ à saisir » (stock jamais renseigné, donc négatif) disparaissaient aussi, ce qui empêchait de les initialiser.
- **Option B, noms de filament dans la grille** : le nom des cartes passe par `tojson`. Un guillemet dans un nom ne casse plus le JSON généré par `auto-entities` (la limite correspondante est retirée du README).
- **Option B, `stock_filament.py`** : écriture plus sûre (`fsync` avant `os.replace`, pour éviter un fichier vide après une coupure de courant). Quand le JSON est illisible, un débit n'est plus perdu sans trace : une ligne `debit_perdu` est ajoutée au CSV pour pouvoir le rattraper à la main.

**Modifié**
- **Option B, `stock_filament.py`** : retrait de la fonction `color_dot` et des attributs `dot` et `option` de `sensor.stock_filament` (pastille emoji, inutilisée par le dashboard depuis 1.1.0). Les attributs du capteur sont plus légers.
- **Option B, `configuration_extrait.yaml`** : suppression de l'`utility_meter` et du capteur `Filament Usage` (héritage SpoolmanSync, non lus par l'option B ; le capteur `Active Tray` n'en dépend pas, contrairement à ce que disait un commentaire). Les installations existantes peuvent les laisser en place ou les supprimer. Commentaire de `stock_filament_masquer_vides` précisé.

**Documentation**
- **README option B (FR + EN)** : description de la mémorisation du slot actif, de la recherche littérale, des bobines « à saisir » toujours visibles et de la ligne `debit_perdu` ; nouvelles entrées de dépannage ; retrait de la limite sur les guillemets dans les noms ; « trois scripts » au lieu de « deux » ; le bloc `notify.mobile_app_*` à décommenter, absent de `automations_extrait.yaml`, est remplacé par un exemple d'action à ajouter ; paragraphe de suppression passé au tutoiement (FR).

### English

**Fixed**
- **Option B, `delta_cm` robust to the counter reset**: if `used_material_length` is lower than the reference (the printer reset it for a new print), the delta is the current value instead of being forced to 0. Previously, the consumption at the start of a print could go undebited until the counter exceeded the old reference.
- **Option B, `print_start` set to `current_length`**: the reference `input_number.k2pro_creality_last_used_length` takes the sensor's current value instead of 0. With 0, a slot change happening before the printer reset the counter could debit the whole previous print a second time. The log message is adjusted.
- **Option B, filament identification (`automations_extrait.yaml`)**: the `material_code`, `material`, `name`, `color` and `vendor` variables use `or ''` instead of `| default('')`. `state_attr()` returns `None` (not an undefined value) when an attribute is missing, so `default('')` never applied: a spool without an `rfid` attribute could produce a key like `None_<color>` and a bogus reference in the stock.
- **Option B, active slot for single-slot prints**: the `print_start` branch now stores the active slot in `input_number.spoolmansync_k2pro_creality_last_tray`. Previously this helper was only updated on a direct slot-to-slot change: if the `Active Tray` sensor went through `unknown` between two prints, an end-of-print debit could be charged to the previous slot.
- **Option B, dashboard search**: the text search and the material filter use a literal (case-insensitive substring) match instead of a regular expression. Searching `PLA+HS` did not find "PLA+HS", and a lone parenthesis caused a template error.
- **Option B, "Masquer les vides"**: only tracked spools (`tracked`) with a stock lower than or equal to 0 are hidden. Previously, "⚠️ à saisir" references (stock never entered, hence negative) disappeared too, which made it impossible to initialize them.
- **Option B, filament names in the grid**: the card name goes through `tojson`. A double quote in a name no longer breaks the JSON generated by `auto-entities` (the matching limitation is removed from the README).
- **Option B, `stock_filament.py`**: safer writes (`fsync` before `os.replace`, to avoid an empty file after a power loss). When the JSON is unreadable, a debit is no longer lost without a trace: a `debit_perdu` row is added to the CSV so it can be caught up by hand.

**Changed**
- **Option B, `stock_filament.py`**: removed the `color_dot` function and the `dot` and `option` attributes of `sensor.stock_filament` (emoji dot, unused by the dashboard since 1.1.0). The sensor attributes are lighter.
- **Option B, `configuration_extrait.yaml`**: removed the `utility_meter` and the `Filament Usage` sensor (SpoolmanSync legacy, not read by option B; the `Active Tray` sensor does not depend on them, contrary to what a comment said). Existing installations can keep or remove them. Comment of `stock_filament_masquer_vides` clarified.

**Documentation**
- **Option B README (FR + EN)**: description of the active-slot memorization, the literal search, the "⚠️ à saisir" spools always visible and the `debit_perdu` row; new troubleshooting entries; removed the limitation about quotes in names; "three scripts" instead of "two"; the `notify.mobile_app_*` block to uncomment, which was absent from `automations_extrait.yaml`, is replaced by an example action to add; delete paragraph switched to informal address (FR).

## [1.1.3] - 2026-11-16

### Français

**Corrigé**
- **Option B, `helper_tray` dans `tray_composite`** : le template utilise désormais un `{% set helper_tray = ... %}` local au lieu de dépendre de la variable `helper_tray` définie au niveau `variables:`. Cela supprime le warning `'helper_tray' is undefined` qui pouvait casser le débit quand Jinja évaluait `tray_composite` avant `helper_tray`.
- **Option B, déclencheur `tray`** : la liste `not_to` inclut désormais aussi `""` en plus de `unavailable` et `unknown`, pour ignorer les transitions vers un état vide.

**Ajouté**
- **Option B, bouton « Supprimer la bobine sélectionnée »** dans la vue Filaments : une carte Mushroom avec confirmation native Home Assistant. Le bouton appelle le nouveau script `stock_filament_supprimer_la_bobine`, qui supprime la référence par sa clé interne puis vide `input_text.stock_filament_selection`. L'historique reste dans le CSV.

**Documentation**
- **README (FR + EN)** : mention du bouton de suppression dans la section « Utilisation », et du remplacement en place des préréglages redéposés dans `add_filament.html`.

### English

**Fixed**
- **Option B, `helper_tray` in `tray_composite`**: the template now uses a local `{% set helper_tray = ... %}` instead of relying on the `helper_tray` variable defined at the `variables:` level. This removes the `'helper_tray' is undefined` warning that could break the debit when Jinja evaluated `tray_composite` before `helper_tray`.
- **Option B, `tray` trigger**: the `not_to` list now also includes `""` in addition to `unavailable` and `unknown`, to ignore transitions to an empty state.

**Added**
- **Option B, "Delete the selected spool" button** in the Filaments view: a Mushroom card with native Home Assistant confirmation. The button calls the new `stock_filament_supprimer_la_bobine` script, which deletes the reference by its internal key and then clears `input_text.stock_filament_selection`. The history stays in the CSV.

**Documentation**
- **README (FR + EN)**: mention of the delete button in the "Usage" section, and of the in-place replacement of re-dropped presets in `add_filament.html`.

## [1.1.2] - 2026-11-15

### Français

**Corrigé**
- **Option B, débit en fin d'impression** : le déclencheur `print_end` couvre désormais `stopped` (annulation) et `error` (plantage), en plus de `completed` et `idle`. Le dernier delta est débité même si l'impression ne va pas au bout. La condition `from_state` exclut `off`, `stopped` et `error` pour éviter les débits fantômes au démarrage ou après un arrêt suivi d'une erreur.
- **Option B, reprise après pause ou erreur** : un `print_start` consécutif à `paused`, `error`, `stopped`, `self-testing`, `unavailable` ou `unknown` ne remet plus la référence de longueur à 0 (nouvelle condition globale sur l'automation). Le compteur `used_material_length` continuant de monter pendant la pause, l'ancien comportement provoquait un double débit à la reprise.
- **Option B, conservation de la référence en fin d'impression et hors ligne** : dans les branches `print_end` et `offline`, la référence `input_number.k2pro_creality_last_used_length` est désormais fixée à `current_length` au lieu de 0. Une impression relancée après un arrêt (changement de bobine, redémarrage) reprend sans re-débiter le delta déjà consommé.
- **Option B, filtre « Autre » retiré** : l'option « Autre » de `input_select.stock_filament_filtre_matiere` ne correspondait à aucun filament (le filtre fait un match de sous-chaîne sur le libellé) et vidait la grille. Les options restantes (PLA, PETG, ABS, ASA, TPU) fonctionnent comme prévu.
- **Option B, grille `auto-entities`** : le template encadre désormais la liste JSON par `[` et `]`. Sans ces crochets, une grille filtrée à un seul élément n'était pas reconnue comme une liste par `auto-entities` et la carte ne s'affichait pas. Ajout de `show_empty: false` pour éviter un espace vide quand aucun filament n'est visible.

**Documentation**
- **README (FR + EN)** : mention des événements `stopped` et `error` couverts, du comportement de reprise après pause, et de la conservation de la référence en fin d'impression.

### English

**Fixed**
- **Option B, debit at end of print**: the `print_end` trigger now covers `stopped` (cancel) and `error` (crash), in addition to `completed` and `idle`. The last delta is debited even if the print does not complete. The `from_state` condition excludes `off`, `stopped` and `error` to avoid phantom debits on startup or after a stop followed by an error.
- **Option B, resume after pause or error**: a `print_start` following `paused`, `error`, `stopped`, `self-testing`, `unavailable` or `unknown` no longer resets the length reference to 0 (new global condition on the automation). Because `used_material_length` keeps rising during the pause, the previous behaviour caused a double debit on resume.
- **Option B, reference kept at end of print and offline**: in the `print_end` and `offline` branches, the reference `input_number.k2pro_creality_last_used_length` is now set to `current_length` instead of 0. A print restarted after a stop (spool change, reboot) resumes without re-debiting the delta already consumed.
- **Option B, "Autre" filter removed**: the "Autre" option of `input_select.stock_filament_filtre_matiere` matched no filament (the filter uses a substring match on the label) and emptied the grid. The remaining options (PLA, PETG, ABS, ASA, TPU) work as expected.
- **Option B, `auto-entities` grid**: the template now wraps the JSON list in `[` and `]`. Without these brackets, a grid filtered down to a single element was not recognized as a list by `auto-entities` and the card did not render. Added `show_empty: false` to avoid an empty gap when no filament is visible.

**Documentation**
- **README (FR + EN)**: mention of the `stopped` and `error` events covered, the resume behaviour after a pause, and the reference being kept at end of print.

## [1.1.1] - 2026-11-14

### Français

**Corrigé**
- **Option B, débit en fin d'impression** : le déclencheur `print_end` couvre désormais `stopped` (annulation) et `error` (plantage), en plus de `completed` et `idle`. Le dernier delta est donc bien débité même si l'impression ne va pas au bout. La condition `from_state` exclut `off`, `stopped` et `error` pour éviter les débits fantômes au démarrage ou après un arrêt suivi d'une erreur.
- **Option B, filtre « Autre » retiré** : l'option « Autre » de `input_select.stock_filament_filtre_matiere` ne correspondait à aucun filament (le filtre fait un match de sous-chaîne sur le libellé, pas sur le type technique) et vidait la grille. Les options restantes (PLA, PETG, ABS, ASA, TPU) fonctionnent comme prévu.

### English

**Fixed**
- **Option B, debit at end of print**: the `print_end` trigger now covers `stopped` (cancel) and `error` (crash), in addition to `completed` and `idle`. The last delta is therefore properly debited even if the print does not complete. The `from_state` condition excludes `off`, `stopped` and `error` to avoid phantom debits on startup or after a stop followed by an error.
- **Option B, "Autre" filter removed**: the "Autre" option of `input_select.stock_filament_filtre_matiere` matched no filament (the filter uses a substring match on the label, not on the technical type) and emptied the grid. The remaining options (PLA, PETG, ABS, ASA, TPU) work as expected.

## [1.1.0] - 2026-11-14

### Français

**Ajouté**
- **Option B, alerte de stock bas** : notification persistante envoyée une seule fois quand une référence passe sous un seuil réglable (`input_number.stock_filament_seuil_alerte`, 0 = désactivée), effacée quand le stock remonte. Nouvelle automation `stock_filament_alerte_stock_bas`. Un bloc `notify.mobile_app_*` commenté permet de recevoir aussi l'alerte sur téléphone.
- **Option B, grille de pastilles** dans le tableau de bord : une carte Mushroom par filament, avec sa couleur réelle (SVG intégré), son nom et le poids restant ; les filaments récemment utilisés apparaissent en premier. Remplace l'ancien tableau Markdown à une seule ligne et l'ancienne liste déroulante.
- **Option B, recherche et filtres** : champ de recherche texte (`input_text.stock_filament_recherche`), filtre par matière (`input_select.stock_filament_filtre_matiere`) et masquage des bobines vides (`input_boolean.stock_filament_masquer_vides`).
- **Option B, sélection par clé interne** : la pastille cliquée écrit la clé du filament (`i.key`) dans `input_text.stock_filament_selection` ; les scripts *Fixer le stock* et *Ajouter au stock* lisent cette clé au lieu du libellé, ce qui évite les collisions entre deux bobines de même nom.
- **Option B, nouveau calcul du débit par delta** : l'automation de débit conserve une référence de longueur (`input_number.k2pro_creality_last_used_length`) et ne retire que la différence entre deux triggers. Un nouveau déclencheur `print_start` remet cette référence à 0 au démarrage d'une impression.
- **Option B, documentation** : README FR/EN réécrits pour la nouvelle interface (grille de pastilles, seuil d'alerte, dépendance aux cartes `auto-entities` et `mushroom`), avec un tableau d'installation mis à jour et de nouvelles entrées de dépannage (grille vide, boutons inactifs sans sélection, alerte qui ne se déclenche pas).
- **`CHANGELOG.md`** : ajout du présent fichier (il n'existait pas encore dans le dépôt).

**Modifié**
- **Option B, `configuration_extrait.yaml`** : ajout des helpers `k2pro_creality_last_used_length`, `stock_filament_seuil_alerte`, `stock_filament_selection`, `stock_filament_recherche`, `stock_filament_filtre_matiere`, `stock_filament_masquer_vides` ; suppression de `input_select.stock_filament_choix` et de la valeur `initial: 1000` sur `stock_filament_grammes` (évite de valider 1000 g fictifs avant la première pesée). L'`utility_meter` et le capteur `Filament Usage` sont conservés (héritage SpoolmanSync), avec un commentaire explicite indiquant qu'ils ne sont pas lus par l'Option B. Le capteur `Active Tray` est marqué requis.
- **Option B, `automations_extrait.yaml`** : l'automation de débit remplace les appels `utility_meter.calibrate` par un calcul de delta ; ajout du déclencheur `print_start` ; la deuxième automation (remplissage de la liste déroulante) est supprimée et remplacée par l'alerte de stock bas.
- **Option B, `scripts_extrait.yaml`** : les scripts *Fixer le stock* et *Ajouter au stock* lisent la clé interne stockée dans `input_text.stock_filament_selection` au lieu du libellé de la liste déroulante.
- **Option B, `dashboard_extrait.yaml`** : la section `grid` avec carte `entities` et tableau Markdown est remplacée par une vue `sections` complète (grille de pastilles via `auto-entities`, recherche/filtre/masquage, carte d'ajustement avec seuil).
- **README racine (FR et EN)** : la section « Partie 2 » est réécrite pour refléter la nouvelle Option B (grille de pastilles, recherche, filtre, seuil d'alerte, dépendance aux cartes `auto-entities` et `mushroom`).

**Corrigé**
- **Option B** : le débit n'est plus calculé à partir d'un `utility_meter` calibré à chaque changement de slot (fragile en cas de trigger manqué), mais à partir du delta de `sensor.k2pro_creality_used_material_length`, ce qui rend le calcul idempotent et résistant aux redémarrages.
- **Option B** : le compteur ne valide plus 1000 g fictifs avant la première pesée (suppression de `initial: 1000`).
- **Option B** : l'alerte de stock bas efface correctement la notification persistante quand une référence remonte ou quand elle est supprimée du JSON (la liste `recovered` inclut les clés disparues).

**Limites connues (inchangées)**
- Tout a été validé sur une seule configuration ; la compatibilité avec d'autres modèles n'est pas garantie.
- L'accès root modifie un fichier interne de l'imprimante : risque pour la garantie, sauvegarde indispensable.
- Option A : impossible de distinguer deux bobines identiques (même fabricant, matériau et couleur).
- Option B : suivi par référence de filament, pas par bobine ; la précision dépend de la longueur déclarée par l'imprimante ; le JSON inline généré par `auto-entities` peut casser si un nom de filament contient une apostrophe ou un guillemet.
- Option B : le déclencheur `print_end` n'inclut pas le passage `printing → idle` ; le débit est alors assuré par le déclencheur `offline` (après 2 min). À revoir dans une prochaine version.

### English

**Added**
- **Option B, low-stock alert**: a persistent notification sent once when a reference goes below an adjustable threshold (`input_number.stock_filament_seuil_alerte`, 0 = disabled), dismissed when the stock goes back up. New automation `stock_filament_alerte_stock_bas`. A commented `notify.mobile_app_*` block lets you also receive the alert on your phone.
- **Option B, tile grid** in the dashboard: one Mushroom card per filament, with its real color (embedded SVG), name and remaining weight; recently used filaments come first. Replaces the old single-line Markdown table and the old drop-down list.
- **Option B, search and filters**: text search field (`input_text.stock_filament_recherche`), material filter (`input_select.stock_filament_filtre_matiere`) and hide-empty-spools toggle (`input_boolean.stock_filament_masquer_vides`).
- **Option B, selection by internal key**: clicking a tile writes the filament key (`i.key`) to `input_text.stock_filament_selection`; the *Fixer le stock* and *Ajouter au stock* scripts read this key instead of the label, avoiding collisions between two spools with the same name.
- **Option B, new delta-based debit**: the debit automation keeps a length reference (`input_number.k2pro_creality_last_used_length`) and only subtracts the difference between two triggers. A new `print_start` trigger resets this reference to 0 at the start of a print.
- **Option B, documentation**: FR/EN READMEs rewritten for the new interface (tile grid, alert threshold, dependency on `auto-entities` and `mushroom` cards), with an updated installation table and new troubleshooting entries (empty grid, inactive buttons without selection, alert not firing).
- **`CHANGELOG.md`**: this file is added (it did not exist in the repository yet).

**Changed**
- **Option B, `configuration_extrait.yaml`**: added helpers `k2pro_creality_last_used_length`, `stock_filament_seuil_alerte`, `stock_filament_selection`, `stock_filament_recherche`, `stock_filament_filtre_matiere`, `stock_filament_masquer_vides`; removed `input_select.stock_filament_choix` and the `initial: 1000` value on `stock_filament_grammes` (avoids validating fictitious 1000 g before the first weighing). The `utility_meter` and the `Filament Usage` sensor are kept (SpoolmanSync legacy), with an explicit comment stating they are not read by Option B. The `Active Tray` sensor is marked as required.
- **Option B, `automations_extrait.yaml`**: the debit automation replaces `utility_meter.calibrate` calls with a delta computation; added the `print_start` trigger; the second automation (filling the drop-down list) is removed and replaced by the low-stock alert.
- **Option B, `scripts_extrait.yaml`**: the *Fixer le stock* and *Ajouter au stock* scripts read the internal key stored in `input_text.stock_filament_selection` instead of the drop-down label.
- **Option B, `dashboard_extrait.yaml`**: the `grid` section with an `entities` card and a Markdown table is replaced by a full `sections` view (tile grid via `auto-entities`, search/filter/hide, adjustment card with threshold).
- **Root README (FR and EN)**: the "Part 2" section is rewritten to reflect the new Option B (tile grid, search, filter, alert threshold, dependency on `auto-entities` and `mushroom` cards).

**Fixed**
- **Option B**: the debit is no longer computed from a `utility_meter` calibrated at each slot change (fragile when a trigger is missed), but from the delta of `sensor.k2pro_creality_used_material_length`, making the computation idempotent and resilient to restarts.
- **Option B**: the counter no longer validates fictitious 1000 g before the first weighing (removed `initial: 1000`).
- **Option B**: the low-stock alert correctly dismisses the persistent notification when a reference goes back up or when it is removed from the JSON (the `recovered` list includes disappeared keys).

**Known limitations (unchanged)**
- Everything was validated on a single configuration; compatibility with other models is not guaranteed.
- Root access edits an internal printer file: warranty risk, a backup is essential.
- Option A: two identical spools (same vendor, material and color) cannot be told apart.
- Option B: tracking is per filament reference, not per spool; accuracy depends on the length the printer reports; the inline JSON generated by `auto-entities` may break if a filament name contains an apostrophe or a double quote.
- Option B: the `print_end` trigger does not include the `printing → idle` transition; the debit is then handled by the `offline` trigger (after 2 min). To be revisited in a future version.

## [1.0.0] - 2026-11-12

> _Note : la description de l'Option B ci-dessous reflète l'état publié en 1.0.0 (tableau Markdown, liste déroulante, boutons Fixer / Ajouter). Cette interface a été remplacée en 1.1.0 par une grille de pastilles, une recherche et un seuil d'alerte. / Note: the Option B description below reflects the state published in 1.0.0 (Markdown table, drop-down list, Set / Add buttons). That interface was replaced in 1.1.0 by a tile grid, a search field and an alert threshold._

### Français

**Ajouté**
- **Guide RFID** pour la Creality K2 Pro / CFS : accès root, modification du catalogue `material_database.json`, synchronisation avec l'appli CFS RFID, écriture de tags M1 Classic 1K, pose des tags sur la bobine.
- **Outils d'ajout de filaments au catalogue** à partir des préréglages exportés de Creality Print :
  - `tools/add_filament.html` : page autonome, hors ligne, par glisser-déposer, en français et en anglais ;
  - `tools/add_filament.py` : script Python équivalent, avec sauvegarde horodatée de l'original.
  - Les deux ajoutent l'entrée sous sa propre marque, mettent à jour `result.count` et augmentent `result.version` à chaque modification (l'appli CFS RFID ne retélécharge la base que si la version change).
- **Modèles 3D** pour poser les tags : gabarit de positionnement (`RFID_Positioning_Tool`), support simple pour bobine carton (`RFID_Holder`) et support clipable de 55 mm (`Support_RFID_55mm`).
- **Partie 2 optionnelle, Home Assistant**, au choix :
  - **Option A** : Spoolman via SpoolmanSync (assignation automatique de la bobine au slot du CFS, `dry_run` activé par défaut, token dans `secrets.yaml`) ;
  - **Option B** : stock de filament dans Home Assistant seul, avec script Python (`debit`, `set`, `add`, `remove`, `dump`), tableau de bord (tableau avec pastille de couleur, liste déroulante, boutons Fixer / Ajouter) et dépannage.
- Documentation **bilingue** (français / anglais), photos d'illustration, `CONTRIBUTING.md`, licences MIT (configuration et outils) et CC BY-SA 4.0 (modèles 3D et documentation).

**Testé avec**
- Creality K2 Pro Combo (CFS), Home Assistant OS 18.5, Creality WebSocket Integration 0.9.10.
- Option A : Spoolman 0.27.0 et SpoolmanSync 1.6.14 (validée avant le passage de l'auteur à l'option B).

**Limites connues**
- Tout a été validé sur une seule configuration ; la compatibilité avec d'autres modèles n'est pas garantie.
- L'accès root modifie un fichier interne de l'imprimante : risque pour la garantie, sauvegarde indispensable.
- Option A : impossible de distinguer deux bobines identiques (même fabricant, matériau et couleur).
- Option B : suivi par référence de filament, pas par bobine ; la précision dépend de la longueur déclarée par l'imprimante.

**Corrigé**
- ...
- **README racine (FR et EN)** : correction du tableau comparatif des options A/B, auquel il manquait des colonnes et qui était de ce fait incompréhensible.

### English

**Added**
- **RFID guide** for the Creality K2 Pro / CFS: root access, editing the `material_database.json` catalog, syncing with the CFS RFID app, writing M1 Classic 1K tags, attaching the tags to the spool.
- **Tools to add filaments to the catalog** from presets exported by Creality Print:
  - `tools/add_filament.html`: standalone, offline, drag-and-drop page, in French and English;
  - `tools/add_filament.py`: equivalent Python script, with a timestamped backup of the original.
  - Both add the entry under its own brand, update `result.count` and raise `result.version` on every change (the CFS RFID app only downloads the catalog again when the version changes).
- **3D models** to attach the tags: positioning jig (`RFID_Positioning_Tool`), simple holder for cardboard spools (`RFID_Holder`) and 55 mm clip-on support (`Support_RFID_55mm`).
- **Optional Part 2, Home Assistant**, with two choices:
  - **Option A**: Spoolman via SpoolmanSync (automatic assignment of the spool to the CFS slot, `dry_run` on by default, token kept in `secrets.yaml`);
  - **Option B**: filament stock in Home Assistant alone, with a Python script (`debit`, `set`, `add`, `remove`, `dump`), a dashboard (table with color dot, drop-down list, Set / Add buttons) and troubleshooting.
- **Bilingual** documentation (French / English), illustration photos, `CONTRIBUTING.md`, MIT (configuration and tools) and CC BY-SA 4.0 (3D models and documentation) licenses.

**Tested with**
- Creality K2 Pro Combo (CFS), Home Assistant OS 18.5, Creality WebSocket Integration 0.9.10.
- Option A: Spoolman 0.27.0 and SpoolmanSync 1.6.14 (validated before the author moved to option B).

**Known limitations**
- Everything was validated on a single configuration; compatibility with other models is not guaranteed.
- Root access edits an internal printer file: warranty risk, a backup is essential.
- Option A: two identical spools (same vendor, material and color) cannot be told apart.
- Option B: tracking is per filament reference, not per spool; accuracy depends on the length the printer reports.

**Fixed**
- ...
- **Root README (FR and EN)**: fixed the A/B options comparison table, which was missing columns and therefore unreadable.

