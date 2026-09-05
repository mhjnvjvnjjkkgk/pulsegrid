# 04 — API CONTRACT

**This document is frozen.** Member 1 builds the routes to match it; Member 5 builds the
frontend against it. Neither waits for the other. If a change is genuinely needed, change
this file first and tell both members.

Base URL:

| Environment | Value of `window.ASHA_API_BASE` |
|---|---|
| Local | `http://127.0.0.1:5000` |
| Production | `https://asha-api.onrender.com` |

---

## 1. The one envelope, used by every endpoint

**Success**

```json
{ "ok": true, "data": { } }
```

**Failure**

```json
{ "ok": false, "error_code": "NO_CAPACITY", "message": "That bed was just taken." }
```

Rules:
- `ok` is always present and always a boolean. The frontend checks nothing else first.
- `message` is always safe to show a human, in plain English, with no stack traces.
- `error_code` is `SCREAMING_SNAKE_CASE` and is what JavaScript branches on.

**HTTP status mapping**

| Status | When |
|---|---|
| `200` | `ok: true` |
| `400` | Missing or malformed input (`MISSING_FIELD`, `BAD_PHONE`, `BAD_DELTA`) |
| `404` | Named thing does not exist (`NO_SUCH_WARD`, `NO_SUCH_HOSPITAL`) |
| `409` | Valid request, but the world said no (`NO_CAPACITY`, `DUPLICATE_HOLD`, `EXPIRED`, `INVALID_CODE`) |
| `503` | Supabase unreachable (`DB_UNAVAILABLE`) |
| `500` | Anything we failed to anticipate (`INTERNAL_ERROR`) |

`409 Conflict` for "someone beat you to it" is the semantically correct choice and is a
nice small thing to mention if a judge asks about API design.

---

## 2. `GET /api/health`

Used by the connection badge in the UI header and by Render's health check.

```json
{ "ok": true,
  "data": {
    "status": "healthy",
    "hospitals_connected": 12,
    "active_holds": 3,
    "ttl_worker_alive": true,
    "ttl_last_check": "2026-09-05T09:41:10Z",
    "triage_engine": "KEYWORD+LLM",
    "server_time": "2026-09-05T09:41:12Z"
  } }
```

`ttl_worker_alive` lets the UI show the worker heartbeat, which is a small but very
persuasive detail during a demo — the judges can *see* the background process breathing.

---

## 3. `POST /api/triage`

**Request**

```json
{ "text": "seene mein bahut dard ho raha hai aur saans nahi aa rahi",
  "input_mode": "VOICE",
  "category_tap": null,
  "patient_age": 54 }
```

| Field | Required | Notes |
|---|---|---|
| `text` | one of `text` / `category_tap` | Free text, English / Hindi / Hinglish, max 500 chars |
| `input_mode` | no | `TEXT` \| `VOICE` \| `TAP`, default `TEXT`. Logged only. |
| `category_tap` | one of `text` / `category_tap` | `cardiac` \| `trauma` \| `maternity` \| `general` |
| `patient_age` | no | Integer. Under 12 redirects RED cases to `pediatric_icu`. |

**Response**

```json
{ "ok": true,
  "data": {
    "severity": "RED",
    "recommended_ward": "cardiac_icu",
    "needs_trauma_center": false,
    "needs_blood": false,
    "suggested_blood_component": null,
    "explanation": "Chest pain with breathing difficulty indicates a possible cardiac event.",
    "matched_keywords": ["seene mein dard", "saans nahi"],
    "score": 100,
    "engine": "KEYWORD",
    "language": "hi",
    "offer_hold": true,
    "advice": "Do not drive yourself. Call 108. Chew an aspirin only if advised."
  } }
```

| Field | Meaning |
|---|---|
| `severity` | `RED` \| `YELLOW` \| `GREEN` — drives every colour in the UI |
| `recommended_ward` | One of the four ward codes, or `null` for GREEN |
| `offer_hold` | `false` for GREEN. The frontend hides the hold button entirely. |
| `engine` | `KEYWORD` \| `LLM` \| `KEYWORD+LLM` — shown as a small chip, so we never pretend a keyword match was AI |
| `score` | 0–100. Drives the severity meter fill. |

**Errors:** `MISSING_FIELD` (neither `text` nor `category_tap`), `TEXT_TOO_LONG`.

**Guarantee:** this endpoint never returns 5xx because of the LLM. If the model is slow,
unreachable, or returns junk, the keyword result is returned with `engine: "KEYWORD"`.

---

## 4. `GET /api/facilities`

The list the citizen and paramedic see. Polled every 4 seconds.

