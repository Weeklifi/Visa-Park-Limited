# Visa Park Pyramid Marketplace

FastAPI backend implementing the BRD/SRS in `BRD_and_SRS_System_Requirements.md`:
a fixed 5-layer (11,111-user) referral pyramid, a "Vendor's Product" marketplace
with automated 180% pricing, and an upward commission payout engine.

## Stack
- Backend: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL 16 (LTREE) + Alembic + Argon2id + JWT.
- Frontend: React + TypeScript + Vite, in `frontend/`.

## Running everything with Docker (recommended)

The whole stack — Postgres, Redis, the FastAPI backend, and the Vite frontend dev
server — is defined in `docker-compose.yml`.

```
docker compose up -d --build
```

- API: `http://localhost:8000` (docs at `/docs`); migrations run automatically on
  container start.
- Frontend: `http://localhost:5173`, running Vite's dev server with hot reload —
  the `frontend/` folder is bind-mounted into the container, so edits on your
  machine reload in the browser without rebuilding the image.
- Postgres is published on host port `5433` (to avoid clashing with any local
  Postgres install on the default `5432`); Redis on `6379`.

`docker compose down` stops everything (add `-v` to also wipe the database volume).
`docker compose logs -f api` / `frontend` tail a service's logs.

Pages: home, login/register (invite-only — register with no referral code once to
create the Layer 0 root, then every subsequent registration needs a referral
code), dashboard (profile, referral code, invite link), Tours & Travel Packages
and Vendor's Product catalogs (the two nav-bar sections from FR-2.1), a vendor
product-listing form, and an orders page that walks an order through
confirm-payment → process-payout.

## Running without Docker

**Backend:**

1. Create a PostgreSQL 16 database (LTREE and uuid-ossp extensions are created by
   the first migration automatically — the DB role just needs `CREATE EXTENSION`
   privilege, or a superuser can pre-create them).
2. Copy `.env.example` to `.env` and adjust `DATABASE_URL` / JWT secrets.
3. Install dependencies and run migrations:

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # (or .venv/bin/pip on macOS/Linux)
.venv/Scripts/alembic upgrade head
```

4. Run the API:

```
.venv/Scripts/uvicorn app.main:app --reload
```

Docs at `http://localhost:8000/docs`. CORS is preconfigured for `http://localhost:5173`
(the Vite dev server).

**Frontend:**

```
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

App at `http://localhost:5173`.

## Key flows

- `POST /auth/register` — first call with no `parent_referral_code` creates the
  single Layer 0 root; every subsequent call requires a valid parent's
  `referral_code` and is placed at `parent.layer_level + 1`.
- `POST /auth/login` — returns a JWT (`Authorization: Bearer <token>`).
- `POST /products` — vendor supplies `base_price`; `retail_price` is always
  server-computed (`base_price * 1.80` for `VENDOR_PRODUCT`, passthrough for
  `TRAVEL_PACKAGE`).
- `POST /orders` — locks unit pricing from the product row at order-creation time.
- `POST /orders/{id}/mark-paid` — simulates payment confirmation (no real
  payment gateway in scope) so an order becomes eligible for payout.
- `POST /orders/{id}/process-payout` — run once an order is `PAID`; credits the
  vendor's base principal + 20% markup share, and splits the remaining 60% of
  markup equally among direct ancestors (bankers' rounding, remainder to the
  Layer 0 root), all as append-only `wallet_ledger` rows in one transaction.

## Notes on scope

- JWT defaults to HS256 for local dev simplicity; switch `JWT_ALGORITHM=RS256`
  and supply a real RSA key pair for production, per NFR 5.3.
- Redis-backed rate limiting and Celery async payout dispatch (BRD §4.1) are not
  wired up yet — `process-payout` currently runs synchronously in-request inside
  one DB transaction, which is correct but not yet decoupled onto a task queue.
- There is no real payment gateway; `mark-paid` is a stand-in so the payout flow
  is reachable end-to-end.
- No wallet balance/withdrawal UI yet — the frontend shows order status but not
  the `wallet_ledger` history; that endpoint isn't built yet either.
- No automated test suite yet.
