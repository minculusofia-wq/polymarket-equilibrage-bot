# Constitution du Projet : Polymarket Equilibrage Bot

## 1. Philosophie "UI First" & "High-End"
- L'interface utilisateur est la priorité absolue. Elle doit être visuellement impressionnante ("Wow effect"), fluide et intuitive.
- Utilisation obligatoire de **Shadcn/UI** et **Tailwind CSS**.
- Design réactif, mode sombre par défaut, animations subtiles.

## 2. Architecture Modulaire
- **Backend** : FastAPI + SQLAlchemy. Structure claire (Routers, Services, Schemas).
- **Frontend** : React. Composants atomiques et réutilisables. Séparation stricte entre la logique (Hooks) et la vue.

## 3. Stratégie "Mock-First"
- **Interdiction temporaire des appels API externes** (Polymarket, Web3, etc.).
- Tous les services doivent être développés avec des **Mocks** réalistes.
- Le backend doit servir des données générées (aléatoires mais cohérentes) pour simuler le marché, les mouvements de whales et le PnL.
- Cela permet de valider l'UX/UI et la logique de gestion des erreurs sans dépendre de la stabilité du réseau ou des clés API.

## 4. Spec-Driven Development
- Pas de code sans spécification préalable dans `.specify/specs/`.
- Chaque fonctionnalité doit être décrite, planifiée, puis implémentée.
