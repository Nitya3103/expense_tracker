# Expense Tracker API

Kharche record karne ka REST API, jisme total kisi bhi currency mein dekha ja sakta hai (live exchange rates se).

**Live:** https://expense-tracker-e2rl.onrender.com/docs

> Note: free tier par hosted hai, isliye 15 minute idle rehne ke baad service so jaati hai. Pehli request 30-50 second le sakti hai, uske baad normal speed.

## Stack

Python 3.12 · FastAPI · PostgreSQL (Neon) · SQLAlchemy · Docker · Render

## Features

- Expenses ka full CRUD, request validation ke saath
- Category aur amount par schema-level validation (negative amount reject hota hai)
- Total aur category-wise breakdown, kisi bhi currency mein
- Exchange rates Frankfurter API se (external integration, async)
- Graceful degradation: rate service down ho to API base currency mein jawab deti hai, crash nahi hoti
- Health endpoint jo database connectivity bhi check karta hai
- Har request ka structured logging (method, path, status, latency)
- Automated tests (pytest)
- Docker se containerized

## Local setup

```bash
git clone https://github.com/Nitya3103/expense-tracker.git
cd expense-tracker
uv sync
cp .env.example .env
```

`.env` mein apna `DATABASE_URL` daalo, phir:

```bash
uv run uvicorn app.main:app --reload
```

Docs: http://127.0.0.1:8000/docs

## Configuration

Saari config environment variables se aati hai. Koi secret code mein nahi hai.

| Variable | Zaroori | Kya hai |
| --- | --- | --- |
| `DATABASE_URL` | Haan | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `RATES_API_URL` | Nahi | Exchange rate API ka base URL |
| `BASE_CURRENCY` | Nahi | Jis currency mein amounts store hain (default: INR) |

## Tests

```bash
uv run pytest -v
```

## Docker

```bash
docker build -t expense-tracker .
docker run -p 8000:8000 --env-file .env expense-tracker
```

## API

| Method | Path | Kya karta hai |
| --- | --- | --- |
| `GET` | `/health` | Service aur database status |
| `POST` | `/expenses` | Naya
