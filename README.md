# Airport Wait Times Aggregator

This project aggregates **real-time airport operational wait times** from official airport APIs and presents them in a **single, normalized format**.

The focus is on:

* **Security screening wait times**
* **Customs / immigration wait times**
* **Walking time to gates** (where available)

No HTML scraping is used — all data comes from **official, publicly accessible airport APIs**.

---

## Airports Covered

### ✈️ John F. Kennedy International Airport (JFK)

* **Location:** New York, USA
* **Terminals:** 1, 4, 5, 7, 8

### ✈️ London Heathrow Airport (LHR)

* **Location:** London, UK
* **Terminals:** 2, 3, 4, 5

---

## Live API Endpoints Used

### JFK (New York)

**Security Wait Times**

```
GET https://avi-prod-mpp-webapp-api.azurewebsites.net/api/v1/SecurityWaitTimesPoints/JFK
```

**Customs / Immigration Wait Times**

```
GET https://avi-prod-mpp-webapp-api.azurewebsites.net/api/CustomClearanceTimesPoints/JFK
```

**Walking Time to Gates**

```
GET https://avi-prod-mpp-webapp-api.azurewebsites.net/api/v1/walkTimes/JFK
```

---

### LHR (London Heathrow)

**Security Wait Time (per terminal)**

```
GET https://api-dp-prod.dp.heathrow.com/pihub/securitywaittime/ByTerminal/{terminal}
```

**Immigration / Customs Wait Time (per terminal)**

```
GET https://api-dp-prod.dp.heathrow.com/pihub/immigrationwaittime/ByTerminal/{terminal}
```

> Heathrow does **not** currently expose a public API for walking-time-to-gates.

---

## Data Normalization Logic

To ensure a **single, consistent output row per terminal**, the following rules are applied:

### Security

* If multiple queues exist (e.g. North/South, PreCheck/Standard)
* The **maximum wait time** is used

### Customs / Immigration

* EEA and Non-EEA queues may be returned
* The **worst-case maximum wait time** is selected

### Walking Time

* Gate ranges such as `"10–15"` minutes
* The **upper bound** is used (`15`)

### Missing Data

* If an airport does not publish a metric, the value is shown as:

```
N/A
```

---

## Output Format

The script outputs a normalized table:

```
| Airport | Terminal | Security (min) | Customs (min) | Walk to Gates (min) | Last Updated |
```

### Example Output

```
| LHR | T3 | 5 | 120 | N/A | 2026-01-15T13:17:18 |
```

---

## How to Run

### Requirements

* Python **3.9+**
* Internet access

### Install Dependencies

```
pip install requests tabulate
```

### Run

```
python airport_wait_times.py
```

(Adjust filename if needed.)

---

## Files

* `airport_wait_times.py` – main combined script
* `sdca.py` – JFK data logic (source)
* `lhrhi.py` – Heathrow data logic (source)
* `README.md` – documentation

---

## Design Principles

* ✅ Uses **official airport APIs only**
* ✅ No scraping or browser automation
* ✅ Terminal-level granularity
* ✅ Worst-case logic to avoid under-reporting
* ✅ Easily extensible to new airports

---

## Potential Extensions

* JSON / CSV output
* REST API (FastAPI)
* Scheduler / cron job
* Configurable logic (EEA-only vs worst-case)
* Add airports (LAX, DXB, SIN, AMS)

---

## Disclaimer

All data is provided by airport authorities and reflects **real-time operational conditions**, which may change frequently.
