from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    name: str
    age:int
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
    stamp = datetime.now(timezone.utc).isoformat()
    return {"payload": payload, "timestamp_utc": stamp}