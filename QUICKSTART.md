# 🚀 Guide de Démarrage Rapide - Bot Polymarket MVP

## ✅ Phase 1 Complétée: Infrastructure

L'infrastructure de base est maintenant en place:
- ✅ Docker Compose (PostgreSQL + Redis)
- ✅ Base de données avec 4 modèles (Position, Trade, Opportunity, Config)
- ✅ Configuration Alembic pour les migrations
- ✅ Scripts de démarrage automatisés

## 📋 Prérequis

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Compte Polymarket (pour Phase 2)

## 🔧 Configuration Initiale

### 1. Copier le fichier d'environnement

```bash
cp .env.example .env
```

### 2. Éditer `.env` avec vos credentials

```bash
# Wallet (à configurer en Phase 2)
WALLET_ADDRESS=votre_adresse_wallet
WALLET_PRIVATE_KEY=votre_clé_privée

# Secret Key (générer avec: openssl rand -hex 32)
SECRET_KEY=votre_secret_key_ici
```

## 🚀 Démarrage

### Option A: Développement Local (Recommandé)

```bash
./start-dev.sh
```

Ce script va:
1. Démarrer PostgreSQL et Redis avec Docker
2. Créer l'environnement virtuel Python
3. Installer les dépendances
4. Exécuter les migrations
5. Démarrer le backend (port 8000)
6. Démarrer le frontend (port 3000)

### Option B: Docker Complet

```bash
docker-compose up -d
```

## 📍 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🛑 Arrêt

```bash
./stop.sh
```

Ou avec Docker:

```bash
docker-compose down
```

## 📊 Structure de la Base de Données

### Tables Créées

1. **positions** - Positions de trading actives/fermées
2. **trades** - Historique de tous les trades
3. **opportunities** - Opportunités détectées par le scanner
4. **config** - Configuration du bot (key-value)

### Migrations

```bash
# Créer une nouvelle migration
cd backend
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## 🔍 Vérification

### Backend

```bash
curl http://localhost:8000/api/status
```

Devrait retourner le statut du bot.

### Frontend

Ouvrir http://localhost:3000 dans le navigateur.

## 📝 Prochaines Étapes

### Phase 2: Intégration Polymarket (3 jours)
- [ ] Installer py-clob-client
- [ ] Créer client Polymarket
- [ ] Implémenter authentification wallet
- [ ] Tester connexion et récupération marchés

### Phase 3: Trading Basique (4 jours)
- [ ] Implémenter trading engine simplifié
- [ ] Créer position monitor
- [ ] Implémenter fermeture manuelle

## 🐛 Dépannage

### PostgreSQL ne démarre pas

```bash
docker-compose down -v
docker-compose up -d postgres
```

### Erreur de migration

```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Port déjà utilisé

Modifier les ports dans `docker-compose.yml` ou arrêter les services conflictuels.

## 📚 Documentation

- [État des Lieux Complet](/.gemini/antigravity/brain/daa5ec6e-4eae-44e4-ba80-bf4cf3630e60/etat_des_lieux.md)
- [Plan d'Optimisation](/.gemini/antigravity/brain/daa5ec6e-4eae-44e4-ba80-bf4cf3630e60/plan_optimisation.md)
- [Résumé Exécutif](/.gemini/antigravity/brain/daa5ec6e-4eae-44e4-ba80-bf4cf3630e60/resume_executif.md)
