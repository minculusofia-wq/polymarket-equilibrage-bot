# Guide de Contribution - Polymarket Equilibrage Bot

Merci de votre intérêt pour contribuer au Polymarket Equilibrage Bot ! Ce document explique comment contribuer efficacement au projet.

---

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Méthodologie Spec-Driven Development](#méthodologie-spec-driven-development)
- [Standards de code](#standards-de-code)
- [Processus de Pull Request](#processus-de-pull-request)
- [Reporting de bugs](#reporting-de-bugs)
- [Suggestions de fonctionnalités](#suggestions-de-fonctionnalités)

---

## Code de conduite

Ce projet suit un code de conduite simple :
- Soyez respectueux et professionnel
- Acceptez les critiques constructives
- Focalisez-vous sur ce qui est meilleur pour la communauté
- Montrez de l'empathie envers les autres contributeurs

---

## Comment contribuer

### 1. Fork et Clone

```bash
# Fork le repository sur GitHub
# Puis cloner votre fork
git clone https://github.com/YOUR_USERNAME/polymarket-equilibrage-bot.git
cd polymarket-equilibrage-bot

# Ajouter le repository original comme remote
git remote add upstream https://github.com/ORIGINAL_OWNER/polymarket-equilibrage-bot.git
```

### 2. Créer une branche

```bash
# Toujours créer une branche pour vos changements
git checkout -b feature/ma-nouvelle-feature
# ou
git checkout -b fix/correction-bug
```

### 3. Faire vos changements

Suivez les [standards de code](#standards-de-code) et la [méthodologie Spec-Driven](#méthodologie-spec-driven-development).

### 4. Tester

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### 5. Commiter

```bash
git add .
git commit -m "feat: description de la feature"
```

Utilisez [Conventional Commits](https://www.conventionalcommits.org/) :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance

### 6. Pousser et créer une PR

```bash
git push origin feature/ma-nouvelle-feature
```

Puis créer une Pull Request sur GitHub.

---

## Méthodologie Spec-Driven Development

Ce projet suit la méthodologie **Spec-Driven Development** avec Spec Kit.

### Workflow pour une nouvelle feature

1. **Créer/Modifier la spécification**
   - Éditer `.specify/specs/001-polymarket-equilibrage-bot/spec.md`
   - Ajouter les user stories et critères d'acceptation
   - Documenter les exigences fonctionnelles

2. **Créer/Modifier le plan technique**
   - Éditer `.specify/specs/001-polymarket-equilibrage-bot/plan.md`
   - Décrire l'architecture et l'implémentation
   - Lister les fichiers à créer/modifier

3. **Obtenir l'approbation**
   - Soumettre une PR avec les specs
   - Discuter et itérer sur les specs
   - Obtenir l'approbation avant d'implémenter

4. **Implémenter**
   - Suivre le plan technique
   - Créer les fichiers listés dans le plan
   - Respecter l'architecture définie

5. **Vérifier**
   - Tester selon le plan de vérification
   - Documenter les résultats
   - Créer un walkthrough si nécessaire

### Structure des specs

```
.specify/
├── memory/
│   └── constitution.md          # Principes du projet
└── specs/
    └── 001-polymarket-equilibrage-bot/
        ├── spec.md              # Spécification fonctionnelle
        └── plan.md              # Plan d'implémentation technique
```

---

## Standards de code

### Backend (Python)

#### Style

- Suivre [PEP 8](https://pep8.org/)
- Utiliser **Black** pour le formatage : `black .`
- Utiliser **flake8** pour le linting : `flake8 .`
- Utiliser **mypy** pour le type checking : `mypy app/`

#### Type hints

```python
def calculate_pnl(entry_price: float, current_price: float, capital: float) -> float:
    """Calculate profit/loss for a position.
    
    Args:
        entry_price: Entry price for the position
        current_price: Current market price
        capital: Capital allocated to position
        
    Returns:
        Profit or loss amount
    """
    return (current_price - entry_price) * capital
```

#### Docstrings

Utiliser le format Google :

```python
def enter_position(market_id: str, capital: float, ratio_yes: float, ratio_no: float) -> Position:
    """Enter a new position on a market.
    
    Args:
        market_id: Polymarket market identifier
        capital: Total capital to allocate
        ratio_yes: Percentage allocated to YES (0-100)
        ratio_no: Percentage allocated to NO (0-100)
        
    Returns:
        Created position object
        
    Raises:
        ValueError: If ratios don't sum to 100
        InsufficientFundsError: If wallet balance is insufficient
    """
    pass
```

#### Tests

```python
import pytest
from app.services.trading_engine import TradingEngine

def test_enter_position_50_50():
    """Test entering a 50/50 position."""
    engine = TradingEngine()
    position = engine.enter_position(
        market_id="test-market",
        capital=100.0,
        ratio_yes=50.0,
        ratio_no=50.0
    )
    assert position.capital_yes == 50.0
    assert position.capital_no == 50.0
```

### Frontend (TypeScript/React)

#### Style

- Utiliser **TypeScript** strict mode
- Suivre les conventions React
- Utiliser **ESLint** (si configuré)

#### Composants

```typescript
import React from 'react';

interface PositionCardProps {
  position: Position;
  onClose: (id: string) => void;
}

export const PositionCard: React.FC<PositionCardProps> = ({ position, onClose }) => {
  return (
    <div className="position-card">
      <h3>{position.marketName}</h3>
      <button onClick={() => onClose(position.id)}>Close</button>
    </div>
  );
};
```

#### Types

```typescript
// Définir les types pour toutes les entités
interface Position {
  id: string;
  marketId: string;
  marketName: string;
  entryPriceYes: number;
  entryPriceNo: number;
  capitalYes: number;
  capitalNo: number;
  status: 'active' | 'closed' | 'liquidated';
}
```

---

## Processus de Pull Request

### Checklist avant de soumettre

- [ ] Code formaté (Black pour Python, Prettier pour TypeScript)
- [ ] Tests passent (`pytest` et `npm test`)
- [ ] Pas de warnings de linting
- [ ] Documentation à jour (docstrings, README si nécessaire)
- [ ] Commits suivent Conventional Commits
- [ ] Specs mises à jour si feature majeure
- [ ] Pas de secrets ou credentials dans le code

### Template de PR

```markdown
## Description
Brève description des changements

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Specs
- Lien vers la spec : `.specify/specs/...`
- User story : US-X.X

## Tests
- [ ] Tests unitaires ajoutés/modifiés
- [ ] Tests d'intégration ajoutés/modifiés
- [ ] Tests manuels effectués

## Checklist
- [ ] Code formaté
- [ ] Tests passent
- [ ] Documentation à jour
- [ ] Pas de secrets committés
```

### Review process

1. **Automated checks** : CI/CD vérifie les tests et le linting
2. **Code review** : Au moins 1 approbation requise
3. **Spec review** : Vérifier que l'implémentation suit le plan
4. **Merge** : Squash and merge vers `main`

---

## Reporting de bugs

### Template d'issue pour bug

```markdown
## Description du bug
Description claire et concise du bug

## Reproduction
Étapes pour reproduire :
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

## Comportement attendu
Ce qui devrait se passer

## Comportement actuel
Ce qui se passe réellement

## Screenshots
Si applicable

## Environnement
- OS: [e.g. macOS 14.0]
- Docker version: [e.g. 24.0.0]
- Browser: [e.g. Chrome 120]

## Logs
```
Coller les logs pertinents
```

## Contexte additionnel
Toute autre information utile
```

---

## Suggestions de fonctionnalités

### Template d'issue pour feature request

```markdown
## Problème à résoudre
Quel problème cette feature résout-elle ?

## Solution proposée
Description de la solution

## Alternatives considérées
Autres approches possibles

## User Story
**En tant que** [type d'utilisateur]
**Je veux** [action]
**Afin de** [bénéfice]

## Critères d'acceptation
- [ ] Critère 1
- [ ] Critère 2

## Impact
- Complexité estimée : [Faible/Moyenne/Élevée]
- Priorité : [Basse/Moyenne/Haute]
```

### Processus

1. **Créer une issue** avec le template
2. **Discussion** : L'équipe discute de la pertinence
3. **Spec** : Si approuvée, créer une spec dans `.specify/specs/`
4. **Plan** : Créer un plan d'implémentation
5. **Implémentation** : Suivre le processus normal de contribution

---

## Questions ?

- Ouvrir une **Discussion** sur GitHub pour les questions générales
- Ouvrir une **Issue** pour les bugs ou feature requests
- Consulter la **documentation** dans `.specify/` et les fichiers `*.md`

---

Merci de contribuer au Polymarket Equilibrage Bot ! 🚀
