from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import json, os, numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("")
def options_handler():
    return Response()

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

with open(DATA_PATH) as f:
    DATA = json.load(f)




@app.post("")
def analytics(payload: dict):



    result = {}

    for region in payload["regions"]:
        records = [r for r in DATA if r["region"] == region]

        lat = [r["latency_ms"] for r in records]
        up = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(lat)),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(np.mean(up)),
            "breaches": sum(1 for l in lat if l > payload["threshold_ms"]),
        }

    return result
