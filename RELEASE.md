# Guide de publication - Ariston BSB Enhanced

## Prérequis

- Git configuré avec accès push au repo
- GitHub CLI (`gh`) installé et authentifié

## Étapes de publication

### 1. Faire les modifications

Modifier les fichiers dans `custom_components/ariston/`.

### 2. Incrémenter la version

Éditer `custom_components/ariston/manifest.json` :

```json
{
  "version": "X.Y.Z"
}
```

### 3. Commit et push

```bash
cd /Users/tacscma2/repo/homeassistant/ariston-integration-fork

# Ajouter les fichiers modifiés
git add custom_components/ariston/
git add MODIFICATIONS.md  # si modifié

# Commit
git commit -m "feat(bsb): description des changements"

# Commit du bump de version
git add custom_components/ariston/manifest.json
git commit -m "chore: bump version to X.Y.Z"

# Push
git push origin main
```

### 4. Créer le tag

```bash
git tag -a vX.Y.Z -m "vX.Y.Z - Description courte"
git push origin vX.Y.Z
```

### 5. Créer la release GitHub (obligatoire pour HACS)

⚠️ **HACS ne détecte que les GitHub Releases, pas les tags seuls !**

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - Titre de la release" \
  --notes "## Nouveautés

- Changement 1
- Changement 2

## Corrections

- Fix 1"
```

Ou via l'interface GitHub :
1. Aller sur https://github.com/marcschorderet/ariston-ha-bsb-fork/releases
2. Cliquer "Draft a new release"
3. Choisir le tag `vX.Y.Z`
4. Remplir le titre et les notes
5. Publier

### 6. Vérifier dans HACS

1. Home Assistant → HACS → Intégrations → Ariston BSB Enhanced
2. Menu (3 points) → Recharger
3. La nouvelle version doit apparaître

## Commande tout-en-un

```bash
VERSION="1.0.11"
MSG="Description des changements"

cd /Users/tacscma2/repo/homeassistant/ariston-integration-fork

# Bump version dans manifest.json (à faire manuellement ou avec sed)
# sed -i '' "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" custom_components/ariston/manifest.json

git add -A
git commit -m "chore: bump version to $VERSION"
git push origin main
git tag -a "v$VERSION" -m "v$VERSION - $MSG"
git push origin "v$VERSION"
gh release create "v$VERSION" --title "v$VERSION - $MSG" --notes "## Nouveautés

$MSG"
```

## Structure des versions

- **Major (X)** : changements incompatibles
- **Minor (Y)** : nouvelles fonctionnalités rétrocompatibles  
- **Patch (Z)** : corrections de bugs

## Fichiers à mettre à jour

| Fichier | Quand |
|---------|-------|
| `manifest.json` | Toujours (version) |
| `MODIFICATIONS.md` | Si nouvelles fonctionnalités |
| `README.md` | Si changements majeurs |
| `hacs.json` | Si changement de nom ou version HA min |
