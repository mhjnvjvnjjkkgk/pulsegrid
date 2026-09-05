# 14 — GLOSSARY

Every term used in these documents, in plain English, with where it appears in ASHA.

If you are about to present this project and any row here is unfamiliar, read that row. A judge
asking "what does TTL stand for?" is not a trick question, and not knowing is the only way to
fail it.

---

## 1. The domain — hospitals and emergencies

| Term | What it means | In ASHA |
|---|---|---|
| **Golden Hour** | The first hour after severe trauma or a heart attack, when treatment has the greatest chance of saving a life. | The entire justification for the project. Every design choice optimises for minutes inside this hour. |
| **Triage** | Sorting patients by how urgently they need care, so the sickest are treated first. From the French *trier*, to sort. | `triage_service.py` turns a description of symptoms into RED / YELLOW / GREEN. |
| **RED / YELLOW / GREEN** | Standard triage severity. RED = immediate, life-threatening. YELLOW = urgent but stable. GREEN = can wait safely. | RED and YELLOW may reserve a bed. GREEN gets advice and no reserve button. |
| **Ghost bed** | A bed that physically exists but has no nurse or doctor assigned, so it cannot take a patient. | Why we store `total_physical` and `total_staffed` separately and only ever count staffed beds as available. The most important idea in the project after the reservation itself. |
| **ICU** | Intensive Care Unit — continuous monitoring, ventilators, one nurse to very few patients. | Three of our four ward types: `adult_icu`, `pediatric_icu`, `cardiac_icu`. |
| **Ward** | A named section of a hospital with its own beds and staffing. | Four fixed codes, chosen once and never renamed. |
| **PRBC** | Packed Red Blood Cells — red cells with most plasma removed. What "a unit of blood" usually means in trauma. | A component in `blood_inventory`. |
| **Platelets / Plasma** | Two other blood components. Platelets help clotting and last about five days; plasma carries clotting factors and is frozen. | Tracked separately, because they are **not** interchangeable with PRBC. A dengue patient needs platelets; PRBC will not help. |
| **Replacement donor** | A blood bank has the component but will only release it if the patient's family donates an equivalent unit. Common in India. | The `requires_replacement_donor` flag — shown to the user, because "available" without that caveat is a lie. |
| **Trauma reserve** | Stock ring-fenced for accident emergencies and not released for planned surgery. | The `is_trauma_reserve` flag. |
| **108** | India's free national emergency ambulance number. | The paramedic mode in the UI is labelled "108 Dispatch". |
| **e-RaktKosh** | The Government of India's national blood bank information portal. | Our closest existing comparison — and it *displays* stock, it cannot reserve it. Know this name; a judge may test whether you researched prior art. |
| **HIS / EMR** | Hospital Information System / Electronic Medical Record — the software a hospital already runs. | We deliberately do not integrate. Named in scope discussions so the exclusion is explicit. |

---

## 2. The core mechanism

| Term | What it means | In ASHA |
|---|---|---|
| **TTL** | Time To Live. How long something stays valid before it automatically stops counting. | 15 minutes for a citizen hold, 20 for a paramedic. |
| **Hold / Live Token Hold** | A temporary reservation of one bed or one blood unit for one specific patient. | The `holds` table. The product, essentially. |
| **OTP** | One-Time Password. Here, a four-digit code proving the arriving patient is the one the bed was held for. | Generated inside `create_live_hold`, typed at the desk to admit. |
| **Redeem** | Converting a hold into an actual admission. | `redeem_hold()` — `held` becomes `occupied`. |
| **Expire** | A hold's time running out, so the bed returns to the pool. | Happens automatically at read time; the worker only tidies the status column afterwards. |
| **Derived state** | A value calculated from other data every time it is read, instead of being stored. | `available_now` is derived. This is why expiry needs no scheduler. |
| **Stored state** | A value written down and kept up to date by code. | `occupied` is stored. `held` deliberately is **not**. |
| **Race condition** | Two things happening at once, where the result depends on which happens first — and sometimes gives a wrong answer. | Three ambulances reading "1 bed free" at the same instant. The problem the project is built around. |
| **Atomic** | Happens completely or not at all, with nothing able to interleave halfway through. | `create_live_hold` is atomic — the check and the insert cannot be split. |
| **Idempotent** | Doing it twice has the same effect as doing it once. | `release_expired_holds()` is idempotent, which is why two copies of the worker are harmless. |
| **Over-triage / under-triage** | Rating a patient more / less severe than they are. | Over-triage wastes a bed; under-triage can kill. When the keyword engine and the LLM disagree, we take the more severe answer. That asymmetry is deliberate. |