**Query parameters**

| Param | Required | Example | Notes |
|---|---|---|---|
| `ward` | no | `cardiac_icu` | Omit to get all four wards per hospital |
| `lat` / `lng` | no | `12.9716` / `77.5946` | Enables distance sorting. Omitted → sorted by availability then name. |
| `only_available` | no | `true` | Default `true`. `false` shows full hospitals greyed out. |
| `trauma_only` | no | `false` | Filter to `is_trauma_center = true` |
| `limit` | no | `12` | Default 12, max 50 |

**Response**

```json
{ "ok": true,
  "data": {
    "generated_at": "2026-09-05T09:41:12Z",
    "count": 2,
    "facilities": [
      {
        "hospital_id": "3f9a…",
        "name": "R.N. Tagore Institute of Cardiac Sciences",
        "short_name": "RTIICS Mukundapur",
        "is_govt": false,
        "is_trauma_center": false,
        "has_blood_bank": true,
        "phone": "+913366050000",
        "lat": 22.4893, "lng": 88.4024,
        "distance_km": 4.2,
        "eta_minutes": 13,
        "maps_url": "https://www.google.com/maps/dir/?api=1&destination=22.4893,88.4024",
        "updated_seconds_ago": 41,
        "wards": [
          { "ward_code": "cardiac_icu", "label": "Cardiac ICU",
            "total_physical": 12, "total_staffed": 10,
            "occupied": 7, "held_now": 1, "available_now": 2, "ghost_gap": 2 },
          { "ward_code": "adult_icu", "label": "Adult ICU",
            "total_physical": 18, "total_staffed": 14,
            "occupied": 14, "held_now": 0, "available_now": 0, "ghost_gap": 4 }
        ],
        "blood_summary": [
          { "blood_group": "O-", "component": "PRBC", "units_free_now": 4,
            "is_trauma_reserve": true, "requires_replacement_donor": false },
          { "blood_group": "B+", "component": "PLATELETS", "units_free_now": 6,
            "is_trauma_reserve": false, "requires_replacement_donor": true }
        ]
      }
    ]
  } }
```

Notes for Member 5:
- `eta_minutes` is `distance_km / 22 km-h * 60`, rounded. 22 km/h is a realistic Kolkata
  ambulance average. It is an estimate and the UI must label it `~`.
- `updated_seconds_ago` powers the freshness dot: green under 120 s, amber under 600 s, grey
  beyond. **Showing data age is a core trust feature** — the portals we are replacing hide it.
- `blood_summary` only includes rows with `units_free_now > 0`, capped at 6 entries.

---

## 5. `GET /api/blood`

For a blood-specific search (the paramedic asks for O− platelets, not a bed).

**Query:** `group=O-` (required), `component=PRBC` (optional), `lat`, `lng`, `limit`.

```json
{ "ok": true,
  "data": {
    "count": 3,
    "stock": [
      { "hospital_id": "3f9a…", "name": "S.S.K.M. Hospital (IPGMER)",
        "distance_km": 1.8, "blood_group": "O-", "component": "PRBC",
        "units_available": 6, "units_held_now": 2, "units_free_now": 4,
        "is_trauma_reserve": true, "requires_replacement_donor": false,
        "updated_seconds_ago": 95 }
    ]
  } }
```

**Errors:** `MISSING_FIELD`, `BAD_BLOOD_GROUP`, `BAD_COMPONENT`.

---

## 6. `POST /api/holds/create` — the important one

**Request (bed)**

```json
{ "hospital_id": "3f9a…",
  "resource_kind": "BED",
  "ward_code": "cardiac_icu",
  "hold_type": "CITIZEN",
  "severity": "RED",
  "requester_name": "Ramesh K",
  "requester_phone": "9880012345" }
```

**Request (blood)**

```json
{ "hospital_id": "3f9a…",
  "resource_kind": "BLOOD",
  "blood_group": "O-",
  "component": "PRBC",
  "units": 2,
  "hold_type": "PARAMEDIC",
  "severity": "RED",
  "requester_name": "108 Unit KA-01-AB-1234",
  "requester_phone": "9880099999" }
```

| Field | Required | Validation |
|---|---|---|
| `hospital_id` | yes | UUID |
| `resource_kind` | yes | `BED` \| `BLOOD` |
| `ward_code` | if `BED` | one of the four codes |
| `blood_group` / `component` | if `BLOOD` | from the allowed sets |
| `units` | no | 1–4, default 1. Beds are forced to 1. |
| `hold_type` | yes | `CITIZEN` → 15 min, `PARAMEDIC` → 20 min |
| `severity` | no | `RED` \| `YELLOW` \| `GREEN`. Rejected if `GREEN`: `GREEN_NO_HOLD`. |
| `requester_phone` | yes | Exactly 10 digits after stripping `+91`, spaces and dashes |

