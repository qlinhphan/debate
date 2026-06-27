# Frontend (React + Vite)

Quick scaffold for a Vite + React frontend that connects to the `back` API.

Run:

```bash
cd front
npm install
npm run dev
```

Notes:
- The Vite dev server proxies `/api` to `http://localhost:8000` (see `vite.config.js`).
- Left sidebar occupies 35% width and can be collapsed. `New Chat` resets the chat state and starts a simulated conversation between two agents.
- Messages from `Tác nhân 1` appear near the left; `Tác nhân 2` near the right.