---

## 3. Databases and SQL

| Term | What it means | In ASHA |
|---|---|---|
| **PostgreSQL** | An open-source relational database. "Postgres" for short. | Our database, managed by Supabase. |
| **Supabase** | A hosted service that gives you a PostgreSQL database plus an HTTP API over it. | Where the data lives. Free tier. |
| **Table / row / column** | A table is a grid; a row is one record; a column is one field. | `hospitals` has 12 rows; `ward_capacity` has 48. |
| **Primary key** | The column that uniquely identifies a row. | `id`, a UUID, on every table. |
| **Foreign key** | A column pointing at another table's primary key. | `ward_capacity.hospital_id` points at `hospitals.id`. |
| **UUID** | Universally Unique Identifier — a 36-character random id like `3f2a…`. Unlike `1, 2, 3` it cannot be guessed or enumerated. | Every id in the project. |
| **View** | A saved query that behaves like a table. Not stored data — recalculated whenever you read it. | `v_ward_availability`. Where the availability formula lives. |
| **CHECK constraint** | A rule the database enforces on every write. Break it and the write is rejected. | `occupied >= 0 and occupied <= total_staffed` — this is what makes overselling *unwritable*, not merely unlikely. |
| **Unique index** | Prevents duplicate values in a column. | On `(hospital_id, otp_code)`. |
| **Partial index** | A unique index that applies only to rows matching a condition. | `where status = 'ACTIVE'` — so an OTP can be reused after the old hold expires, but never while it is live. Explain this one carefully; it is genuinely clever and easy to state badly. |
| **Transaction** | A group of operations that all succeed together or all undo together. | Everything inside a PostgreSQL function is one transaction. |
| **Row-level lock / `FOR UPDATE`** | Telling the database "nobody else may touch this row until I'm done." Others wait in line. | One line in `create_live_hold`. The reason double-booking is impossible. |
| **plpgsql** | The programming language for writing functions that run inside PostgreSQL. | Our six functions. Chosen so the lock and the insert are in the same transaction. |
| **RPC** | Remote Procedure Call — asking a remote system to run a named function. | `supabase.rpc("create_live_hold", …)` — one HTTP call replacing four. |
| **PostgREST** | The component that turns Supabase tables into an HTTP API. | Why Python cannot hold a transaction across two calls: each call is separate HTTP. |
| **RLS** | Row Level Security. Per-row permission rules. | Enabled on all five tables with **zero policies**, so the public key can read nothing. |
| **`anon` key / `service_role` key** | Supabase's public key (subject to RLS) and its admin key (bypasses RLS). | The browser gets neither. `service_role` lives only in server environment variables. |
| **Seed data** | Starting rows inserted so the app has something to show. | `supabase_seed.sql` — 12 Kolkata facilities. Capacity numbers are invented; that is disclosed on screen. |
| **`now()`** | PostgreSQL's current-time function. | The only clock in the project. Python never generates a timestamp. |

---

## 4. Web, HTTP and APIs

