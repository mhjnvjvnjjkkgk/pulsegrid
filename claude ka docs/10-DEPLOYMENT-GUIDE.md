# 10 — DEPLOYMENT GUIDE

Two hosts, one database. Frontend on Vercel, Flask on Render, PostgreSQL on Supabase.

**Do the deployment a week before the competition, not the night before.** Every item in §4
is something that has ruined somebody's demo.

> **Before you start: the names below may already be taken.** Render service names and Vercel
> subdomains are globally unique, and `asha` is a short common word. If `asha-api` or
> `asha.vercel.app` is refused, fall back to **`asha-sih2026`** / **`asha-sih2026.vercel.app`**
> and change the name in exactly three places: `render.yaml` (`name:`), `ALLOWED_ORIGINS` on
> Render, and the production URL in `public/js/config.js`. Nothing else in the project contains
> a hostname. Decide the final names once, write them on the whiteboard, and do not change them
> again — a stale hostname in `config.js` is a silent CORS failure on demo morning.

---

## 1. Backend on Render (do this first — the frontend needs its URL)

Render runs `python app.py` as an ordinary long-lived process, which is why
`ttl_worker.py` actually works there and would not on Vercel serverless
([02 §6](02-SYSTEM-ARCHITECTURE.md#6-why-not-vercel-serverless-for-the-python-too)).

`render.yaml` (Member 1 owns this):

```yaml
services:
  - type: web
    name: asha-api
    runtime: python
    plan: free
    region: singapore              # closest Render region to India
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT
    healthCheckPath: /api/health
    envVars:
      - key: PYTHON_VERSION
        value: "3.12.3"
      - key: SUPABASE_URL
        sync: false               # set by hand in the dashboard
      - key: SUPABASE_KEY
        sync: false               # NEVER in this file
      - key: ALLOWED_ORIGINS
        value: https://asha.vercel.app
      - key: TTL_WORKER_ENABLED
        value: "1"
      - key: TRIAGE_LLM_ENABLED
        value: "0"
```

Steps:

1. <https://render.com> → **New → Web Service** → connect the GitHub repo.
2. Render reads `render.yaml`. Confirm the plan is Free.
3. **Environment** → add `SUPABASE_URL` and `SUPABASE_KEY` by hand. These are secrets and
   must not be in the repo.
4. Deploy. Watch the log for `[TTL WORKER] started`.
5. Verify: `curl https://asha-api.onrender.com/api/health`

### `--workers 1` is deliberate — do not raise it

Gunicorn workers are separate processes. Two workers means two TTL worker threads doing the
same housekeeping, which is harmless but produces confusing doubled log lines, and
`ttl_worker_alive` in `/api/health` would then describe only whichever process answered that
request. One worker with four threads handles far more traffic than a demo will ever see.

This is worth knowing because it is a genuinely good judge question: *"what happens to your
background thread if you scale to two servers?"* The honest answer: **the design already
survives it** — expiry is derived at read time, so duplicate janitors are redundant rather
than dangerous. In production you would move housekeeping to `pg_cron` inside PostgreSQL and
delete the thread entirely. Say exactly that.

---

## 2. Frontend on Vercel

`vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    },
    {
      "source": "/fonts/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

Steps:

1. <https://vercel.com> → **Add New → Project** → import the repo.
2. Framework preset: **Other**. Build command: **leave empty**. Output directory: **`public`**.
   There is no build step — that is the point of vanilla JS.
3. Deploy. Note the URL, e.g. `https://asha.vercel.app`.
4. Set the API base in `public/js/config.js` (Member 1 owns this file):

```javascript
// Auto-detects: localhost uses the local Flask server, anything else uses Render.
window.ASHA_API_BASE =
  (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
    ? location.origin
    : 'https://asha-api.onrender.com';

window.ASHA_MOCK = false;   // true = run the UI with no backend at all
```

5. Add the Vercel URL to `ALLOWED_ORIGINS` on Render and redeploy the API.
6. Open the Vercel URL. If the hospital list fills, both halves are live.

---

## 3. Deployment verification checklist

Run all of these against the **deployed** URLs, not localhost.

- [ ] `GET /api/health` returns `ttl_worker_alive: true`
- [ ] Vercel page loads over HTTPS with no mixed-content warning
- [ ] Hospital list populates within 4 seconds
- [ ] No CORS error in the browser console
- [ ] A hold can be created and shows an OTP
- [ ] The hospital desk redeems that OTP and the ward count increments
- [ ] Countdown runs down and the hold flips to EXPIRED after 15 minutes
- [ ] Render logs show the TTL worker line every 10 seconds
- [ ] Supabase Table Editor shows the same rows as the UI
- [ ] `view-source:` on the deployed page contains **no** Supabase key
      (`Ctrl-U`, `Ctrl-F`, search for `eyJ` — must be zero hits)
- [ ] Works on a real phone over mobile data, not just laptop Wi-Fi
- [ ] Works at 320 px width and at 200% zoom

---

## 4. The Render cold-start problem, and the demo-day plan

**The problem:** a Render free web service sleeps after ~15 minutes with no requests. The next
request takes 30–60 seconds while the container boots. If the jury arrives at your table
after a quiet twenty minutes, your first click appears to hang. This has ended more hackathon
demos than any bug.

Three defences, in order:

### Defence 1 — keep it awake (do this on the day)

Ten minutes before your slot, open the API health URL and leave a tab refreshing. A free
uptime pinger such as cron-job.org hitting `/api/health` every 10 minutes on demo day also
works.

### Defence 2 — make waking visible instead of silent

`api.js` shows `Waking server… first request takes about 30 seconds` if a request has not
answered within 3 seconds. A progress message is a system working; a frozen button is a system
broken. Same 30 seconds, completely different impression.

### Defence 3 — the local fallback, which is the real insurance

**Run the whole product on your own laptop and demo that.**

```bash
python app.py
```

`app.py` serves `public/` itself, so `http://127.0.0.1:5000` is the complete application with
zero cloud dependency except Supabase. No cold start, no venue Wi-Fi in the critical path,
sub-10 ms responses.

**Recommendation: demo locally, and show the Vercel URL as proof it is deployed.** Say it
plainly: *"This is running on my machine for speed; here is the same build live at
asha.vercel.app, and here is the database it shares."* No judge has ever objected to
that. Several have objected to watching a spinner.

### If the venue has no internet at all

Supabase is remote, so nothing works offline. Two mitigations, decided in advance:

- **Mobile hotspot** from two different phones on two different networks. This is the plan.
- `TRIAGE_LLM_ENABLED=0` so triage stays entirely local — already the default.

A local PostgreSQL fallback is *possible* but doubles the schema-maintenance work for one
unlikely scenario. **Decided: we are not building it** — hotspots are the plan. The reasoning is
written out in plain English in [15 §3, Q5](15-DECISIONS-AND-RISKS.md#open-questions). If that
decision is ever revisited, it has to be revisited early; retrofitting it in the last week is how
a working project breaks.

---

## 5. Three environments, one table

| | Frontend | API | Database |
|---|---|---|---|
| **Local dev** | `http://127.0.0.1:5000` (served by Flask) | same origin | Supabase cloud |
| **Deployed** | `https://asha.vercel.app` | `https://asha-api.onrender.com` | same Supabase project |
| **Demo day** | `http://127.0.0.1:5000` | same origin | same Supabase project |

All three share one database, so the Supabase Table Editor projected on a second laptop shows
live rows no matter which environment you are demonstrating. That shared window is one of the
most persuasive things you can put on a screen — the judges watch a row appear the instant you
tap a button.

---

## 6. Reset the demo data between runs

Have this saved in the Supabase SQL editor, ready to run between practice runs and before the
real one:

```sql
-- Clear all reservations and put every ward back to its seeded occupancy.
delete from holds;
delete from triage_logs;
update ward_capacity set occupied = round(total_staffed * 0.7), updated_at = now();
select release_expired_holds();
```

Practise the whole demo at least three times end to end with a reset in between. The third run
is when you find the thing the first two hid.
