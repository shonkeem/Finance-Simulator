from fastapi import FastAPI, Request, Body
from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    name: str
    income: int
    expenses: int

@app.get("/health")
def heatlh():
    return {"status": "ok"}

@app.post("/echo")
def echo(payload: Any = Body(default={})):
    stamp = datetime.now(timezone.utc).isoformat()
    print(f"[{stamp}] /echo received:", payload)
    return {"received": payload, "timestamp_utc": stamp}

@app.post("/simulate")
def simulate(payload: Input):
    return payload