| Term | What it means | In ASHA |
|---|---|---|
| **API** | Application Programming Interface — the set of URLs one program offers another. | Our 13 endpoints, frozen in [04](04-API-CONTRACT.md). |
| **Endpoint** | One URL that does one thing. | `POST /api/holds/create`. |
| **REST** | A convention for APIs: nouns in the URL, verbs as HTTP methods. | Roughly what we follow. |
| **GET / POST** | GET reads and changes nothing. POST sends data and changes something. | `GET /api/facilities` reads; `POST /api/holds/create` reserves. |
| **JSON** | A text format for structured data: `{"ok": true, "count": 3}`. | Every request and response body. |
| **Status code** | A number describing the outcome. 200 fine, 400 your input was bad, 404 not found, 409 conflict, 500 our fault. | **409** for "someone got that bed a moment before you" — worth knowing why it is not 400: nothing was wrong with the request, the world changed. |
| **Envelope** | Wrapping every response in the same outer shape. | `{"ok": true, "data": …}` or `{"ok": false, "error_code": …, "message": …}`. One shape means one handler in the frontend. |
| **CORS** | The browser rule that a page on one domain cannot call an API on another unless the API allows it. | Our Vercel page calls our Render API, so the API lists that origin in `ALLOWED_ORIGINS`. Never `*`. |
| **Origin** | Scheme + host + port together. | `localhost:5000` and `127.0.0.1:5000` are *different* origins — a classic hour lost to this. |
| **Polling** | Asking the server "anything new?" on a timer. | Every 4 seconds for facilities, 1 second for a live hold. |
| **WebSocket** | A connection kept open so the server can push updates. | Deliberately not used — see [02 §7](02-SYSTEM-ARCHITECTURE.md). |
| **Latency** | How long a round trip takes. | Why our Supabase region is Mumbai and our Render region is Singapore. |
| **XSS** | Cross-Site Scripting: user-supplied text treated as code by the browser. | Prevented by inserting all human-typed text with `textContent`, never `innerHTML`. |
| **Rate limiting** | Capping how often one caller may act. | Not implemented; the one-hold-per-phone index is the abuse control we do have. Disclosed. |

---

## 5. Python and Flask

| Term | What it means | In ASHA |
|---|---|---|
| **Flask** | A small Python web framework: map a URL to a function, return a value. | `app.py`. Chosen because it is readable end to end. |
| **Route / decorator** | `@app.route("/api/health")` above a function tells Flask which URL calls it. | The only decorator allowed in this project. |
| **`requirements.txt`** | The list of libraries to install. | `pip install -r requirements.txt`. |
| **Virtual environment (venv)** | A private folder of libraries for one project, so projects cannot break each other. | `.venv`. Your prompt shows `(.venv)` when it is active. |
| **Environment variable** | A value given to a program by the system rather than written in the code. | Where every secret lives. |
| **`.env`** | A local file of environment variables, never committed. | Holds your Supabase URL and key. **Gitignored.** |
| **Thread** | A second line of execution inside one program, running alongside the main one. | `ttl_worker.py`. |
| **Daemon thread** | A thread that does not stop the program from exiting. | Ours is one, so Ctrl-C actually quits. |
| **Gunicorn** | A production server that runs Flask properly under real traffic. | Render's start command. `--workers 1` deliberately. |
| **Worker** | One operating-system process running a copy of the app. | Two workers would mean two TTL threads — harmless, but the reason we pin it to one. |
| **`pytest`** | Python's test runner. | `python -m pytest tests/ -v`. |
| **UTC** | Coordinated Universal Time — the world's reference clock, no time zones, no daylight saving. | All stored times. Converted to local only for display. |

---

## 6. Frontend

