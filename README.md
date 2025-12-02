# Polymarket Equilibrage Bot

Un bot de trading automatisé pour Polymarket qui implémente une stratégie d'équilibrage flexible avec ratios configurables et liquidation intelligente pour maximiser les profits.

## 🎯 Vue d'ensemble

Le Polymarket Equilibrage Bot est un système de trading automatisé qui :
- Entre des positions avec **ratios configurables** (50/50, 60/40, 70/30, ou même 100/0)
- Surveille les mouvements de prix en temps réel (toutes les 30 secondes)
- Liquide **intelligemment uniquement le côté perdant** quand les seuils sont atteints
- **Maintient le côté gagnant** jusqu'à la résolution du pari pour maximiser le profit
- Détecte et score les opportunités de trading (1-10)
- Suit les mouvements des "whales" (gros traders)
- Agrège les informations pertinentes du marché

## 📋 Fonctionnalités principales

### Trading automatisé
- ✅ Entrée avec **ratios configurables par bet** (50/50, 60/40, 70/30, 100/0, etc.)
- ✅ Surveillance continue des positions actives (toutes les 30 secondes)
- ✅ **Liquidation partielle intelligente** : vend uniquement le côté perdant
- ✅ **Maintien du côté gagnant** jusqu'à résolution du bet
- ✅ Fermeture manuelle complète disponible à tout moment
- ✅ Gestion du capital avec allocation configurable

### Détection d'opportunités
- 🔍 Scan continu des marchés Polymarket
- 📊 Scoring des opportunités (échelle 1-10)
- 🐋 Suivi des whales et analyse de leurs mouvements
- 📰 Agrégation d'informations (news, données on-chain)
- ⚡ Seuil d'opportunité configurable pour auto-trading

### Dashboard interactif
- 💰 Vue d'ensemble du capital et des performances
- 📈 Tableau des positions actives en temps réel
- 🎯 Liste des opportunités détectées avec scores
- 📜 Historique complet des trades
- ⚙️ Configuration des paramètres de trading

### Gestion des risques
- 🛡️ **Stop-loss configurable** : seuil unique OU seuils séparés YES/NO (défaut: 0% = désactivé)
- 📈 **Take-profit configurable** : seuil unique OU seuils séparés YES/NO (défaut: 0% = désactivé)
- 🔢 Limite de positions concurrentes (1-10)
- 💵 Allocation de capital par pari (en %)
- 🔐 Gestion sécurisée des wallets
- 📊 Transparence totale sur les décisions du bot

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)             │
│  Dashboard | Settings | History | Scanner                    │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API + WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                    Backend (FastAPI + Python)                │
│  Trading Engine | Scanner | Opportunity Scorer               │
│  Position Monitor | Whale Tracker | Info Aggregator          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              Background Workers (Celery + Redis)             │
│  Market Scanner | Position Monitor | Whale Tracker           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Database (PostgreSQL)                       │
│  Positions | Trades | Opportunities | Config | Whales        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prérequis

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Compte Polymarket avec wallet configuré

### Configuration rapide

1. **Cloner le projet**
```bash
cd "bot equilibrage polymarket"
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos credentials
```

3. **Lancer avec Docker Compose**
```bash
docker-compose up -d
```

4. **Accéder au dashboard**
```
http://localhost:3000
```

## ⚙️ Configuration

### Paramètres de trading

Accédez à la page **Settings** pour configurer :

#### Wallet
- Adresse du wallet
- Clé privée (stockée chiffrée)

#### Paramètres de trading
- **Ratio d'entrée** : Configurable par bet (défaut: 50% YES / 50% NO)
  - Exemples: 60/40, 70/30, 100/0 (tout sur un seul côté)
