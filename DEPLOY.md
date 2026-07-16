# Deploy — Vercel (web) + Railway (API + Postgres)

Educational paper-simulation terminal. No real trading. Live prices via yfinance
may be rate-limited from datacenter IPs — the app falls back to mock with a
warning, so the UI never breaks.

## 1. Backend + database on Railway

1. Create a new Railway project → **Deploy from GitHub repo** → `smellywesley/Hedge-Fund-Agent`.
2. Add a **PostgreSQL** plugin to the project. Railway sets `DATABASE_URL` automatically
   (the app normalizes `postgres://` → `postgresql://`).
3. Railway auto-detects Python (root `requirements.txt` + `runtime.txt`) and runs the
   root `Procfile`:
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir apps/api`
4. Set one variable once you have the Vercel URL (step 2):
   `ALLOWED_ORIGINS = https://<your-app>.vercel.app`
5. Deploy. Confirm `https://<railway-app>.up.railway.app/api/health` returns `{"status":"ok"}`.
   First boot seeds the DB and backfills prices (network permitting).

## 2. Frontend on Vercel

1. Import the same GitHub repo into Vercel.
2. **Root Directory:** `apps/web` (Vercel then auto-detects Next.js).
3. Environment variable: `NEXT_PUBLIC_API_URL = https://<railway-app>.up.railway.app`
4. Deploy → open `https://<your-app>.vercel.app` (redirects to `/markets`).

## 3. After first deploy

- Back in Railway, set `ALLOWED_ORIGINS` to the real Vercel URL and redeploy the API
  (CORS is env-driven, no code change).
- The paper fund is a single shared instance (no user accounts yet) — fine for personal
  use; add auth before sharing widely.

## Optional keys (set as Railway env vars — each activates a feature)

| Env var | Enables | Without it |
|---|---|---|
| `ANTHROPIC_API_KEY` | the live **Run Research** button (calls Claude; your tokens per press) | button returns "not configured" |
| `RESEARCH_MODEL` | override the model id (default `claude-sonnet-4-5`) | uses the default |
| `FMP_API_KEY` | real `growth_momentum` from analyst estimates (free tier) | component stays mock |
| `FRED_API_KEY` | richer macro series | regime already works from yfinance |

All are blocked-not-faked when absent — the app never fabricates data, so
missing keys never break the deploy.

## Notes / known limits in production

- **yfinance throttling:** datacenter IPs get rate-limited by Yahoo more than home IPs.
  Live data may intermittently fall back to mock (shown via the source badges). A paid
  data provider (or OpenBB) is the upgrade path.
- **DB migrations:** the app calls `create_all` on boot (no Alembic yet) — fine for the
  current schema; add migrations before changing tables in production.
- **Disclaimers:** every AI/score/backtest panel is labeled educational / paper
  simulation. Keep them; this is not investment advice and places no real trades.