**Success**

```json
{ "ok": true,
  "data": {
    "hold_id": "b71c…",
    "otp_code": "5821",
    "hold_minutes": 15,
    "seconds_left": 900,
    "expires_at": "2026-09-05T09:56:12Z",
    "server_time": "2026-09-05T09:41:12Z",
    "left_after": 1,
    "hospital": { "name": "R.N. Tagore Institute of Cardiac Sciences", "phone": "+913366050000",
                  "lat": 22.4893, "lng": 88.4024,
                  "maps_url": "https://www.google.com/maps/dir/?api=1&destination=22.4893,88.4024" },
    "ward_label": "Cardiac ICU",
    "sms_preview": "ASHA: Bed HELD at R.N. Tagore Inst. of Cardiac Sciences, Cardiac ICU. Code 5821. Valid 15 min until 09:56. Show this code at the emergency desk."
  } }
```

Both `expires_at` **and** `server_time` are returned so the countdown can be driven by the
*difference* between them rather than by the phone's clock, which may be minutes off.
Member 5 must implement it that way.

`sms_preview` is the exact text a real SMS gateway would send. We log it and display it;
plumbing it into a paid gateway is the only remaining step. Say that honestly.

**Errors**

| `error_code` | HTTP | Frontend behaviour |
|---|---|---|
| `NO_CAPACITY` | 409 | Toast "Just taken — here are the next 3", refresh list, do **not** open the transit screen |
| `DUPLICATE_HOLD` | 409 | Offer to open the existing hold instead |
| `GREEN_NO_HOLD` | 400 | Explain that GREEN cases go to a local clinic |
| `NO_SUCH_WARD` / `NO_SUCH_STOCK` | 404 | Refresh the list; the seed data changed |
| `BAD_PHONE` | 400 | Inline field error |
| `DB_UNAVAILABLE` | 503 | Offline banner, keep the last list on screen marked stale |

On `NO_CAPACITY` the response also carries the next best options, so the UI can re-route in
one step instead of making the user search again:

```json
{ "ok": false, "error_code": "NO_CAPACITY",
  "message": "That bed was taken 2 seconds ago.",
  "alternatives": [
    { "hospital_id": "8ac1…", "name": "Medica Superspecialty Hospital",
      "ward_code": "cardiac_icu", "available_now": 3, "distance_km": 6.9 }
  ] }
```

---

## 7. `GET /api/holds/<hold_id>`

Polled every second by the transit screen so the countdown is server-truth, and so the
screen flips to "ADMITTED" the instant the nurse redeems the code.

```json
{ "ok": true,
  "data": { "hold_id": "b71c…", "status": "ACTIVE", "otp_code": "5821",
            "seconds_left": 512, "expires_at": "2026-09-05T09:56:12Z",
            "server_time": "2026-09-05T09:47:40Z",
            "hospital_name": "R.N. Tagore Inst. of Cardiac Sciences", "ward_label": "Cardiac ICU" } }
```

`status` transitions the UI: `ACTIVE` → countdown · `REDEEMED` → green "Patient admitted" ·
`EXPIRED` → amber "Hold expired, search again" · `CANCELLED` → back to the list.

**Errors:** `NOT_FOUND` (404).

> Polling once a second is fine here because exactly one screen does it, for at most
> 20 minutes. `GET /api/facilities` stays on the 4-second interval.

---

## 8. `POST /api/holds/cancel`

```json
{ "hold_id": "b71c…", "requester_phone": "9880012345" }
```

→ `{ "ok": true, "data": { "message": "Reservation released." } }`

**Errors:** `NOT_CANCELLABLE` (409) when the hold is not active or the phone does not match.

---

## 9. `POST /api/holds/redeem` — the hospital desk

```json
{ "hospital_id": "3f9a…", "otp_code": "5821" }
```

**Success**

```json
{ "ok": true,
  "data": { "hold_id": "b71c…", "resource_kind": "BED",
            "ward_code": "cardiac_icu", "ward_label": "Cardiac ICU",
            "severity": "RED", "hold_type": "PARAMEDIC",
            "requester_name": "Ramesh K",
            "message": "Patient admitted. Bed marked occupied." } }
```

The nurse's screen shows a full-width green confirmation with the patient name, ward and
severity — big enough to read from two metres away.

