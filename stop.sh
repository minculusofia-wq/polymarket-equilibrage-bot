#!/bin/bash

# =====================================================
# 🛑 POLYMARKET BOT - ARRÊT COMPLET
# =====================================================

echo ""
echo "🛑 Arrêt du Bot Polymarket..."
echo ""

# Arrêter le backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm backend.pid
    echo "✓ Backend arrêté"
fi

# Arrêter le frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm frontend.pid
    echo "✓ Frontend arrêté"
fi

# Arrêter les processus par nom au cas où
pkill -f "uvicorn backend.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Arrêter Docker
docker-compose down
echo "✓ PostgreSQL + Redis arrêtés"

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║               ✅ BOT ARRÊTÉ PROPREMENT                ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
