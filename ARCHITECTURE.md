# Polymarket Equilibrage Bot - Architecture Documentation

## Vue d'ensemble de l'architecture

Ce document décrit l'architecture technique du bot d'équilibrage Polymarket, organisée selon la méthodologie Spec-Driven Development.

## Structure des composants

### 1. Frontend (React + TypeScript)

#### Pages principales
- **Dashboard** : Vue d'ensemble avec capital, positions actives, opportunités
- **Settings** : Configuration wallet, paramètres de trading, limites
- **History** : Historique des trades avec filtres et export
- **Scanner** : Opportunités détectées, activité whales, informations marché

#### State Management (Redux)
- **positions** : Positions actives et leur état
- **opportunities** : Opportunités détectées avec scores
- **config** : Configuration utilisateur
- **dashboard** : Données agrégées pour le dashboard
- **whales** : Données des whales trackés

#### Services
- **api.ts** : Client REST API (axios)
- **websocket.ts** : Client WebSocket pour mises à jour temps réel

### 2. Backend (FastAPI + Python)

#### API Layer
Endpoints REST organisés par domaine :
- `/api/positions` : Gestion des positions
- `/api/opportunities` : Opportunités détectées
- `/api/config` : Configuration
- `/api/dashboard` : Données dashboard
- `/api/whales` : Données whales
- `/api/info` : Informations marché
- `/ws` : WebSocket pour temps réel

#### Services métier

**Trading Engine** (`services/trading_engine.py`)
- Entrée de positions 50/50 YES/NO
- Liquidation de positions
- Fermeture manuelle
- Gestion des transactions

**Polymarket Client** (`services/polymarket_client.py`)
- Wrapper py-clob-client
- Récupération données marché
- Placement d'ordres
- Rate limiting

**Position Monitor** (`services/position_monitor.py`)
- Surveillance positions actives
- Détection divergence 30%
- Déclenchement liquidations automatiques

**Market Scanner** (`services/market_scanner.py`)
- Scan marchés Polymarket
- Filtrage marchés éligibles
- Détection opportunités

**Opportunity Scorer** (`services/opportunity_scorer.py`)
- Algorithme de scoring multi-facteurs
- Normalisation scores 1-10
- Facteurs : liquidité, volatilité, whales, news

**Whale Tracker** (`services/whale_tracker.py`)
- Identification wallets à fort volume
- Suivi positions whales
- Analyse patterns de trading

**Info Aggregator** (`services/info_aggregator.py`)
- Intégration APIs news
- Analyse données on-chain
- Détection tendances marché

### 3. Background Workers (Celery)

#### Tâches périodiques

**Scanner Task** (`tasks/scanner_task.py`)
- Fréquence : 5 minutes (configurable)
- Scan marchés + scoring opportunités
- Mise à jour base de données

**Monitor Task** (`tasks/monitor_task.py`)
- Fréquence : 30 secondes (configurable)
- Surveillance toutes positions actives
- Déclenchement liquidations

**Whale Task** (`tasks/whale_task.py`)
- Fréquence : 10 minutes (configurable)
- Mise à jour données whales
- Identification nouveaux whales

### 4. Data Layer (PostgreSQL)

#### Modèles de données

**Positions**
```python
- id: UUID (PK)
- market_id: String
- market_name: String
- entry_time: Timestamp
- entry_price_yes: Decimal
- entry_price_no: Decimal
- capital_yes: Decimal
- capital_no: Decimal
- current_price_yes: Decimal
- current_price_no: Decimal
- status: Enum (active, closed, liquidated)
- liquidated_side: Enum (yes, no, null)
- pnl: Decimal
```

**Opportunities**
```python
- id: UUID (PK)
- market_id: String
- market_name: String
- score: Integer (1-10)
- liquidity: Decimal
- whale_activity_score: Integer
- news_relevance_score: Integer
- volatility_score: Integer
- detected_at: Timestamp
```

**Config**
```python
- id: Integer (PK, singleton)
- wallet_credentials_encrypted: Text
- stop_loss: Decimal
- take_profit: Decimal
- capital_allocation_percent: Integer
- max_positions: Integer
- opportunity_threshold: Integer
```

