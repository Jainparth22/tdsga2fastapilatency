from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import json, os, numpy as np

# prevent /api/latency → /api/latency/ redirect
app = FastAPI(redirect_slashes=False)

# CORS for IITM checker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

with open(DATA_PATH) as f:
    DATA = json.load(f)


# Handle CORS preflight
@app.options("")
def options_handler():
    return Response()


# POST → /api/latency
@app.post("")
def analytics(payload: dict):

    result = {}

    for region in payload["regions"]:
        records = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(
                1 for l in latencies if l > payload["threshold_ms"]
            ),
        }

    return result