| Term | What it means | In ASHA |
|---|---|---|
| **Vanilla JavaScript** | Plain JS with no framework. | All of `public/js/`. No build step, which is the point. |
| **DOM** | The browser's live tree of page elements, which JavaScript changes. | `ui.js` writes to it. |
| **`textContent` vs `innerHTML`** | `textContent` inserts text as text. `innerHTML` parses it as HTML — so it can execute. | The XSS rule: human-typed text always uses `textContent`. |
| **Tailwind CSS** | A CSS library of tiny utility classes (`flex`, `p-4`) used directly in HTML. | Layout and spacing. Loaded from a CDN, so no build step. |
| **CSS custom property** | A variable in CSS: `--vital-400: #3DE3D0`, used as `var(--vital-400)`. | Every colour and duration. No hex codes in HTML, ever. |
| **Glassmorphism / liquid glass** | A style where panels look like frosted glass over a moving background. | The whole visual language. Four layers: tint, blur, inset highlight, hairline border. |
| **`backdrop-filter`** | The CSS property that blurs whatever is behind an element. | What makes the glass. Also the most expensive property on the page — hence a limit of eight visible at once. |
| **`@supports`** | A CSS block that only applies if the browser supports a feature. | `@supports not (backdrop-filter: blur(2px))` gives solid panels instead of unreadable ones. Mandatory. |
| **Keyframes** | A named CSS animation defining what happens at each stage. | The ECG pulse and the aurora drift. |
| **`prefers-reduced-motion`** | An operating-system setting saying "less animation, please." | Honoured — all motion collapses. Not optional; some people get motion sickness. |
| **Specular highlight** | The bright edge where light catches a curved glass surface. | The inset top-edge highlight that makes a panel look like glass rather than a grey box. |
| **Tabular numerals** | A font setting where every digit is the same width, so numbers do not shift while counting. | Used on every countdown. Without it, `14:59 → 14:58` visibly jitters. |
| **`aria-live`** | Marks a region whose changes a screen reader should announce. | The countdown — announced at milestones only, not every second. |
| **Web Speech API / `webkitSpeechRecognition`** | The browser's built-in speech-to-text. | The microphone. Audio never leaves the browser; only the transcript does. |
| **Skeleton loader** | Grey placeholder shapes shown while data loads. | Hospital cards, so the layout does not jump. |
| **Debounce** | Waiting until typing stops before acting. | The symptom box. |
| **`clamp()`** | CSS for "at least this, ideally that, at most this" — used for text that scales with the viewport. | The type scale. |

---

## 7. Deployment and Git

| Term | What it means | In ASHA |
|---|---|---|
| **Vercel** | A host for static files and serverless functions. | Serves `public/`. |
| **Render** | A host that runs an ordinary long-lived server process. | Runs Flask, because our background thread needs a process that stays alive. |
| **Serverless** | Code that runs on demand and is frozen or destroyed between requests. | Why Flask is **not** on Vercel: a background thread there would silently stop. |
| **Cold start** | The delay when a sleeping service must boot before answering. | 30–60 s on Render's free tier. Three defences in [10 §4](10-DEPLOYMENT-GUIDE.md). |
| **Health check** | A URL a host polls to confirm the app is alive. | `/api/health`, which also reports `ttl_worker_alive`. |
| **Repository (repo)** | A project tracked by Git, with its full history. | `asha`. |
| **Commit** | One saved change with a message, an author and a timestamp. | 38 of them across six members. |
| **Author vs committer** | Author wrote the change; committer applied it. Git stores both. | `git -c user.name=… -c user.email=…` sets both, so `git log --format=fuller` is consistent. |
| **Branch** | A parallel line of work. | One per member: `feature/database-schema`, etc. |
| **Pull Request (PR)** | A request to merge a branch, with a page for review and discussion. | Six of them. **A PR belongs to whoever opens it** — which is why each member opens their own. |
| **Merge vs squash** | Merge keeps every individual commit. Squash flattens them into one. | Squash is **off**, so each member's commits stay visible in Insights. |
| **GitHub Insights** | The tab showing who contributed what. | What the jury checks. Attribution only works if the commit email matches a registered GitHub account. |
| **`.gitignore`** | A list of files Git must never track. | Contains `.env`, `__pycache__`, `.venv`. |
| **Conventional Commits** | A message format: `feat(scope): description`. | `feat(triage): add Hindi keyword lexicon`. |

---

## 8. Five sentences worth being able to say verbatim

Not definitions — the compressed versions of the ideas. If these come out fluently, everything
above is understood.

1. **Availability is derived, not stored:** staffed minus occupied minus unexpired active holds,
   computed on every read.
2. **A row lock inside one database function** is what makes two simultaneous requests take
   turns instead of both succeeding.
3. **A CHECK constraint** makes an oversold ward impossible to write, even from buggy code.
4. **The background worker is housekeeping, not correctness** — kill it and beds still release
   on time.
5. **All time comes from the database in UTC**, and the countdown is `expires_at` minus the
   server's own clock, so a wrong phone clock cannot desynchronise anything.
