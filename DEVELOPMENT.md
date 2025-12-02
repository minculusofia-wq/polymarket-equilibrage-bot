# Guide de Développement - Polymarket Equilibrage Bot

## 🚀 Démarrage rapide

### Prérequis

- **Docker** et **Docker Compose** installés
- **Python 3.11+** (pour développement local)
- **Node.js 18+** (pour développement local)
- **Git** pour le versioning

### Installation initiale

1. **Cloner le repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/polymarket-equilibrage-bot.git
   cd polymarket-equilibrage-bot
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

4. **Vérifier que tout fonctionne**
   - Backend API : http://localhost:8000/docs
   - Frontend : http://localhost:3000
   - Base de données : localhost:5432
   - Redis : localhost:6379

---

## 🛠️ Développement local (sans Docker)

### Backend

1. **Créer un environnement virtuel**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer la base de données**
   ```bash
   # Assurez-vous que PostgreSQL tourne localement
   # Créer la base de données
   createdb polymarket_bot
   
   # Appliquer les migrations
   alembic upgrade head
   ```

4. **Lancer le serveur de développement**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Lancer les workers Celery** (dans un autre terminal)
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

6. **Lancer Celery Beat** (dans un autre terminal)
   ```bash
   celery -A app.celery_app beat --loglevel=info
   ```

### Frontend

1. **Installer les dépendances**
   ```bash
   cd frontend
   npm install
   ```

2. **Lancer le serveur de développement**
   ```bash
   npm start
   ```

3. **Accéder à l'application**
   - Ouvrir http://localhost:3000

---

## 📁 Structure du projet

```
.
├── backend/                    # Backend Python
│   ├── alembic/               # Migrations DB
│   ├── app/
│   │   ├── api/               # Endpoints REST
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── services/          # Logique métier
│   │   ├── tasks/             # Tâches Celery
│   │   ├── security/          # Chiffrement & sécurité
│   │   ├── main.py            # Point d'entrée FastAPI
│   │   ├── config.py          # Configuration
│   │   └── database.py        # Setup DB
│   ├── tests/                 # Tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── pages/             # Pages (Dashboard, Settings, etc.)
│   │   ├── components/        # Composants réutilisables
│   │   ├── store/             # Redux store
│   │   └── services/          # API client, WebSocket
│   ├── Dockerfile
│   └── package.json
│
├── .specify/                   # Spec Kit
│   ├── memory/
│   │   └── constitution.md
│   └── specs/
│       └── 001-polymarket-equilibrage-bot/
│           ├── spec.md        # Spécification fonctionnelle
│           └── plan.md        # Plan d'implémentation
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧪 Tests

### Tests backend

```bash
cd backend

# Tests unitaires
pytest tests/unit/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Tous les tests avec coverage
pytest --cov=app --cov-report=html

# Voir le rapport de coverage
open htmlcov/index.html
```

### Tests frontend

```bash
cd frontend

# Lancer les tests
npm test

# Tests avec coverage
npm test -- --coverage
```

### Linting et formatage

```bash
# Backend
cd backend
black .                    # Formatage
flake8 .                   # Linting
mypy app/                  # Type checking

# Frontend
cd frontend
npm run lint               # ESLint (si configuré)
```

---

## 🗄️ Base de données

### Migrations Alembic

```bash
cd backend

# Créer une nouvelle migration
alembic revision -m "description de la migration"

# Créer une migration automatique
alembic revision --autogenerate -m "add new table"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1

# Voir l'historique
alembic history

# Voir la version actuelle
alembic current
```

### Accéder à la base de données

```bash
# Via psql
psql -h localhost -U polymarket -d polymarket_bot

# Via Docker
docker exec -it polymarket_db psql -U polymarket -d polymarket_bot
```

---

## 🐛 Debugging

### Logs Docker

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Dernières 100 lignes
docker-compose logs --tail=100 backend
```

### Accéder à un conteneur

```bash
# Backend
docker exec -it polymarket_backend bash

# Base de données
docker exec -it polymarket_db psql -U polymarket -d polymarket_bot

# Redis
docker exec -it polymarket_redis redis-cli
```

### Redémarrer un service

```bash
docker-compose restart backend
docker-compose restart worker
```

---

## 🔧 Outils de développement

### API Documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Monitoring Redis

```bash
# Se connecter à Redis
docker exec -it polymarket_redis redis-cli

# Voir toutes les clés
KEYS *

# Voir les tâches Celery
LRANGE celery 0 -1
```

### Monitoring Celery

```bash
# Flower (monitoring web pour Celery)
# À ajouter dans docker-compose.yml si nécessaire
celery -A app.celery_app flower
# Accéder à http://localhost:5555
```

---

## 📝 Workflow de développement

### 1. Créer une nouvelle feature

```bash
# Créer une branche
git checkout -b feature/nom-de-la-feature

# Développer la feature
# ...

# Commiter les changements
git add .
git commit -m "feat: description de la feature"

# Pousser vers GitHub
git push origin feature/nom-de-la-feature

# Créer une Pull Request sur GitHub
```

### 2. Convention de commits

Utiliser [Conventional Commits](https://www.conventionalcommits.org/) :

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage, pas de changement de code
- `refactor:` refactoring
- `test:` ajout de tests
- `chore:` tâches de maintenance

### 3. Avant de commiter

```bash
# Vérifier le formatage
cd backend && black . && cd ..

# Lancer les tests
cd backend && pytest && cd ..
cd frontend && npm test && cd ..

# Vérifier que Docker build fonctionne
docker-compose build
```

---

## 🔐 Sécurité

### Générer une clé de chiffrement

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Ne jamais commiter

- ❌ Fichier `.env`
- ❌ Clés privées
- ❌ API keys
- ❌ Credentials de wallet

### Vérifier avant de pousser

```bash
# Vérifier qu'aucun secret n'est committé
git diff --cached | grep -i "private_key\|api_key\|password"
```

---

## 🚨 Problèmes courants

### Le backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier que la DB est prête
docker-compose logs db

# Reconstruire l'image
docker-compose build backend
docker-compose up -d backend
```

### Les migrations échouent

```bash
# Se connecter à la DB et vérifier
docker exec -it polymarket_db psql -U polymarket -d polymarket_bot

# Réinitialiser Alembic (ATTENTION: perte de données)
docker exec -it polymarket_backend alembic downgrade base
docker exec -it polymarket_backend alembic upgrade head
```

### Le frontend ne se connecte pas au backend

- Vérifier que `REACT_APP_API_URL` est correct dans `.env`
- Vérifier que le backend est accessible : http://localhost:8000/docs
- Vérifier les CORS dans le backend

---

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Material-UI](https://mui.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Polymarket API](https://docs.polymarket.com/)
- [py-clob-client](https://github.com/Polymarket/py-clob-client)

---

## 💡 Conseils

1. **Toujours travailler sur une branche** : Ne jamais développer directement sur `main`
2. **Tester localement** : Avant de pousser, vérifier que tout fonctionne
3. **Documenter** : Ajouter des docstrings et des commentaires
4. **Suivre le plan** : Se référer à `.specify/specs/001-polymarket-equilibrage-bot/plan.md`
5. **Utiliser les types** : TypeScript pour frontend, type hints Python pour backend

---

Bon développement ! 🚀
