#!/bin/bash

# Script de lancement rapide pour le développement local (sans Docker)

echo "🚀 Démarrage du Bot Polymarket (Mode Développement)"
echo ""

# Vérifier si .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé. Copie de .env.example..."
    cp .env.example .env
    echo "✅ Fichier .env créé. Veuillez le configurer avec vos credentials."
    echo ""
fi

# Démarrer PostgreSQL et Redis avec Docker
echo "📦 Démarrage de PostgreSQL et Redis..."
docker-compose up -d postgres redis

# Attendre que les services soient prêts
echo "⏳ Attente des services..."
sleep 5

# Activer l'environnement virtuel backend
echo "🐍 Configuration de l'environnement Python..."
cd backend

if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances Python..."
pip install -r requirements.txt

# Lancer les migrations
echo "🗄️  Exécution des migrations..."
alembic upgrade head

# Démarrer le backend
echo "🔧 Démarrage du backend..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Démarrer le frontend
echo "⚛️  Démarrage du frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Bot démarré avec succès!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Pour arrêter: Ctrl+C puis exécuter ./stop.sh"
echo ""

# Attendre les processus
wait $BACKEND_PID $FRONTEND_PID
