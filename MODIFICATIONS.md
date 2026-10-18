# Ariston Integration Fork - Modifications

Fork de [fustom/ariston-remotethermo-home-assistant-v3](https://github.com/fustom/ariston-remotethermo-home-assistant-v3) avec support amélioré pour les appareils BSB (pompes à chaleur Ariston).

## Modifications apportées

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
