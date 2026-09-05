# 02 — SYSTEM ARCHITECTURE

## 1. The whole system on one screen

```
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │  CITIZEN / PARAMEDIC     │        │  HOSPITAL DESK (tablet)  │
 │  public/index.html       │        │  public/hospital.html    │
 │  Tailwind + vanilla JS   │        │  high-contrast variant   │
 └────────────┬─────────────┘        └────────────┬─────────────┘
              │  fetch() every 4 s               │  fetch() every 4 s
              │                                  │
              └──────────────┬───────────────────┘
                             │   JSON over HTTPS
                             ▼
              ┌──────────────────────────────────┐
              │        FLASK API  (app.py)       │
              │  ┌────────────────────────────┐  │
              │  │ triage_service.py          │  │  keyword engine + optional LLM
              │  │ database.py                │  │  the only file that talks to Supabase
              │  │ ttl_worker.py  (thread)    │  │  janitor, runs every 10 s
              │  └────────────────────────────┘  │
              └──────────────┬───────────────────┘
                             │   supabase-py  (HTTPS / PostgREST)
                             ▼
              ┌──────────────────────────────────┐
              │   SUPABASE — PostgreSQL          │
              │   hospitals · ward_capacity      │
              │   blood_inventory · holds        │
              │   triage_logs                    │
              │   + v_ward_availability  (view)  │
              │   + create_live_hold()   (fn)    │  ← correctness lives here
              │   + redeem_hold()        (fn)    │
              └──────────────────────────────────┘
```

**One rule that keeps this simple:** only `database.py` is allowed to import `supabase`.
Every other Python file calls functions in `database.py`. If a judge asks "where does data
come from?", the answer is always one file.

## 2. Where each piece runs

| Piece | Host | Why |
|---|---|---|
| `public/` (HTML, CSS, JS) | **Vercel** static | Free, instant, global CDN, zero config, custom domain. |
| Flask API | **Render** free web service | Vercel serverless **cannot run a background thread** (see §4). Render runs a normal always-on Python process, so `ttl_worker.py` actually works. |
| PostgreSQL | **Supabase** free tier | Persistent (unlike SQLite on ephemeral serverless disks), plus a spreadsheet-style table editor the team can project on a second laptop during the demo. |

`app.py` **also serves `public/` itself**, so `python app.py` on any laptop gives you the
complete working product at `http://127.0.0.1:5000` with no Vercel involved. That is our
demo-day insurance policy.

## 3. Request flows

### 3.1 Happy path — citizen finds and holds a bed

```
1. User types "seene mein bahut dard hai"  (or taps 🫀, or speaks it)
2. POST /api/triage            → severity RED, ward cardiac_icu, engine KEYWORD
3. GET  /api/facilities?ward=cardiac_icu&lat=..&lng=..
                               → hospitals sorted by distance, availability computed live
4. User taps "Request Live Token Hold"
5. POST /api/holds/create      → PostgreSQL create_live_hold() runs atomically
                               → { hold_id, otp_code: "5821", expires_at, seconds_left: 900 }
6. Transit screen opens: countdown ring, OTP, directions link
7. Ambulance arrives. Nurse types 5821 on the hospital desk.
8. POST /api/holds/redeem      → hold REDEEMED, ward.occupied += 1
```

### 3.2 Sad path — patient never arrives

```
6'. Countdown reaches 0
    → availability recomputes instantly (the view stops counting an expired hold)
    → within 10 s, ttl_worker flips the row ACTIVE → EXPIRED and logs it
    → the hospital's inbound queue drops the card
```

### 3.3 Contended path — two ambulances, one bed

```
Ambulance A: POST /api/holds/create ─┐
Ambulance B: POST /api/holds/create ─┘  arrive within the same millisecond

PostgreSQL serialises them on the ward row lock:
   A → { ok: true,  otp_code: "5821" }
   B → { ok: false, error: "NO_CAPACITY", alternatives: [ ...next 3 hospitals ] }

B's UI never shows a success screen. B's driver is re-routed before moving.
```

## 4. Hard problem #1 — availability must be correct even when the worker is dead

### The naive design (and why we rejected it)

The obvious approach is a stored counter:

```
available = total_staffed - occupied - held      -- 'held' is a column we increment
```

This breaks the moment the TTL worker stops. If the worker dies at 11:00, every hold
created after that stays counted forever, `held` only grows, and by 11:30 the system
reports every hospital as full. **Correctness would depend on a background thread staying
alive** — the most fragile thing in the stack.

### What we do instead: expiry is *derived*, not *stored*

`held` is not a column. It is counted from the `holds` table at read time:

```sql
-- inside v_ward_availability
count(*) filter (where status = 'ACTIVE' and expires_at > now())
```

The instant the wall clock passes `expires_at`, that hold stops blocking capacity —
**automatically, with no code running.** Time itself frees the bed.

### So what is `ttl_worker.py` for?

Housekeeping, not correctness. Every 10 seconds it flips expired rows from `ACTIVE` to
`EXPIRED` so that:

- the hospital's **inbound queue** stops showing dead cards,
- the **audit trail** distinguishes "expired" from "cancelled" from "redeemed",
- the partial unique index on OTP codes frees that 4-digit code for reuse,
- and there is a visible, honest console log for the judges:
  `[TTL WORKER] 12:04:10 — checked 7 active holds, released 1 stale reservation`

