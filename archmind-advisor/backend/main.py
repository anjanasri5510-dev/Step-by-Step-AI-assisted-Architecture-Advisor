from fastapi import FastAPI

from backend.api.routes import router as api_router

app = FastAPI(title="ArchMind")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "project": "ArchMind"}


app.include_router(api_router)
