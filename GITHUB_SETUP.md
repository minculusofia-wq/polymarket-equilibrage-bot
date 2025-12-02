# Guide: Pousser le projet sur GitHub

## Étapes à suivre

Votre repository Git local est maintenant prêt avec un commit initial. Voici comment le pousser sur GitHub :

### Option 1 : Via l'interface GitHub (Recommandé)

1. **Créer le repository sur GitHub**
   - Allez sur https://github.com/new
   - Nom du repository : `polymarket-equilibrage-bot` (ou le nom de votre choix)
   - Description : `Bot d'équilibrage automatisé pour Polymarket avec stratégie 50/50 YES/NO`
   - Visibilité : **Private** (recommandé car contient de la logique de trading)
   - **NE PAS** initialiser avec README, .gitignore ou license (vous les avez déjà)
   - Cliquer sur "Create repository"

2. **Pousser votre code local**
   
   GitHub vous donnera des instructions. Utilisez celles-ci dans votre terminal :

   ```bash
   cd "/Users/anthony/Desktop/bot equilibrage polymarket"
   
   # Ajouter le remote GitHub (remplacer YOUR_USERNAME par votre nom d'utilisateur)
   git remote add origin https://github.com/YOUR_USERNAME/polymarket-equilibrage-bot.git
   
   # Renommer la branche en main si nécessaire
   git branch -M main
   
   # Pousser le code
   git push -u origin main
   ```

### Option 2 : Via GitHub CLI (si vous l'installez)

Si vous souhaitez installer GitHub CLI pour automatiser :

```bash
# Installer GitHub CLI
brew install gh

# S'authentifier
gh auth login

# Créer le repo et pousser en une commande
cd "/Users/anthony/Desktop/bot equilibrage polymarket"
gh repo create polymarket-equilibrage-bot --private --source=. --push
```

## Vérification

Une fois poussé, vérifiez sur GitHub que vous voyez :
- ✅ README.md affiché sur la page principale
- ✅ Structure de dossiers `.specify/`, `backend/`, `frontend/`
- ✅ Fichiers de configuration (docker-compose.yml, .env.example)
- ✅ Documentation (ARCHITECTURE.md)

## Prochaines étapes après publication

1. **Protéger la branche main**
   - Settings → Branches → Add rule
   - Require pull request reviews

2. **Configurer les secrets** (si vous utilisez GitHub Actions plus tard)
   - Settings → Secrets and variables → Actions
   - Ajouter vos API keys

3. **Inviter des collaborateurs** (optionnel)
   - Settings → Collaborators

## Commandes Git utiles pour la suite

```bash
# Vérifier le statut
git status

# Ajouter des changements
git add .

# Créer un commit
git commit -m "Description des changements"

# Pousser vers GitHub
git push

# Créer une nouvelle branche
git checkout -b feature/nom-de-la-feature

# Voir l'historique
git log --oneline
```

## Notes importantes

- ⚠️ **Ne jamais commiter le fichier `.env`** (il est dans .gitignore)
- ⚠️ **Ne jamais commiter de clés privées ou API keys**
- ✅ Le fichier `.env.example` est safe à commiter (pas de vraies credentials)
- ✅ Tous les fichiers sensibles sont déjà dans .gitignore

## Structure commitée

Voici ce qui a été inclus dans le commit initial :

```
✅ .env.example              # Template de configuration
✅ .gitignore                # Exclusions Git
✅ .specify/                 # Documentation Spec Kit
   ├── memory/constitution.md
   └── specs/001-polymarket-equilibrage-bot/
       ├── spec.md
       └── plan.md
✅ ARCHITECTURE.md           # Documentation architecture
✅ README.md                 # Documentation principale
✅ docker-compose.yml        # Configuration Docker
✅ backend/                  # Structure backend (vide pour l'instant)
✅ frontend/                 # Structure frontend (vide pour l'instant)

❌ spec-kit-main/            # Exclu (ajouté au .gitignore)
❌ .env                      # Exclu (dans .gitignore)
```

## Résumé du commit initial

```
Commit: fb39d66
Message: Initial commit: Polymarket Equilibrage Bot structure
Files: 76 fichiers
Insertions: 12,406 lignes
```

Le repository est prêt à être poussé sur GitHub ! 🚀