**This is a two-layer design.** Layer 1 (the view) can never be wrong. Layer 2 (the worker)
makes things tidy. Losing Layer 2 degrades neatness, never safety. Member 4 should be able
to say that sentence from memory.

## 5. Hard problem #2 — two ambulances must never get the same bed

`supabase-py` speaks to PostgREST over HTTP. It has **no transactions**. So this Python is
broken no matter how carefully you write it:

```python
row = supabase.table("ward_capacity").select("*").eq(...).execute()   # reads 1 available
if row.available > 0:                                                 # ← B reads here too
    supabase.table("holds").insert({...}).execute()                   # both insert. Oversold.
```

The window between the read and the write is where the bug lives, and no amount of Python
can close it — the two calls are separate HTTP requests.

### The fix: move the decision inside the database

We write one PostgreSQL function, `create_live_hold(...)`. A PostgreSQL function runs
inside a single implicit transaction. Its first statement takes a **row-level lock** on
that ward's capacity row:

```sql
select * into cap from ward_capacity
 where hospital_id = p_hospital_id and ward_code = p_ward_code
 for update;                            -- ← B waits here until A commits
```

Now the check and the insert are one indivisible operation. Ambulance B does not read
stale data; it *waits a few milliseconds*, then reads the truth, then gets
`NO_CAPACITY`. Python's job shrinks to one line:

```python
response = supabase.rpc("create_live_hold", payload).execute()
```

Beginner-simple in Python, provably correct in SQL. Full function body in
[03-DATABASE-SCHEMA §5](03-DATABASE-SCHEMA.md#5-the-atomic-hold--the-most-important-half-page-in-this-project).

### And a third layer of defence

`ward_capacity` carries `CHECK (occupied >= 0 AND occupied <= total_staffed)`. Even a
future bug in a route cannot push a ward past its staffed capacity — PostgreSQL rejects the
write. We do not rely on application code for a safety property.

## 6. Why not Vercel serverless for the Python too?

We considered putting `app.py` on Vercel as a Python serverless function. Three facts ruled
it out:

1. **Background threads do not survive.** A serverless function is frozen or destroyed
   after it returns a response. `threading.Thread(...).start()` at import time gets killed
   with the container. Member 4's worker would silently never run.
2. **Cold starts.** A first request after idle can take seconds. Bad for a product whose
   entire pitch is speed.
3. **No shared in-process state** across invocations, which makes any future rate-limiting
   or caching awkward.

Render's free web service runs `python app.py` as an ordinary long-lived process, so the
thread behaves exactly as it does on a laptop. The one Render caveat — free instances sleep
after ~15 minutes idle and take ~50 s to wake — is handled in
[10-DEPLOYMENT-GUIDE](10-DEPLOYMENT-GUIDE.md#4-the-render-cold-start-problem-and-the-demo-day-plan).

## 7. Polling, not WebSockets

The frontend calls `GET /api/facilities` every 4 seconds. We chose polling over
WebSockets/Supabase Realtime deliberately:

- 4-second staleness is clinically irrelevant when the hold itself lasts 15 minutes.
- Polling has no reconnection logic, no heartbeat, no auth handshake — roughly 6 lines of
  JavaScript that a first-year can fully explain.
- It degrades gracefully on flaky venue Wi-Fi: a failed poll is simply retried 4 seconds
  later, whereas a dropped socket needs backoff logic we would get wrong.

If a judge pushes on this, the honest answer is in
[13-VIVA-DOSSIER](13-VIVA-DOSSIER.md) under Member 5.

## 8. Failure behaviour, summarised

| If this dies | What breaks | What still works |
|---|---|---|
| TTL worker thread | Inbound-queue cards linger; audit log less tidy | **All availability and all holds stay correct** |
| LLM API / no internet | Nothing visible | Keyword triage engine handles 100% of classification |
| Browser speech recognition unsupported | Mic button hides itself | Typing and category taps |
| Supabase unreachable | API returns `503` with a clear message; UI shows an offline banner | Cached last-known hospital list stays on screen, marked stale |
| Render instance asleep | First request slow | UI shows "waking server…" instead of an error |
| Flask down entirely | Everything | Nothing — this is the single point of failure, and we say so honestly |

## 9. Security posture (and its honest limits)

| Concern | Our position |
|---|---|
| Supabase keys | Only the **service-role key** is used, only in the Flask process, only from an environment variable. It is never shipped to the browser. The frontend has no database credentials at all. |
| Row Level Security | Enabled on all tables with **no public policies**, so the anon key can read nothing. All access is through Flask. |
| Endpoint authentication | **There is none, and this is a deliberate, disclosed gap.** Anyone who knows the URL can create a hold. A malicious script could exhaust capacity. |
| Why we accept it | A prototype's job is to prove the reservation model. Adding accounts would consume the build time of six first-years and prove nothing new. |
| What production needs | Paramedic device tokens issued to 108 dispatch, per-phone rate limiting (max 1 active hold per number — *this one is already enforced in the SQL*), OTP verification of the citizen's phone before a hold is granted, and an audit log of every hold by device. |

Say this plainly if asked. Judges respect a team that knows exactly where its prototype
stops. Pretending otherwise is how you lose the round.
