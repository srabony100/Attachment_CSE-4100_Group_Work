# Semantic Programming Question Search Monorepo

Semantic search app for programming questions using embeddings + FAISS.

## Production-style additions

- JWT auth with httpOnly cookies
- Role-based access control (`user`, `admin`)
- Admin panel routes for analytics, files, users, and logs
- SQLite persistence with SQLAlchemy
- Admin upload pipeline (`.txt`, `.md`, `.json`, `.pdf`, `.docx`) with chunking + reindex
- Search history for authenticated users
- Admin activity logging

## Monorepo layout

- `apps/web`: Next.js frontend
- `apps/api`: FastAPI backend
- `scripts`: dataset processing and embedding generation
- `docs`: architecture and setup notes
- `data`: raw/processed/index data assets

## Quick start

1. Copy env templates:
   - `cp .env.example .env`
   - `cp apps/web/.env.example apps/web/.env.local`
   - `cp apps/api/.env.example apps/api/.env`
2. Set required backend auth values in `apps/api/.env`:
   - `JWT_SECRET_KEY`
   - `SEED_ADMIN_EMAIL`
   - `SEED_ADMIN_PASSWORD`
2. Install frontend dependencies:
   - `cd apps/web && npm install`
3. Create Python environments and install dependencies:
   - `cd apps/api && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   - `cd scripts && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
4. Run services:
   - Frontend: `cd apps/web && npm run dev`
   - API: `cd apps/api && uvicorn app.main:app --reload --port 8000`

## Main routes

- Public: `/`, `/login`, `/admin/login`
- User protected: `/search`, `/history`
- Admin protected: `/admin/dashboard`, `/admin/files`, `/admin/users`, `/admin/logs`

See `docs/architecture.md` and `docs/setup.md` for full details.

## Deployment

- Deployment guide: `docs/deployment.md`
- Render config: `render.yaml`
- Railway config: `railway.json`
- Vercel config (web app): `apps/web/vercel.json`
- Production env examples:
   - `apps/api/.env.production.example`
   - `apps/web/.env.production.example`
