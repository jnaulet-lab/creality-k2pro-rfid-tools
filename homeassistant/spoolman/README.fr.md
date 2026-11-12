# Option A : Spoolman via SpoolmanSync

[English version](README.md) · [Retour au guide principal](../../README.fr.md)

Garde **Spoolman** synchronisé avec ton imprimante : la consommation est suivie et la bonne bobine Spoolman est assignée automatiquement au slot du CFS qui lit une puce.

> **Choisis A ou B, pas les deux.** Cette option partage des assistants, des capteurs, un compteur et un identifiant d'automation avec l'[option B (stock dans Home Assistant)](../stock-ha/README.fr.md). N'installe que l'une des deux.
>
> **État :** cette option a été validée par l'auteur, qui est ensuite passé à l'option B parce que la chaîne était trop complexe et trop sensible aux mises à jour. Ce n'est plus l'installation en service chez l'auteur.

## Fonctionnement
1. L'intégration expose un capteur par slot du CFS (`sensor.k2pro_creality_cfs_box_1_slot_1_filament`, ...) avec des attributs comme `vendor`, `type`, `color_hex`, `rfid`, `spool_key` et `selected`.
2. Deux automations SpoolmanSync suivent le slot actif et la longueur de filament consommée (cm), puis l'envoient à SpoolmanSync.
3. Une troisième automation **assigne la bobine Spoolman au slot** quand une puce est lue : elle cherche dans Spoolman les bobines non archivées du **même fabricant, matériau et couleur** que la puce. S'il y en a plusieurs, elle prend celle déjà entamée qui a le moins de filament restant, sinon la première.

### Règle de correspondance (importante)
Dans Spoolman :
- le **nom du fabricant** doit être identique à la marque écrite sur la puce (ex. `eSun`), sans tenir compte des majuscules. **Pour le slot de la bobine externe, le fabricant est facultatif**, ce qui aide pour une bobine sans puce ;
- le **matériau** doit être identique au type de filament (ex. `PLA`) ;
- le **code couleur hex** doit être identique à la couleur écrite sur la puce (sans `#`, majuscules ou minuscules sans importance).

## Testé avec
Home Assistant OS 18.5, Creality WebSocket Integration ([ha_creality_ws](https://github.com/3dg1luk43/ha_creality_ws)) 0.9.10, [Spoolman](https://github.com/Donkie/Spoolman) 0.27.0 (port 7912 par défaut) et [SpoolmanSync](https://github.com/gibz104/SpoolmanSync) 1.6.14 (port 3000 par défaut).

## Installation
1. Installe et configure Spoolman et SpoolmanSync, puis ajoute ton imprimante dans SpoolmanSync.
2. Ajoute les blocs de [`configuration_extrait.yaml`](configuration_extrait.yaml) à ton `configuration.yaml`. Remplace `k2pro_creality` par le préfixe des entités de ton imprimante, et les adresses d'exemple `SPOOLMANSYNC_IP` et `SPOOLMAN_IP` par les tiennes (souvent la même machine). Fusionne avec tes blocs `template:`, `input_number:` et `utility_meter:` existants au lieu de les dupliquer.
3. Mets le token du webhook SpoolmanSync dans `secrets.yaml` (voir [`secrets.example.yaml`](secrets.example.yaml)). **Ne publie jamais ton vrai token.**
4. Ajoute les trois automations de [`automations_extrait.yaml`](automations_extrait.yaml) à ton `automations.yaml` (ou recrée-les dans l'interface avec « Modifier en YAML »). Dans la dernière, renseigne `printer_ip` avec l'adresse IP de ton imprimante.
5. Redémarre Home Assistant.
6. **Teste d'abord :** `dry_run` est à `true` par défaut, l'automation envoie alors seulement une notification indiquant la bobine qu'elle *assignerait*. Insère une bobine avec puce, vérifie la notification, puis passe `dry_run: false`.

## Bon à savoir
- **Index des slots :** SpoolmanSync compte les slots à partir de 0, alors que les capteurs du CFS sont numérotés à partir de 1. L'automation d'assignation écrit `slot_<n-1>` : le slot 1 du CFS devient `slot_0`.
- **Bobine externe :** elle est prise en charge par l'assignation automatique (capteur `cfs_external_filament`). Le fabricant est facultatif pour ce slot ; le matériau et la couleur sont obligatoires.
- **Plusieurs bobines identiques :** quand plusieurs bobines Spoolman ont le même fabricant, matériau et couleur, l'automation choisit la bobine déjà entamée qui a le moins de filament restant. C'est une heuristique, pas une certitude : l'attribut `spool_key` des capteurs correspond au fabricant et à la couleur, **pas** à un numéro de puce unique, donc Home Assistant ne peut pas distinguer deux bobines identiques.
- Si aucune bobine ne correspond, une notification persistante te demande de l'assigner à la main dans SpoolmanSync.
- Les entités gardent leur préfixe `spoolmansync_*` : elles correspondent à la configuration réellement testée.

## Dépannage
- **La bobine du slot 2 apparaît au slot 3 (et ainsi de suite) :** c'est le décalage d'index décrit plus haut. Utilise la version actuelle de `automations_extrait.yaml`, qui écrit `slot_<n-1>`.
- **Rien n'est assigné :** vérifie que `dry_run` est bien à `false`, puis qu'une bobine Spoolman non archivée a le même matériau et la même couleur (et le même fabricant, sauf pour le slot externe).

## Fichiers
| Fichier | Rôle |
|---|---|
| `configuration_extrait.yaml` | Assistant, compteur, commandes REST vers SpoolmanSync et Spoolman, capteurs |
| `automations_extrait.yaml` | Mise à jour de la consommation, changement de slot et assignation automatique |
| `secrets.example.yaml` | Modèle pour le token SpoolmanSync |
