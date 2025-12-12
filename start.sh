#!/bin/bash

# =====================================================
# 🚀 POLYMARKET BOT - DÉMARRAGE TOUT EN UN
# =====================================================

set -e

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║        ⚖️  POLYMARKET EQUILIBRAGE BOT                 ║"
echo "║              Démarrage Automatique                     ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Chemin du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Vérifier Docker
echo -e "${YELLOW}[1/6]${NC} Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker OK${NC}"

# Créer .env si nécessaire
echo -e "${YELLOW}[2/6]${NC} Configuration de l'environnement..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Fichier .env créé${NC}"
else
    echo -e "${GREEN}✓ Fichier .env existant${NC}"
fi

# Démarrer PostgreSQL et Redis
echo -e "${YELLOW}[3/6]${NC} Démarrage PostgreSQL + Redis..."
docker-compose up -d postgres redis 2>/dev/null
sleep 3
echo -e "${GREEN}✓ Base de données prête${NC}"

# Setup Backend
echo -e "${YELLOW}[4/6]${NC} Configuration du Backend..."
cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

echo -e "${GREEN}✓ Backend configuré${NC}"

# Démarrer Backend
echo -e "${YELLOW}[5/6]${NC} Démarrage du Backend (port 8000)..."
export PYTHONPATH="$SCRIPT_DIR"
nohup python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
sleep 2
echo -e "${GREEN}✓ Backend démarré (PID: $BACKEND_PID)${NC}"
cd ..

# Démarrer Frontend
echo -e "${YELLOW}[6/6]${NC} Démarrage du Frontend (port 3000)..."
cd frontend
npm install --silent 2>/dev/null
nohup npm run dev -- --port 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
sleep 3
echo -e "${GREEN}✓ Frontend démarré (PID: $FRONTEND_PID)${NC}"
cd ..

# Afficher les URLs
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║               🎉 BOT DÉMARRÉ AVEC SUCCÈS !             ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║   📊 Dashboard:    http://localhost:3000              ║"
echo "║   🔧 API Backend:  http://localhost:8000              ║"
echo "║   📚 API Docs:     http://localhost:8000/docs         ║"
echo "║                                                        ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║   Pour arrêter:    ./stop.sh                          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Ouvrir le navigateur
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 2
    open http://localhost:3000
fi

echo -e "${GREEN}Le bot est accessible sur http://localhost:3000${NC}"
echo ""
