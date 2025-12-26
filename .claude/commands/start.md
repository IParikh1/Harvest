---
allowed-tools: Bash(*)
description: Start the Harvest frontend and backend servers
---

# Start Harvest Servers

Start both the Harvest backend (FastAPI) and frontend (React/Vite) servers.

## Steps

1. Start the FastAPI backend on port 8000:
   ```bash
   cd /tmp/Harvest && python3 -m uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Run this in the background.

2. Start the React frontend on port 3000:
   ```bash
   cd /tmp/Harvest/frontend && npm run dev
   ```
   Run this in the background.

3. Report the URLs to the user:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

Both servers should be started as background tasks so the user can continue working.
