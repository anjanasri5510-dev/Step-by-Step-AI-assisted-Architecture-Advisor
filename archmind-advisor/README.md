# ArchMind

AI-powered multi-agent architecture advisor.

## Folder structure

```
archmind-advisor/
├── backend/
│   ├── agents/        # Multi-agent logic (planner, advisor, reviewer, etc.)
│   ├── api/           # FastAPI routers and endpoint definitions
│   ├── models/        # Pydantic models and data schemas
│   ├── utils/         # Shared utilities and helpers
│   └── main.py        # FastAPI application entrypoint
├── frontend/
│   └── index.html     # Static frontend entrypoint
├── tests/             # Test suite for backend and agents
├── .gitignore         # Ignored files (env, caches, OS metadata)
├── requirements.txt   # Python dependencies
└── README.md          # Project overview (this file)
```

- **backend/** – Python backend powered by FastAPI. `main.py` wires up the app, while
  `agents/`, `api/`, `models/`, and `utils/` hold the multi-agent logic, HTTP routes,
  data schemas, and shared helpers respectively.
- **frontend/** – Minimal static frontend served as `index.html`. Will later be
  expanded into the user-facing UI for the advisor.
- **tests/** – Automated tests covering the backend agents and API endpoints.
- **requirements.txt** – Python runtime dependencies (FastAPI, Uvicorn, httpx,
  Anthropic SDK, python-dotenv).
- **.gitignore** – Keeps local environment files, Python caches, and OS metadata
  out of version control.
