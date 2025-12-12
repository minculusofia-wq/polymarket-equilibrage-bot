# Spécification 001 : Structure UI & Mock Data

## Objectif
Mettre en place l'interface utilisateur complète (Dashboard) et les services backend mockés pour valider l'UX avant toute intégration réelle.

## 1. Interface Utilisateur (Frontend)
L'application est un Dashboard divisé en 4 onglets principaux.

### Onglet 1 : Dashboard (Command Center)
Le cœur de l'action.
- **Top Cards** :
  - `Solde Total` : Montant en USDC (Wallet + Engagé).
  - `PnL Global` : Profit/Perte total en % et valeur absolue (Vert/Rouge).
  - `Positions Actives` : Compteur.
- **Calculateur de Ratios** :
  - Widget interactif.
  - Input : Montant investissement (ex: 100$).
  - Output : Répartition automatique (ex: 60$ YES / 40$ NO) selon config.
- **Tableau des Positions** :
  - Liste des paris en cours.
  - Colonnes : Marché (Titre + Icône), Ratio (ex: 60/40), PnL (Live Mock), SL/TP (Valeurs).
  - **Action** : Bouton "PANIC CLOSE" (Rouge, Icone Danger) par ligne. Fermeture immédiate de la position spécifique.

### Onglet 2 : Scanner
Outil de surveillance.
- **Whale Tracker** :
  - Feed défilant (type ticker ou liste).
  - Affiche : "Whale X a acheté 50k$ sur Trump (YES)".
- **Opportunités** :
  - Tableau triable.
  - Colonnes : Marché, Score (1-10), Volatilité (Haute/Moyenne/Basse), Action (Bouton "Analyser").

### Onglet 3 : Paramètres
Configuration du bot.
- **Wallet** :
  - Champs : Adresse Publique, Clé Privée (Masquée *****).
  - Bouton "Sauvegarder" (Chiffrement local simulé).
- **Config Trading** :
  - Ratios par défaut (Slider ou Input).
  - Stop-Loss Global (%) et Take-Profit Global (%).

### Onglet 4 : Historique
- Liste simple des trades passés.
- Colonnes : Date, Marché, Résultat (+/- $), Statut (Win/Loss).

## 2. Données Mockées (Backend)
Le backend doit simuler une activité réaliste.

### Structure des Objets (JSON Schemas)

**Position**
```json
{
  "id": "pos_123",
  "market_title": "Will Trump win 2024?",
  "market_image": "url...",
  "entry_price_yes": 0.60,
  "current_price_yes": 0.62,
  "pnl_percent": 3.33,
  "pnl_value": 20.0,
  "status": "OPEN"
}
```

**WhaleMovement**
```json
{
  "id": "wm_456",
  "timestamp": "2023-10-27T10:00:00Z",
  "market": "Bitcoin > 100k in 2024",
  "amount": 50000,
  "side": "YES",
  "whale_label": "Whale #1"
}
```

**Opportunity**
```json
{
  "id": "opp_789",
  "market": "Ethereum ETF Approval",
  "score": 8.5,
  "volatility": "HIGH"
}
```
