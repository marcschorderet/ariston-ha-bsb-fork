# Ariston Integration Fork - Modifications

Fork de [fustom/ariston-remotethermo-home-assistant-v3](https://github.com/fustom/ariston-remotethermo-home-assistant-v3) avec support amélioré pour les appareils BSB (pompes à chaleur Ariston).

## Modifications apportées

### 4. Timeout et gestion des erreurs API (`coordinator.py`) — 2026-10-20

**Problème résolu :** L'intégration cessait de recevoir des mises à jour de données, nécessitant un redémarrage de Home Assistant pour rétablir le fonctionnement.

**Cause racine :** La bibliothèque `ariston` (v0.19.9) n'a aucun timeout HTTP configuré pour les requêtes async. Quand l'API cloud Ariston devient lente ou ne répond pas, les requêtes HTTP restent bloquées indéfiniment, ce qui bloque le coordinateur Home Assistant.

**Corrections apportées :**

1. **Timeout de 60 secondes** sur tous les appels API via `asyncio.wait_for()`
2. **Exception `UpdateFailed`** levée en cas de timeout ou d'erreur, permettant à Home Assistant de gérer automatiquement les retry
3. **Logging détaillé** pour diagnostiquer les problèmes :
   - Temps de réponse de chaque requête
   - Timeouts avec message explicite
   - Erreurs de connexion HTTP
   - Compteur d'erreurs consécutives
   - Message de récupération après erreurs

**Configuration logging recommandée :**

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.ariston: debug  # Tous les détails
    # ou
    custom_components.ariston: info   # Seulement erreurs et récupérations
```

**Exemples de logs :**

```
# Succès (niveau DEBUG)
[COORDINATOR] Data update successful (took 2.34s)

# Timeout (niveau ERROR)
[COORDINATOR] API request TIMED OUT after 60.00s (timeout=60s). This indicates the Ariston cloud API is unresponsive. Consecutive errors: 1

# Récupération (niveau INFO)
[COORDINATOR] Data update recovered after 3 consecutive errors (took 1.89s)
```

---

### 1. Preset modes pour appareils BSB (`climate.py`)

Les appareils BSB n'avaient pas de preset modes car `plant_mode_supported` retourne `False`. Maintenant, les appareils BSB exposent les modes de zone comme presets :

| Preset | Mode BSB | Description |
|--------|----------|-------------|
| **Confort** | `BsbZoneMode.MANUAL` | Mode manuel à température confort |
| **Réduit** | `BsbZoneMode.MANUAL_NIGHT` | Mode manuel à température réduite |
| **Automatique** | `BsbZoneMode.TIME_PROGRAM` | Programmation horaire |
| **Protection** | `BsbZoneMode.OFF` | Mode antigel/protection |

### 2. Capteur binaire pompe à chaleur BSB (`const.py`)

Ajout d'un capteur binaire `is heat pump on` pour les appareils BSB, exposant l'état `hpOn` de l'API.

### 3. Noms d'entités en français pour BSB (`const.py`)

Les noms des entités BSB ont été francisés pour une meilleure lisibilité :

| Nom original (anglais) | Nouveau nom (français) |
|------------------------|------------------------|
| `is heat pump on` | **Pompe à chaleur active** |
| `is heating on` | **Chauffage actif** |
| `Outside temp` | **Température extérieure** |
| `room temperature` | **Température intérieure** |
| `desired room temperature` | **Température consigne** |
| `CH comfort temperature` | **Consigne confort** |
| `CH reduced temperature` | **Consigne réduit** |
| `DHW temperature` | **Température eau chaude** |
| `DHW mode` (sensor) | **Mode eau chaude** |
| `DHW mode` (select) | **Régler mode eau chaude** |
| `heating mode` | **Mode chauffage** |
| `holidays mode` | **Mode vacances** |
| `errors count` | **Nombre d'erreurs** |
| `CH comfort temperature setpoint` | **Régler consigne confort** |
| `CH reduced temperature setpoint` | **Régler consigne réduit** |
| `DHW comfort temperature setpoint` | **Régler eau chaude confort** |
| `DHW reduced temperature setpoint` | **Régler eau chaude réduit** |

## Installation

1. Copier le dossier `custom_components/ariston/` dans votre répertoire Home Assistant `config/custom_components/`
2. Redémarrer Home Assistant
3. L'intégration Ariston détectera automatiquement les modifications

## Utilisation dans Home Assistant

### Sélectionner un preset mode

```yaml
# Exemple d'automatisation pour passer en mode Confort
service: climate.set_preset_mode
target:
  entity_id: climate.votre_thermostat_ariston
data:
  preset_mode: "Confort"
```

### Automatisation basée sur la production solaire

```yaml
automation:
  - alias: "Chauffage Confort si production solaire"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power
        above: 1400  # 1.4 kW d'injection
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.ariston
        data:
          preset_mode: "Confort"
          
  - alias: "Chauffage Automatique si pas de soleil"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power
        below: 100
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.ariston
        data:
          preset_mode: "Automatique"
```

## Compatibilité

- Home Assistant 2024.1+
- Pompes à chaleur Ariston avec connexion cloud (BSB)
- Testé avec Ariston Nimbus

## Différences avec l'intégration originale

| Fonctionnalité | Original | Fork |
|----------------|----------|------|
| Preset modes BSB | ❌ | ✅ (Confort, Réduit, Automatique, Protection) |
| Capteur pompe à chaleur BSB | ❌ | ✅ |
| HVAC modes | ✅ | ✅ (OFF, HEAT, AUTO) |

## Upstream

Les modifications seront proposées en PR au repository upstream une fois validées.
