from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import json, os
import numpy as np

app = FastAPI()

# ---- CORS (VERY IMPORTANT) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load data ----
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

with open(DATA_PATH) as f:
    DATA = json.load(f)


# ✅ Handle preflight request (REQUIRED FOR VERCEL)
@app.options("/api/latency")
def options_handler():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


# ✅ Main API
@app.post("/api/latency")
async def analytics(request: Request):

    payload = await request.json()

    result = {}

    for region in payload["regions"]:
        records = [r for r in DATA if r["region"] == region]

        lat = [r["latency_ms"] for r in records]
        up = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(lat)),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(np.mean(up)),
            "breaches": sum(
                1 for l in lat if l > payload["threshold_ms"]
            ),
        }

    return Response(
        content=json.dumps(result),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*"
        },
    )
