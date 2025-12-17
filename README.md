# Cig Kofte Yonetim Sistemi

Restoran yonetim sistemi MVP - Vue 3 + FastAPI + PostgreSQL

## Hizli Baslangic (Docker)

```bash
# Projeyi calistir
docker-compose up -d

# Migration ve seed data (ilk kurulumda)
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed.py
```

Sistem calistiktan sonra:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Giris Bilgileri

```
Email: admin@cigkofte.com
Sifre: admin123
```

## Gelistirme (Docker olmadan)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL calistir (port 5433)
# Migration
alembic upgrade head

# Seed data
python seed.py

# Backend calistir
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Ozellikler (MVP)

- [x] Login/Logout
- [x] Dashboard (KPI'lar)
- [x] POS (Siparis olusturma)
- [x] Siparisler listesi
- [x] Mal alimi girisi
- [x] Gider girisi

## Tech Stack

- Frontend: Vue 3, Tailwind CSS, Pinia, Vue Router
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Infra: Docker, Docker Compose
