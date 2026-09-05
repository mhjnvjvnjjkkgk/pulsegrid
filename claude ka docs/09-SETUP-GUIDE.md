# 09 — SETUP GUIDE

Windows-first, because that is what this team is on. Everything here takes about 25 minutes
the first time.

You have **Python 3.12.3** and **Python 3.14.0** installed. Use **3.12** — `supabase-py` and
its dependencies are not reliably wheeled for 3.14 yet, and debugging a C build on the night
before a demo is not a good use of anyone's evening.

---

## 1. Create the Supabase project (10 minutes, do this first)

1. Go to <https://supabase.com> → **Start your project** → sign in with GitHub.
2. **New project.**
   - Name: `asha`
   - Database password: generate one and **save it in your password manager** — Supabase shows
     it once.
   - Region: **South Asia (Mumbai) — ap-south-1.** Latency matters for a live demo, and this
     is the closest region.
   - Plan: Free.
3. Wait ~2 minutes for provisioning.
4. **SQL Editor → New query.** Paste all of `supabase_schema.sql`. Click **Run**. You should
   see `Success. No rows returned`.
5. New query again. Paste `supabase_seed.sql`. **Run.**
6. **Table Editor** → you should now see five tables, with 12 rows in `hospitals` and 48 in
   `ward_capacity`. Keep this tab open — it is your live window into the system, and it is
   what you project on a second laptop during the demo.
7. **Project Settings → API.** Copy two values:
   - **Project URL** → `https://xxxxxxxx.supabase.co`
   - **`service_role` secret key** → the long one under *Project API keys*

> **The `service_role` key bypasses every security rule in your database.** It goes in `.env`
> on your machine and in Render's environment variables. It never goes in a commit, a
> screenshot, a WhatsApp group, or any file inside `public/`. If it leaks, rotate it
> immediately in Project Settings → API.
>
> We use `service_role` rather than `anon` because RLS is enabled with no policies — see
> [03 §4](03-DATABASE-SCHEMA.md#4-row-level-security). The browser never sees either key.

Run the six verification queries in
[03 §8](03-DATABASE-SCHEMA.md#8-how-to-verify-the-schema-in-60-seconds) before moving on. If
they pass, your database is done.

---

## 2. Get the code running (10 minutes)

```bash
git clone https://github.com/YOUR-ORG/asha.git
cd asha
```

Create an isolated Python environment so this project's packages cannot break anything else
on your laptop:

```bash
py -3.12 -m venv .venv
```

Activate it. **The command differs by shell** — this is the single most common place people
get stuck:

```bash
source .venv/Scripts/activate
```

```powershell
.venv\Scripts\Activate.ps1
```

You know it worked when your prompt starts with `(.venv)`.

If PowerShell refuses with an execution-policy error, run this once as your own user (it does
not need admin):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` from the template and fill in the two Supabase values:

```bash
cp .env.example .env
```

`.env` should end up looking like this — no quotes, no spaces around `=`:

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOi…your-service-role-key…
PORT=5000
FLASK_DEBUG=1
ALLOWED_ORIGINS=http://127.0.0.1:5000,http://localhost:5000
TRIAGE_LLM_ENABLED=0
TRIAGE_LLM_PROVIDER=
TRIAGE_LLM_API_KEY=
TTL_WORKER_ENABLED=1
TTL_INTERVAL_SECONDS=10
```

Run it:

```bash
python app.py
```

Expected console output:

```
[ASHA] Supabase connected: https://xxxxxxxx.supabase.co
[ASHA] Triage engine: KEYWORD (LLM disabled)
[TTL WORKER] started, checking every 10s
[ASHA] serving frontend from ./public
 * Running on http://127.0.0.1:5000
[TTL WORKER] 14:32:10 — checked 0 active holds, released 0 stale reservations
```

Open <http://127.0.0.1:5000>. You should see the citizen screen with 12 hospitals.
<http://127.0.0.1:5000/hospital.html> is the nurse desk.

**`.env` must never be committed.** `.gitignore` covers it, but confirm with `git status`
before your first commit — a leaked `service_role` key is the one mistake in this project that
cannot be undone by editing a file.

---

## 3. When it does not work

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | venv not activated, or you installed into the wrong Python | Re-activate; confirm `where python` points inside `.venv` |
| `SUPABASE_URL is not set` | `.env` missing, misnamed (`env.txt`), or in the wrong folder | It must be `.env` in the same folder as `app.py`. Windows Explorer hides extensions — check with `ls -la` |
| `Invalid API key` | You copied the `anon` key instead of `service_role` | Project Settings → API → the key labelled `service_role` |
| Frontend loads, hospital list stays empty forever | Seed never ran | Re-run `supabase_seed.sql`; confirm `select count(*) from hospitals;` returns 12 |
| `relation "v_ward_availability" does not exist` | Schema ran with an error partway | Re-run the whole `supabase_schema.sql` — it drops first, so this is safe |
| CORS error in the browser console | Origin not in `ALLOWED_ORIGINS` | Add the exact origin including port; `localhost` and `127.0.0.1` are different origins |
| Port 5000 already in use | Something else is on it (on Windows this is often a system service) | Set `PORT=5050` in `.env` |
| `[TTL WORKER]` never logs | `TTL_WORKER_ENABLED=0`, or the thread crashed at startup | Set it to `1`; scroll up for a traceback from the first loop |
| Everything worked yesterday, dies today | Supabase free projects pause after ~7 days idle | Open the dashboard and click **Restore** |
| Glass panels look like flat grey boxes | `backdrop-filter` unsupported or disabled | Expected on old Android WebViews — the `@supports` fallback is doing its job |

**The debugging rule for this project:** find out *which layer* is broken before changing
anything.

1. Is the database right? → run the query in the Supabase SQL editor.
2. Is the API right? → `curl http://127.0.0.1:5000/api/health`
3. Is the browser right? → open DevTools → Network, look at the actual response body.

Three checks, in that order, will locate any bug in this codebase in under two minutes.
Changing code before locating the layer is how evenings disappear.

---

## 4. Useful commands

```bash
curl http://127.0.0.1:5000/api/health
```

```bash
curl -X POST http://127.0.0.1:5000/api/triage -H "Content-Type: application/json" -d "{\"text\":\"severe chest pain and breathlessness\"}"
```

```bash
python -m pytest tests/ -v
```

```bash
python scripts/simulate_ambulance_rush.py --hospital-id <uuid> --ward adult_icu --requests 5
```

---

## 5. Optional: enable the LLM triage enhancer

Everything works without this. The keyword engine handles 100% of classification on its own,
and the demo is safer with the LLM off. Turn it on only after the rest is finished.

```
TRIAGE_LLM_ENABLED=1
TRIAGE_LLM_PROVIDER=gemini
TRIAGE_LLM_API_KEY=your-key
```

The service enforces a 4-second timeout and falls back to keywords on any failure, so a dead
API key degrades the response to `engine: "KEYWORD"` and nothing else. See
[15 §3](15-DECISIONS-AND-RISKS.md) for the provider decision, which is still open.
