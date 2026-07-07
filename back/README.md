# Backend Structure

The backend is organized as a Python package under `app/`.

```text
back/
  api.py                 # Compatibility entrypoint for uvicorn api:app
  main.py                # Compatibility exports for discussion service
  app/
    api/                 # FastAPI app and HTTP endpoints
    agents/              # LangChain agents used by the discussion flow
    core/                # Storage and prompt persistence helpers
    services/            # Application orchestration/business logic
    rag/                 # PDF chunking, embedding, MongoDB, and FAISS pipeline
    experiments/         # Standalone experiment scripts
  data/                  # Runtime JSON data mounted by Docker
```

Preferred server command:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

The old `uvicorn api:app` command still works through `back/api.py`.