**Errors:** `INVALID_CODE` (409), `EXPIRED` (409), `CAPACITY_SHRANK` (409),
`BAD_OTP_FORMAT` (400 — not exactly 4 digits).

---

## 10. `GET /api/hospital/<hospital_id>/dashboard`

Everything `hospital.html` needs, in one call. Polled every 4 seconds.

```json
{ "ok": true,
  "data": {
    "hospital": { "id": "3f9a…", "name": "S.S.K.M. Hospital (IPGMER)", "is_trauma_center": true },
    "wards": [
      { "ward_code": "adult_icu", "label": "Adult ICU",
        "total_physical": 18, "total_staffed": 14, "occupied": 11,
        "held_now": 2, "available_now": 1, "ghost_gap": 4 }
    ],
    "inbound": [
      { "hold_id": "b71c…", "otp_code": "5821", "severity": "RED",
        "hold_type": "PARAMEDIC", "ward_code": "adult_icu", "ward_label": "Adult ICU",
        "requester_name": "Ramesh K", "requester_phone": "98800•••45",
        "seconds_left": 512, "created_at": "2026-09-05T09:41:12Z" }
    ],
    "recent": [
      { "otp_code": "3390", "status": "REDEEMED", "ward_label": "Cardiac ICU",
        "resolved_at": "2026-09-05T09:30:02Z" }
    ],
    "server_time": "2026-09-05T09:47:40Z"
  } }
```

`inbound` is sorted **RED first, then by `seconds_left` ascending** — the nurse's eye should
land on the most critical, soonest-arriving patient with no scanning.

Phone numbers are masked to `98800•••45`. Full numbers are never sent to a browser.

---

## 11. `POST /api/hospital/counter` — the one-tap `[+]` / `[-]`

```json
{ "hospital_id": "3f9a…", "ward_code": "adult_icu", "delta": 1 }
```

```json
{ "ok": true,
  "data": { "ward_code": "adult_icu", "occupied": 12, "total_staffed": 14,
            "held_now": 2, "available_now": 0 } }
```

The response carries the **new full state of that ward**, so the tile re-renders from the
server's answer rather than from an optimistic guess. If two nurses tap at once, both
screens converge on the truth.

**Errors:** `BAD_DELTA` (400 — anything but ±1), `ALREADY_EMPTY` (409),
`ABOVE_STAFFED` (409), `NO_SUCH_WARD` (404).

---

## 12. `POST /api/hospital/staffing` — shift change

```json
{ "hospital_id": "3f9a…", "ward_code": "adult_icu", "total_staffed": 9 }
```

→ `{ "ok": true, "data": { "total_staffed": 9, "ghost_gap": 9 } }`

**Errors:** `OUT_OF_RANGE` (400), `PATIENTS_PRESENT` (409), `NO_SUCH_WARD` (404).

This is the endpoint behind the Ghost Bed demo moment.

---

## 13. `GET /api/stats` — the header ticker and the closing slide

```json
{ "ok": true,
  "data": { "hospitals_connected": 12,
            "staffed_icu_beds_citywide": 148,
            "available_now_citywide": 23,
            "ghost_beds_citywide": 37,
            "active_holds": 3,
            "holds_today": 41,
            "redeemed_today": 28,
            "expired_today": 11,
            "cancelled_today": 2,
            "redemption_rate_pct": 68,
            "median_triage_ms": 6,
            "triage_counts_today": { "RED": 18, "YELLOW": 15, "GREEN": 8 } } }
```

`ghost_beds_citywide` — the sum of `ghost_gap` — is the single most quotable number in the
whole project: *"There are 37 ICU beds in this city that exist but cannot admit anyone
tonight, and no current portal can tell you that."*

---

## 14. CORS

`app.py` enables CORS for `GET, POST, OPTIONS` on `/api/*`.

Allowed origins are read from the `ALLOWED_ORIGINS` environment variable
(comma-separated) — the Vercel URL plus `http://127.0.0.1:5000` and
`http://localhost:5000`. We do **not** ship `*`: an open wildcard on an unauthenticated
write API is the kind of detail a sharp judge will spot.

---

## 15. Frozen-contract checklist

Before either member starts coding, confirm all of these are true:

- [ ] Every response has a top-level `ok`
- [ ] Every failure has `error_code` **and** a human `message`
- [ ] No endpoint returns a bare list — always an object, so fields can be added later
- [ ] All timestamps are ISO-8601 UTC with a trailing `Z`
- [ ] Every duration is either `seconds_left` (int) or `*_minutes` (int) — never a string
- [ ] No endpoint returns a full phone number
- [ ] No endpoint returns a Supabase key, SQL text, or a Python traceback
