# MCP Billing Demo (Polished)

This repo demonstrates agent-to-agent communication using an MCP server with a polished React UI built using Tailwind, shadcn-style components, and lucide-react icons.

## What you get

- Backend: MCP server exposing tools + FastAPI bridge
- SQLite DB seeded with mock invoices
- Agents: example agent + test client that call the MCP tools
- Frontend: React + Vite with shadcn-style components and icons
- Docker + docker-compose to run backend + frontend locally

## Quick start (local)

1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python billing_server.py
```

2. Frontend

```bash
cd frontend
npm install
npm run dev -- --host
```

3. Agents

```bash
cd agents
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python test_client.py
python agent_run.py
```

## Quick start (docker)

```bash
docker compose up --build
```

Then open `http://localhost:5173` for the frontend.

## Notes

- Replace `OPENAI_API_KEY` in backend `.env` for the agent to use OpenAI models.
- `download_invoice_pdf` is a demo stub. Replace with real file store for production.
