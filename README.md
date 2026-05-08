# Git Analytics

Stack fullstack de collecte et d’analyse de données Git avec :

- Backend API (FastAPI)
- Frontend (React + Vite)
- Worker de traitement asynchrone
- PostgreSQL (base de données)
- Redis (queue / cache)

## Objectif

Ce projet a pour objectif d’analyser des repositories Git afin d’en extraire des indicateurs de qualité, de santé et de risque.

L’idée est de fournir une vision rapide et synthétique d’un projet logiciel à partir de son historique Git, sans avoir à lire les commits ou le code source.

## Fonctionnement

Le système fonctionne en pipeline automatisé :

- L’utilisateur soumet une URL de repository Git
- Le backend valide l’accessibilité du repository
- Le repository est enregistré en base de données
- Une tâche d’analyse est envoyée dans une queue Redis
- Le worker exécute l’analyse :
  1. clonage du repository
  2. lecture de l’historique Git
  3. calcul des métriques
  4. génération des graphes et statistiques
- Les résultats sont stockés en base de données
- Le frontend affiche les données de manière interactive.

## Architecture

```bash
frontend (Vite React)
        ↓
backend (FastAPI)
        ↓
Redis + Worker
        ↓
PostgreSQL
```

---

## Lancer le projet

### 1. Cloner le projet

```bash
git clone <repo-url>
cd git-analytics
```

---

### 2. Lancer avec Docker

```bash
docker compose up
```

---

### Mode développement recommandé

```bash
docker compose down
docker compose up --build
```

## Accès services

Frontend : http://localhost:5173  
Backend API : http://localhost:8000  
Swagger : http://localhost:8000/docs  


## Stack technique

Frontend :

- React
- Vite
- TypeScript

Backend :

- FastAPI
- Uvicorn

Worker :

- Python async processing

Infra :

- PostgreSQL 15
- Redis 7
- Docker / Docker Compose

## Configuration Docker

Frontend : 5173  
Backend : 8000  
Postgres : 5432  
Redis : 6379  

## Variables d’environnement

Backend :

```bash
PYTHONUNBUFFERED=1  
DATABASE_URL=postgresql://user:password@db:5432/gitanalytics  
REDIS_URL=redis://redis:6379  
```

Frontend :

```bash
VITE_API_URL=http://localhost:8000  
```

## Développement

Frontend :

```bash
cd frontend
npm install
npm run dev
```

Backend :

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Commandes Docker utiles

Stop :

```bash
docker compose down
```

Reset complet :

```bash
docker compose down -v
docker compose up --build
```

Logs :

```bash
docker compose logs -f
```
