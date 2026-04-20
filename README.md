# Git Analytics

Stack fullstack de collecte et d’analyse de données Git avec :

- Backend API (FastAPI)
- Frontend (React + Vite)
- Worker de traitement asynchrone
- PostgreSQL (base de données)
- Redis (queue / cache)

---

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

---

## Accès services

Frontend : http://localhost:5173  
Backend API : http://localhost:8000  
Swagger : http://localhost:8000/docs  

---

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

---

## Configuration Docker

Frontend : 5173  
Backend : 8000  
Postgres : 5432  
Redis : 6379  

---

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

---

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

---

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
