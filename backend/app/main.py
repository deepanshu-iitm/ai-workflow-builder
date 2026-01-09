from fastapi import FastAPI

app = FastAPI(title="AI Workflow Builder")

@app.get("/health")
def health():
    return {"status": "ok"}