**Trades**
```python
- id: UUID (PK)
- position_id: UUID (FK)
- side: Enum (yes, no)
- action: Enum (buy, sell)
- price: Decimal
- amount: Decimal
- transaction_hash: String
- executed_at: Timestamp
```

**Whales**
```python
- id: UUID (PK)
- wallet_address: String (unique)
- total_volume: Decimal
- trade_count: Integer
- markets_active: JSON
- last_trade_time: Timestamp
```

## Flux de données

### 1. Détection d'opportunité

```
Scanner Task (Celery)
    ↓
Market Scanner Service
    ↓
Opportunity Scorer Service
    ↓
Database (opportunities table)
    ↓
WebSocket → Frontend
```

### 2. Entrée de position

```
Frontend (Dashboard/Scanner)
    ↓
POST /api/positions
    ↓
Trading Engine Service
    ↓
Polymarket Client
    ↓
Blockchain Transaction
    ↓
Database (positions + trades tables)
    ↓
WebSocket → Frontend
```

### 3. Surveillance et liquidation

```
Monitor Task (Celery, every 30s)
    ↓
Position Monitor Service
    ↓
Détection divergence 30%
    ↓
Trading Engine Service (liquidate)
    ↓
Polymarket Client
    ↓
Database (update position)
    ↓
WebSocket → Frontend
```

### 4. Tracking whales

```
Whale Task (Celery)
    ↓
Whale Tracker Service
    ↓
Polymarket API / On-chain data
    ↓
Database (whales table)
    ↓
Factored into Opportunity Scorer
```

## Sécurité

### Chiffrement des credentials
- Utilisation de Fernet (cryptography)
- Clé de chiffrement dans variable d'environnement
- Credentials jamais en clair dans logs ou DB

### Gestion des erreurs
- Try/catch sur toutes opérations critiques
- Logging structuré sans données sensibles
- Retry logic avec exponential backoff

### Rate limiting
- Respect des limites API Polymarket
- Throttling des requêtes
- Cache pour données non-critiques

## Performance

### Optimisations base de données
- Index sur market_id, status, detected_at
- Connection pooling
- Requêtes optimisées avec SQLAlchemy

### Optimisations temps réel
- WebSocket pour push updates (pas de polling)
- Mises à jour incrémentales
- Batch updates pour positions multiples

### Scalabilité
- Celery workers horizontalement scalables
- Database read replicas possibles
- Redis pour cache et queue

## Déploiement

### Docker Compose
Services :
- `backend` : FastAPI app
- `frontend` : React app
- `worker` : Celery worker
- `beat` : Celery beat scheduler
- `db` : PostgreSQL
- `redis` : Redis

### Variables d'environnement
Voir `.env.example` pour configuration complète

### Migrations
Alembic pour gestion schéma DB :
```bash
alembic upgrade head
```

## Monitoring et Logs

### Logs structurés
- Format JSON pour parsing facile
- Niveaux : DEBUG, INFO, WARNING, ERROR
- Contexte : request_id, user_id, market_id

### Métriques clés
- Nombre positions actives
- Taux de succès liquidations
- Latence API Polymarket
- Taux d'erreur transactions

## Tests

### Tests unitaires
- Services métier isolés
- Mocking des dépendances externes
- Coverage > 80%

### Tests d'intégration
- Endpoints API
- Flux complets (entrée → monitoring → liquidation)
- Interactions base de données

### Tests end-to-end
- Scénarios utilisateur complets
- Tests browser avec Playwright/Selenium
- Validation UI + backend

## Évolutions futures

### Phase 1 (actuelle)
- ✅ Structure et architecture
- 🔄 Implémentation core features

### Phase 2
- Support multi-stratégies
- Backtesting sur données historiques
- Optimisation automatique paramètres

### Phase 3
- Notifications (email, Telegram)
- Mobile app
- Support autres prediction markets

## Références

- **Spec Kit** : https://github.com/github/spec-kit
- **Polymarket API** : https://docs.polymarket.com
- **py-clob-client** : https://github.com/Polymarket/py-clob-client
- **FastAPI** : https://fastapi.tiangolo.com
- **React** : https://react.dev
