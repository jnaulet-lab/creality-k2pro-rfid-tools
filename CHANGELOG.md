# Changelog

Toutes les modifications notables de ce projet sont consignées ici. / All notable changes to this project are recorded here.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), numérotation de type [SemVer](https://semver.org/lang/fr/) : `x.y.z` (rupture.nouveauté.correction). / Format inspired by Keep a Changelog, SemVer-style numbering: `x.y.z` (breaking.feature.fix).

## [Unreleased] / [À venir]

_Rien pour le moment. / Nothing yet._

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

