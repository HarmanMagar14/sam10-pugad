# Pugad Assist health check (SAM10 automation #2)
# Runs every 15 minutes from EventBridge. Calls the public site and writes
# two CloudWatch metrics (namespace SAM10) using Embedded Metric Format,
# so the function only needs the basic Lambda logging role.
import json
import os
import time
import urllib.request

URL = os.environ.get("CHECK_URL", "https://13-239-67-10.sslip.io/api/config")


def lambda_handler(event, context):
    start = time.time()
    ok, status, error = 0, 0, ""
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "pugad-health-check"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            ok = 1 if status == 200 else 0
    except Exception as e:
        error = repr(e)
    latency = round(time.time() - start, 3)

    print(json.dumps({
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [{
                "Namespace": "SAM10",
                "Dimensions": [[]],
                "Metrics": [
                    {"Name": "HealthCheckOK", "Unit": "Count"},
                    {"Name": "HealthCheckLatency", "Unit": "Seconds"},
                ],
            }],
        },
        "HealthCheckOK": ok,
        "HealthCheckLatency": latency,
        "status": status,
        "url": URL,
        "error": error,
    }))
    return {"ok": ok, "status": status, "latency_s": latency, "error": error}
