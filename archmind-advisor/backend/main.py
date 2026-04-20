from fastapi import FastAPI

app = FastAPI(title="ArchMind")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "project": "ArchMind"}
