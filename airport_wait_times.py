import requests
from datetime import datetime
from tabulate import tabulate

ROWS = []

JFK_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.jfkairport.com",
    "Referer": "https://www.jfkairport.com/",
    "User-Agent": "Mozilla/5.0"
}

JFK_SECURITY_URL = "https://avi-prod-mpp-webapp-api.azurewebsites.net/api/v1/SecurityWaitTimesPoints/JFK"
JFK_CUSTOMS_URL  = "https://avi-prod-mpp-webapp-api.azurewebsites.net/api/CustomClearanceTimesPoints/JFK"
JFK_WALK_URL     = "https://avi-prod-mpp-webapp-api.azurewebsites.net/api/v1/walkTimes/JFK"

jfk_security = requests.get(JFK_SECURITY_URL, headers=JFK_HEADERS).json()
jfk_customs  = requests.get(JFK_CUSTOMS_URL, headers=JFK_HEADERS).json()
jfk_walk     = requests.get(JFK_WALK_URL, headers=JFK_HEADERS).json()


jfk_security_by_terminal = {}
for s in jfk_security:
    t = s["terminal"]
    jfk_security_by_terminal[t] = max(
        s["timeInMinutes"],
        jfk_security_by_terminal.get(t, 0)
    )


jfk_customs_by_terminal = {
    c["terminal"]: c["timeInMinutes"]
    for c in jfk_customs
}


jfk_walk_by_terminal = {}
for t in jfk_walk["terminals"]:
    terminal = t["terminalName"].split()[-1]
    max_walk = 0
    for g in t["gateNames"]:
        upper = int(g["walkTime"].split("-")[1])
        max_walk = max(max_walk, upper)
    jfk_walk_by_terminal[terminal] = max_walk

jfk_timestamp = datetime.utcnow().isoformat()

for terminal in sorted(
    set(jfk_security_by_terminal)
    | set(jfk_customs_by_terminal)
    | set(jfk_walk_by_terminal)
):
    ROWS.append([
        f"JFK T{terminal}",
        jfk_security_by_terminal.get(terminal, "N/A"),
        jfk_customs_by_terminal.get(terminal, "N/A"),
        jfk_walk_by_terminal.get(terminal, "N/A"),
        jfk_timestamp
    ])

LHR_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.heathrow.com",
    "referer": "https://www.heathrow.com/",
    "user-agent": "Mozilla/5.0"
}

LHR_BASE = "https://api-dp-prod.dp.heathrow.com/pihub"
LHR_TERMINALS = ["2", "3", "4", "5"]

def extract_max_wait(data):
    waits = []
    timestamps = []
    for d in data:
        timestamps.append(d["lastUpdated"])
        for qm in d.get("queueMeasurements", []):
            if qm["name"] == "maximumWaitTime" and qm["value"] >= 0:
                waits.append(qm["value"])
    return (max(waits) if waits else "N/A",
            max(timestamps) if timestamps else None)

for terminal in LHR_TERMINALS:
    sec = requests.get(
        f"{LHR_BASE}/securitywaittime/ByTerminal/{terminal}",
        headers=LHR_HEADERS
    ).json()

    cus = requests.get(
        f"{LHR_BASE}/immigrationwaittime/ByTerminal/{terminal}",
        headers=LHR_HEADERS
    ).json()

    sec_wait, sec_ts = extract_max_wait(sec)
    cus_wait, cus_ts = extract_max_wait(cus)

    timestamp = max(t for t in [sec_ts, cus_ts] if t)

    ROWS.append([
        f"LHR T{terminal}",
        sec_wait,
        cus_wait,
        "N/A",    
        timestamp
    ])


print(tabulate(
    ROWS,
    headers=[
        "Airport",
        "Security Wait (min)",
        "Customs Wait (min)",
        "Walk to Gates (min)",
        "Timestamp"
    ],
    tablefmt="github"
))
