# ⚖️ Polymarket Equilibrage Bot (v0.2.1)

Bot de trading autonome haute performance pour Polymarket. Détecte les opportunités d'arbitrage et de value trading en temps réel.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![React](https://img.shields.io/badge/frontend-React-61dafb)

## 🚀 Fonctionnalités Clés (v0.2.1)

- **Scanner 2.0 (Optimisé)** : Algo de détection amélioré (Volume Effectif + Liquidité) avec cache intelligent. Détecte les opportunités "invisibles" (long-term bets).
- **Scanner Avancé (Asyncio)** : Analyse parallèle de 50+ marchés simultanément (2s / 100 marchés).
- **Scoring Multi-Critères** : Algorithme propriétaire basés sur 5 facteurs (Divergence, Volume, Liquidité, Timing, Activité).
- **Trading Autonome** : Exécution automatique des ordres sur la blockchain (via API CLOB) avec gestion d'erreurs.
- **Temps Réel (WebSockets)** : Mises à jour instantanées du P&L, des positions et du scanner sur le dashboard.
- **Sécurité** : Gestion stricte des trades (Cost Protection check), Panic Button, et Repair Script intégré.
- **Dashboard Complet** : Interface React moderne pour le monitoring et le contrôle.

## 🛠 Prérequis

- **Docker** & **Docker Compose**
- **Clé API Polymarket** & **Clé Privée Wallet** (pour le trading réel)

## 📦 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/minculusofia-wq/polymarket-equilibrage-bot.git
   cd polymarket-equilibrage-bot
   ```

2. **Configurer l'environnement**
   Copiez le fichier exemple et remplissez vos identifiants :
   ```bash
   cp .env.example .env
   ```
   *Note : Le bot ne trade PAS si les clés ne sont pas configurées.*

3. **Démarrer le Bot**
   Utilisez le script unifié :
   ```bash
   ./start.sh
   ```
   
   Le script va :
   - Lancer le Backend (FastAPI).
   - Lancer le Frontend (React/Vite).

4. **En cas de problème (Base de données)**
   Si vous rencontrez des erreurs de configuration ou de base de données :
   ```bash
   python3 backend/repair_config.py
   ```
   *Attention : Cela réinitialise la configuration par défaut.*

## 🖥 Interface

Accédez au dashboard sur : **[http://localhost:3000](http://localhost:3000)**

### Configurer le Trading
Par défaut, **tous les paramètres sont à 0** pour éviter les accidents.
1. Allez dans l'onglet **Settings**.
2. Définissez votre capital maximum par trade.
3. Configurez vos Stop-Loss et Take-Profit.
4. Activez le trading automatique.

### Contrôles
- **▶️ Start** : Lance la boucle de trading autonome.
- **⏸️ Pause** : Suspend l'ouverture de nouvelles positions (le monitoring reste actif).
- **🚨 PANIC** : Ferme immédiatement toutes les positions ouvertes.

## 🏗 Architecture

- **Backend** : FastAPI, SQLAlchemy (PostgreSQL), Redis (Cache), Asyncio (Parallel processing).
- **Frontend** : React, Vite, Zustand (State), Recharts (Graphiques).
- **Protocole** : WebSockets pour le streaming de données temps réel.

## ⚠️ Avertissement

Ce logiciel est fourni à titre expérimental. Le trading de crypto-monnaies comporte des risques financiers importants. L'utilisation de ce bot est à vos propres risques.

## 📄 Licence

MIT License.
