# Guide de Déploiement - Polymarket Equilibrage Bot

Ce guide explique comment déployer le Polymarket Equilibrage Bot en production.

---

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Déploiement local (production-like)](#déploiement-local-production-like)
- [Déploiement sur VPS](#déploiement-sur-vps)
- [Déploiement sur cloud](#déploiement-sur-cloud)
- [Configuration de production](#configuration-de-production)
- [Monitoring et maintenance](#monitoring-et-maintenance)
- [Backup et récupération](#backup-et-récupération)
- [Sécurité](#sécurité)

---

## Prérequis

### Serveur

- **OS** : Ubuntu 22.04 LTS (recommandé) ou macOS
- **RAM** : Minimum 4GB, recommandé 8GB
- **CPU** : Minimum 2 cores, recommandé 4 cores
- **Stockage** : Minimum 20GB SSD
- **Réseau** : Connexion stable avec IP publique (pour VPS)

### Logiciels

- Docker 24.0+
- Docker Compose 2.0+
- Git
- (Optionnel) Nginx pour reverse proxy

---

## Déploiement local (production-like)

Pour tester en mode production sur votre machine locale :

### 1. Préparer l'environnement

```bash
# Cloner le repository
git clone https://github.com/YOUR_USERNAME/polymarket-equilibrage-bot.git
cd polymarket-equilibrage-bot

# Créer le fichier .env
cp .env.example .env
```

### 2. Configurer .env pour production

```bash
# Éditer .env
nano .env
```

**Variables critiques à configurer :**

```bash
# Database (utiliser un mot de passe fort)
DATABASE_URL=postgresql://polymarket:STRONG_PASSWORD@db:5432/polymarket_bot

# Polymarket (vos vraies credentials)
POLYMARKET_API_KEY=your_real_api_key
POLYMARKET_PRIVATE_KEY=your_real_private_key

# Security (générer de vraies clés)
ENCRYPTION_KEY=<générer avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
SECRET_KEY=<générer avec: openssl rand -hex 32>

# News API (optionnel)
NEWS_API_KEY=your_newsapi_key

# Logging
LOG_LEVEL=INFO
```

### 3. Build et lancer

```bash
# Build les images
docker-compose build

# Lancer en mode détaché
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 4. Initialiser la base de données

```bash
# Appliquer les migrations
docker exec -it polymarket_backend alembic upgrade head

# Vérifier
docker exec -it polymarket_db psql -U polymarket -d polymarket_bot -c "\dt"
```

### 5. Vérifier le déploiement

- Backend : http://localhost:8000/docs
- Frontend : http://localhost:3000
- Vérifier les logs : `docker-compose logs -f`

---

## Déploiement sur VPS

### 1. Préparer le VPS

```bash
# Se connecter au VPS
ssh user@your-vps-ip

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installer Docker Compose
sudo apt install docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
# Se déconnecter et reconnecter pour appliquer
```

### 2. Configurer le firewall

```bash
# Installer ufw
sudo apt install ufw

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP/HTTPS (si vous utilisez Nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le firewall
sudo ufw enable
```

### 3. Cloner et configurer

```bash
# Cloner le repository
git clone https://github.com/YOUR_USERNAME/polymarket-equilibrage-bot.git
cd polymarket-equilibrage-bot

# Configurer .env (voir section précédente)
cp .env.example .env
nano .env
```

### 4. Lancer l'application

```bash
# Build et lancer
docker-compose up -d

# Vérifier
docker-compose ps
docker-compose logs -f
```

### 5. Configurer Nginx (optionnel mais recommandé)

```bash
# Installer Nginx
sudo apt install nginx

# Créer la configuration
sudo nano /etc/nginx/sites-available/polymarket-bot
```

**Configuration Nginx :**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Activer la configuration
sudo ln -s /etc/nginx/sites-available/polymarket-bot /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### 6. Configurer SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d your-domain.com

# Renouvellement automatique (déjà configuré par défaut)
sudo certbot renew --dry-run
```

---

## Déploiement sur cloud

### AWS (EC2)

1. **Créer une instance EC2**
   - AMI : Ubuntu 22.04 LTS
   - Type : t3.medium (ou plus)
   - Stockage : 30GB SSD
   - Security Group : Autoriser ports 22, 80, 443

2. **Suivre les étapes VPS** ci-dessus

3. **Configurer RDS** (optionnel, pour DB managée)
   - Créer une instance PostgreSQL RDS
   - Modifier `DATABASE_URL` dans `.env`

### Google Cloud (Compute Engine)

1. **Créer une VM**
   - Image : Ubuntu 22.04 LTS
   - Machine type : e2-medium (ou plus)
   - Disque : 30GB SSD

2. **Suivre les étapes VPS** ci-dessus

### DigitalOcean (Droplet)

1. **Créer un Droplet**
   - Image : Ubuntu 22.04 LTS
   - Plan : Basic, 4GB RAM / 2 vCPUs
   - Datacenter : Choisir le plus proche

2. **Suivre les étapes VPS** ci-dessus

---

## Configuration de production

### docker-compose.prod.yml

Créer un fichier `docker-compose.prod.yml` pour la production :

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - LOG_LEVEL=WARNING
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  worker:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  beat:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    restart: always
    command: npm run build && npx serve -s build
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
```

**Lancer en production :**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Monitoring et maintenance

### Logs

```bash
# Voir tous les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend

# Logs avec timestamp
docker-compose logs -f --timestamps

# Dernières 100 lignes
docker-compose logs --tail=100 backend
```

### Monitoring des ressources

```bash
# Utilisation CPU/RAM des conteneurs
docker stats

# Espace disque
df -h

# Logs Docker
sudo journalctl -u docker.service
```

### Mises à jour

```bash
# Pull les derniers changements
git pull origin main

# Rebuild et redémarrer
docker-compose build
docker-compose up -d

# Appliquer les migrations
docker exec -it polymarket_backend alembic upgrade head
```

### Redémarrage

```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend
```

---

## Backup et récupération

### Backup de la base de données

```bash
# Créer un backup
docker exec polymarket_db pg_dump -U polymarket polymarket_bot > backup_$(date +%Y%m%d_%H%M%S).sql

# Ou via script automatisé
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec polymarket_db pg_dump -U polymarket polymarket_bot > "$BACKUP_DIR/backup_$DATE.sql"
# Garder seulement les 7 derniers backups
ls -t $BACKUP_DIR/backup_*.sql | tail -n +8 | xargs rm -f
EOF

chmod +x backup.sh

# Ajouter au crontab (backup quotidien à 2h du matin)
crontab -e
# Ajouter: 0 2 * * * /path/to/backup.sh
```

### Restauration

```bash
# Restaurer depuis un backup
docker exec -i polymarket_db psql -U polymarket polymarket_bot < backup_20240101_020000.sql
```

---

## Sécurité

### Checklist de sécurité

- [ ] Utiliser des mots de passe forts pour la DB
- [ ] Générer de vraies clés de chiffrement (pas celles de .env.example)
- [ ] Activer le firewall (ufw)
- [ ] Utiliser HTTPS (Let's Encrypt)
- [ ] Ne pas exposer les ports DB/Redis publiquement
- [ ] Mettre à jour régulièrement le système et Docker
- [ ] Limiter l'accès SSH (clés SSH uniquement, pas de password)
- [ ] Configurer fail2ban pour protéger SSH
- [ ] Sauvegarder régulièrement la base de données
- [ ] Monitorer les logs pour activité suspecte

### Fail2ban (protection SSH)

```bash
# Installer fail2ban
sudo apt install fail2ban

# Configurer
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Activer
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Troubleshooting

### Le bot ne trade pas

1. Vérifier les logs : `docker-compose logs -f worker`
2. Vérifier la configuration dans Settings
3. Vérifier le solde du wallet
4. Vérifier la connexion à l'API Polymarket

### Erreurs de base de données

```bash
# Vérifier que la DB est accessible
docker exec -it polymarket_db psql -U polymarket -d polymarket_bot

# Vérifier les migrations
docker exec -it polymarket_backend alembic current
docker exec -it polymarket_backend alembic history
```

### Problèmes de performance

```bash
# Vérifier l'utilisation des ressources
docker stats

# Augmenter les ressources si nécessaire
# Modifier docker-compose.yml pour ajouter des limites
```

---

## Support

Pour toute question ou problème :
- Consulter les logs : `docker-compose logs -f`
- Vérifier la documentation dans `.specify/`
- Ouvrir une issue sur GitHub

---

Bon déploiement ! 🚀
