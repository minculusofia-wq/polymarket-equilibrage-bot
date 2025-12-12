# Plan Technique : UI & Mocks

## 1. Backend (FastAPI)
Création d'une API REST simple servie par FastAPI. Pas de DB réelle pour l'instant (In-Memory ou JSON statique).

### Endpoints Requis
Tous les endpoints retournent des données mockées dynamiques (valeurs qui changent légèrement à chaque appel pour simuler la vie).

- `GET /api/status` : État global du bot (Running/Paused) et Solde.
- `GET /api/positions` : Liste des positions actives.
- `POST /api/positions/{id}/close` : Simule la fermeture (supprime de la liste en mémoire).
- `GET /api/scanner/whales` : Retourne les 10 derniers mouvements de whales.
- `GET /api/scanner/opportunities` : Retourne les opportunités détectées.
- `GET /api/history` : Historique des trades.
- `GET /api/config` & `POST /api/config` : Lecture/Écriture de la config (Wallet, Ratios).

### Structure Dossiers Backend
```
backend/
  main.py
  routers/
    dashboard.py
    scanner.py
    settings.py
  services/
    mock_generator.py  <-- Cœur de la simulation
  schemas/
    ...
```

## 2. Frontend (React + Vite)
Utilisation de Shadcn/UI pour les composants.

### Arborescence Composants
```
src/
  components/
    ui/             <-- Shadcn components (Card, Button, Table, Input...)
    layout/
      MainLayout.tsx
      Navbar.tsx
    dashboard/
      StatCard.tsx
      CalculatorWidget.tsx
      PositionsTable.tsx
      PanicButton.tsx
    scanner/
      WhaleFeed.tsx
      OpportunitiesTable.tsx
    settings/
      WalletForm.tsx
      TradingConfig.tsx
  pages/
    DashboardPage.tsx
    ScannerPage.tsx
    SettingsPage.tsx
    HistoryPage.tsx
  services/
    api.ts          <-- Appels Axios vers le backend
```

## 3. Étapes d'Implémentation
1.  **Setup Backend** : Init FastAPI, création du `mock_generator`.
2.  **Setup Frontend** : Init Vite + React, install Tailwind + Shadcn.
3.  **Dev Dashboard** : Intégration des composants Dashboard + Connexion API Mock.
4.  **Dev Scanner** : Intégration Whale Tracker + Opportunités.
5.  **Dev Settings** : Formulaires et persistance mockée.
6.  **Validation** : Vérification de la fluidité et du "Look & Feel".