- **Stop-Loss (SL)** : Seuil de liquidation (défaut: 0% = désactivé)
  - Mode unique (s'applique à YES et NO) OU modes séparés
- **Take-Profit (TP)** : Seuil de prise de profit (défaut: 0% = désactivé)
  - Mode unique (s'applique à YES et NO) OU modes séparés
- **Allocation de capital** : Pourcentage du capital par pari (1-100%)

#### Limites de positions
- **Positions max concurrentes** : 1 à 10 positions simultanées
- Le bot priorise les opportunités avec le meilleur score

#### Seuil d'opportunité
- **Seuil minimum** : Score 1-10
- Le bot n'entre automatiquement que sur les opportunités >= seuil
- Exemple : seuil à 6 → le bot trade uniquement les scores de 6 à 10

## 📊 Utilisation

### Dashboard principal

Le dashboard affiche :
- **Capital total** : Solde wallet + capital alloué
- **Positions actives** : Nombre de positions en cours
- **P&L total** : Profit/perte global
- **Opportunités détectées** : Nombre et meilleur score

### Scanner d'opportunités

La page **Scanner** montre :
- **Tableau d'opportunités** : Marchés avec scores 1-10
- **Activité des whales** : Mouvements récents
- **Informations du marché** : News et tendances
- **Bouton "Scan Now"** : Déclenche un scan manuel

### Positions actives

Pour chaque position :
- Nom du marché
- Prix d'entrée YES/NO
- Prix actuels YES/NO
- P&L en temps réel
- Bouton **Close** pour fermeture manuelle

### Historique

La page **History** contient :
- Tous les trades passés
- Filtres par date, marché, résultat
- Métriques de performance
- Export CSV

## 🔧 Structure du projet

```
.
├── .specify/                    # Spec Kit - Méthodologie Spec-Driven
│   ├── memory/
│   │   └── constitution.md      # Principes du projet
│   ├── specs/
│   │   └── 001-polymarket-equilibrage-bot/
│   │       ├── spec.md          # Spécification fonctionnelle
│   │       └── plan.md          # Plan d'implémentation technique
│   └── templates/               # Templates Spec Kit
│
├── backend/                     # Backend Python
│   ├── app/
│   │   ├── main.py             # Point d'entrée FastAPI
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Base de données
│   │   ├── models/             # Modèles SQLAlchemy
│   │   ├── services/           # Logique métier
│   │   ├── api/                # Endpoints API
│   │   ├── tasks/              # Tâches Celery
│   │   └── security/           # Sécurité & chiffrement
│   ├── alembic/                # Migrations DB
│   ├── tests/                  # Tests
│   ├── requirements.txt        # Dépendances Python
│   └── Dockerfile
│
├── frontend/                    # Frontend React
│   ├── src/
│   │   ├── App.tsx             # Application principale
│   │   ├── pages/              # Pages (Dashboard, Settings, etc.)
│   │   ├── components/         # Composants React
│   │   ├── store/              # Redux store
│   │   └── services/           # API client & WebSocket
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml           # Configuration Docker
├── .env.example                 # Variables d'environnement exemple
└── README.md                    # Ce fichier
```

## 🔐 Sécurité

- **Chiffrement des credentials** : Les clés privées sont chiffrées avec Fernet
- **Pas de logs sensibles** : Aucune clé privée dans les logs
- **Communication sécurisée** : HTTPS pour les APIs externes
- **Gestion des erreurs** : Erreurs détaillées sans exposer de données sensibles

## 📈 Stratégie de trading

### Entrée de position
1. Le scanner détecte une opportunité
2. Le scorer attribue un score 1-10
3. Si score >= seuil configuré → entrée automatique
4. Allocation selon ratio configuré (ex: 60% YES / 40% NO)

### Surveillance
- Monitoring toutes les 30 secondes (configurable)
- Calcul de la divergence par rapport au prix d'entrée
- Détection des seuils stop-loss et take-profit configurés

### Liquidation intelligente
- **Déclenchement** : Quand un seuil (SL ou TP) est atteint sur YES ou NO
- **Action** : Vente **uniquement du côté concerné** (perdant ou gagnant selon le seuil)
- **Maintien** : L'autre côté reste actif jusqu'à résolution du pari
- **Exemple** : 
  ```
  Entrée: 100$ → 50$ YES + 50$ NO
  
  Scénario:
  - YES monte à 70$ (valeur actuelle)
  - NO baisse à 30$ (valeur actuelle)
  
  Si SL à 25% atteint sur NO:
  1. Vendre NO → récupère 30$
  2. Garder YES jusqu'à 100% → récupère 100$
  3. Profit total = 30$ + 100$ - 100$ = 30$ ✅
  ```

### Fermeture manuelle
- Disponible à tout moment via le dashboard
- Vend les **deux côtés** (YES et NO)
- Capital retourné au wallet

## 🧪 Tests

### Tests unitaires
```bash
cd backend
pytest tests/unit/
```

### Tests d'intégration
```bash
cd backend
pytest tests/integration/
```

### Tests frontend
```bash
cd frontend
npm test
```

## 📚 Documentation Spec Kit

Ce projet suit la méthodologie **Spec-Driven Development** avec Spec Kit :

- **Constitution** : `.specify/memory/constitution.md` - Principes du projet
- **Spécification** : `.specify/specs/001-polymarket-equilibrage-bot/spec.md` - User stories et exigences
- **Plan technique** : `.specify/specs/001-polymarket-equilibrage-bot/plan.md` - Architecture et implémentation

### Commandes Spec Kit (si agent AI disponible)

```bash
/speckit.constitution  # Créer/modifier la constitution
/speckit.specify       # Créer/modifier les spécifications
/speckit.plan          # Créer/modifier le plan technique
/speckit.tasks         # Générer la liste des tâches
/speckit.implement     # Implémenter selon le plan
```

## 🛠️ Développement

### Lancer en mode développement

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm start
```

**Workers Celery**
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Migrations de base de données

```bash
cd backend
alembic upgrade head
```

## 🐛 Dépannage

### Le bot ne détecte pas d'opportunités
- Vérifier la connexion à l'API Polymarket
- Vérifier les logs du scanner : `docker-compose logs scanner`
- Réduire le seuil d'opportunité temporairement

### Les positions ne se liquident pas
- Vérifier que le worker de monitoring tourne : `docker-compose logs worker`
- Vérifier les logs de position_monitor
- Vérifier la connexion réseau

### Erreurs de wallet
- Vérifier que les credentials sont corrects dans Settings
- Vérifier le solde du wallet
- Vérifier la connexion au réseau Polygon

## 📝 Roadmap

### Phase 1 : Foundation ✅
- Structure du projet
- Base de données
- API de base

### Phase 2 : Core Trading (en cours)
- Intégration Polymarket
- Moteur de trading
- Monitoring des positions

### Phase 3 : Opportunity Detection
- Scanner de marchés
- Algorithme de scoring
- Whale tracker

### Phase 4 : Configuration & Settings
- Gestion de configuration
- Chiffrement wallet
- Interface Settings

### Phase 5 : Real-time & Polish
- WebSocket
- Mises à jour temps réel
- Agrégateur d'informations

### Phase 6 : Testing & Deployment
- Tests complets
- Documentation
- Guide de déploiement

## ⚠️ Avertissements

- **Trading réel uniquement** : Pas de mode paper trading - testez avec de petites sommes
- **Risques de marché** : Le trading comporte des risques de perte en capital
- **Pas de garantie** : Les performances passées ne garantissent pas les résultats futurs
- **Responsabilité** : Utilisez ce bot à vos propres risques

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre la méthodologie Spec-Driven Development :

1. Créer une spécification dans `.specify/specs/`
2. Créer un plan d'implémentation
3. Soumettre une PR avec les changements

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation dans `.specify/`
- Vérifier les logs : `docker-compose logs`

---

**Développé avec Spec Kit - Spec-Driven Development**
