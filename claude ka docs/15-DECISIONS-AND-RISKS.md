# 15 — DECISIONS AND RISKS

Three parts: the decisions already made and why, what could go wrong and what we do about it,
and the questions still open that need the team lead's answer before implementation starts.

A judge who asks "why did you do it this way?" is not attacking the choice — they are checking
whether it *was* a choice. Every entry in §1 exists so the answer is yes.

---

## 1. Architecture decisions

Format: what we decided, what we rejected, what it costs us, and who explains it in the viva.

### ADR-01 — Availability is derived at read time, never stored

**Decided:** `available_now = total_staffed − occupied − (count of ACTIVE holds with
`expires_at > now()`)`, computed inside a view on every read.
**Rejected:** a stored `held` integer column, incremented on hold and decremented on expiry.
**Why:** a stored counter must be decremented by *something*. If that something dies between
the expiry moment and the decrement, the bed is lost forever and only a human notices. Deriving
it means expiry is a property of time, not of a running process.
**Cost:** one small aggregate per read over 48 ward rows. Unmeasurable at our scale.
**Explains it:** M2, with M4 on the consequences. This is the single most defensible decision in
the project — lead with it.

### ADR-02 — Holds are created inside one PostgreSQL function with a row-level lock

**Decided:** `create_live_hold()` in plpgsql. `select id from ward_capacity … for update`
*before* measuring availability, then insert, all in one transaction.
**Rejected:** doing the check-then-insert in Python via `supabase-py`.
**Why:** PostgREST is HTTP. Two HTTP calls cannot share a transaction, so there is an
unclosable gap between "read 1 bed free" and "insert the hold" in which another request reads
the same 1. That is not a bug to be careful about; it is structurally unfixable from the client.
**Cost:** logic lives in SQL, which is less familiar to the team than Python. Mitigated by
seven numbered comments in the function and a rehearsed walkthrough.
**Explains it:** M2.

### ADR-03 — A `CHECK` constraint as the last line of defence

**Decided:** `check (occupied >= 0 and occupied <= total_staffed)` on `ward_capacity`.
**Rejected:** trusting application logic alone.
**Why:** the lock prevents overselling; the constraint makes it *unwritable*. Two independent
mechanisms, so a bug in one cannot produce a wrong bed count.
**Cost:** a write that violates it fails loudly — which is the desired behaviour and is handled
explicitly (`CAPACITY_SHRANK`).
**Explains it:** M2.

### ADR-04 — Supabase managed PostgreSQL, not local SQLite

**Decided:** hosted Postgres.
**Rejected:** SQLite in a file.
**Why:** two reasons, and the second is the real one. Serverless and container hosts have
ephemeral filesystems — a redeploy silently erases a SQLite file. And SQLite has no
`SELECT … FOR UPDATE`, so ADR-02 would be impossible.
**Cost:** requires internet. Addressed in the demo plan with two mobile hotspots.
**Explains it:** M2.

### ADR-05 — Flask on Render, static frontend on Vercel

**Decided:** two hosts, one database.
**Rejected:** everything on Vercel as serverless Python.
**Why:** the TTL worker is a background thread. Serverless functions are frozen or destroyed
between requests, so the thread stops without any error appearing anywhere. Render runs an
ordinary long-lived process.
**Cost:** two dashboards, a CORS configuration, and Render's free-tier cold start. All three
are documented and mitigated in [10](10-DEPLOYMENT-GUIDE.md).
**Explains it:** M1, with M4 on why the thread needs a real process.

### ADR-06 — Vanilla JavaScript and Tailwind from a CDN, no build step

**Decided:** plain HTML, Tailwind via CDN, no bundler, no framework.
**Rejected:** React, Vue, Vite, npm.
**Why:** six first-year students and five weeks. A build step is a category of failure that can
appear on demo morning. And every member must be able to explain their own file — that is not
achievable in a framework they learned last month.
**Cost:** manual DOM updates, and no component reuse. Managed by the element-ID contract in
[06](06-SCREEN-SPECS.md) and one global namespace per file.
**Explains it:** M1 or M5. State the trade openly; do not apologise for it.

### ADR-07 — Deterministic keyword triage is primary; the LLM is an optional enhancer

**Decided:** a weighted keyword lexicon with negation handling decides severity. Any LLM runs
with a 4-second timeout, can never block the response, and on disagreement the **more severe**
result wins.
**Rejected:** an LLM as the primary classifier.
**Why:** auditability (a hospital will ask why a patient was rated RED), offline capability
(ambulances lose signal), and 6 ms versus ~2 s. The asymmetry rule exists because over-triage
wastes a bed and under-triage kills a patient — that is not a judgement to delegate to a model.
**Cost:** unusual phrasings score zero and return GREEN with advice to rephrase or call 108.
**Explains it:** M3. Expect "so it's not really AI" and have the answer ready — it is in
[13 §4](13-VIVA-DOSSIER.md#4-m3--triage-engine).

### ADR-08 — Polling, not WebSockets

**Decided:** 4-second poll for facilities, 1-second for an active hold.
**Rejected:** WebSockets or Supabase Realtime.
**Why:** bed availability changes on the order of minutes. Polling is a few lines that recover
by themselves after a lid close or a dropped connection.
**Cost:** up to 4 seconds of staleness, which the UI labels honestly with a freshness dot.
**Explains it:** M5.

### ADR-09 — `total_physical` and `total_staffed` are separate columns

**Decided:** store both; compute availability only from staffed.
**Rejected:** one `total_beds` column.
**Why:** this *is* the Ghost Bed problem. A dashboard that reports physical beds as available is
the specific failure we exist to correct. Storing both also makes the gap measurable — and
`ghost_beds_citywide` is the most quotable number in the pitch.
**Cost:** one more column and a `set_staffed_beds` control on the desk.
**Explains it:** M2 for the model, M6 for the control.

### ADR-10 — Four ward codes, fixed forever

**Decided:** `adult_icu`, `pediatric_icu`, `cardiac_icu`, `general_oxygen`. Enforced by a CHECK
constraint and repeated identically in SQL, Python, the API and the DOM ids.
**Rejected:** a configurable ward-type table.
**Why:** every renaming of these strings costs four files and an evening. Four is enough to
demonstrate routing, and a real deployment would extend the list, not restructure it.
**Cost:** adding a fifth ward type means a migration.
**Explains it:** M2.

### ADR-11 — GREEN is never offered a hold

**Decided:** the triage response carries `offer_hold`, and it is `false` for GREEN. The reserve
button is not rendered at all — not disabled, absent.
**Rejected:** letting the user reserve regardless of severity.
**Why:** an ICU bed held for acidity is a bed taken from someone having a heart attack. Making
it visually impossible is a clinical safeguard, not a UI preference.
**Cost:** a user with an under-described serious symptom must rephrase. Accepted, and the advice
text says to call 108.
**Explains it:** M3 for the flag, M6 for the absent button.

### ADR-12 — All time comes from the database, in UTC

**Decided:** `now()` in PostgreSQL is the only clock. Python never generates a timestamp. The
API returns `expires_at` **and** `server_time`; the countdown is their difference.
**Rejected:** `datetime.now()` in Python, or counting down from the browser clock.
**Why:** three machines with three clocks produce three answers. A fifteen-minute reservation
that shows different numbers to the citizen and the hospital is worthless.
**Cost:** display code must convert UTC to IST. One function.
**Explains it:** M5 for the countdown, M2 for the storage rule.

### ADR-13 — `service_role` on the server, RLS enabled with zero policies

**Decided:** Flask holds `service_role` in an environment variable. RLS is on for all five
tables with no policies at all, so the public `anon` key can read nothing. The browser holds
neither key and talks only to our API.
**Rejected:** the browser calling Supabase directly with the anon key and RLS policies.
**Why:** writing correct RLS policies for a transactional hold system is more subtle than
writing the hold function itself, and a policy mistake is silent. Routing everything through one
API means one place to reason about access.
**Cost:** the API is a single point of failure, and there is no authentication in front of it —
see ADR-14.
**Explains it:** M2 and M1 together.

### ADR-14 — No authentication, disclosed rather than hidden

**Decided:** no endpoint requires credentials. We say so, out loud, before anyone asks. The one
abuse control we did build is a partial unique index limiting a phone number to one active hold.
**Rejected:** quietly shipping it and hoping nobody asks; and also building real auth, which
would consume the time the reservation engine needed.
**Why:** authentication for this product means paramedic device certificates and citizen phone
OTP — a procurement and integration problem, not an architecture problem. Building a fake
version would prove nothing.
**Cost:** the honest one. State it in the pitch: *"anyone who can reach the API can create a
hold; here is what production needs."*
**Explains it:** M1. Volunteer it — it converts the project's biggest gap into evidence of
judgement.

### ADR-15 — Real hospital names, simulated capacity, permanent on-screen disclosure

**Decided:** 12 real Kolkata facilities with public names and approximate coordinates; every
bed and blood number invented; a `SIMULATED DATA · DEMONSTRATION ONLY` badge that cannot be
dismissed.
**Rejected:** fictional hospital names (loses all geographic credibility), and unlabelled
invented numbers (misrepresents real institutions).
**Why:** the demo needs a recognisable map, and no real hospital's occupancy may be implied.
**Cost:** none, and it buys credibility — saying it first is stronger than being caught.
**Explains it:** M1 in the opening 50 seconds.

### ADR-16 — One owner per file

**Decided:** every file in [07](07-FILE-MAP-AND-OWNERSHIP.md) has exactly one owner. Nobody
edits another member's file without saying so aloud.
**Rejected:** shared ownership of `app.py` and `custom.css`, the two natural bottlenecks.
**Why:** merge conflicts between first-years cost whole evenings, and the viva requires that one
named person can answer for every line.
**Cost:** the owner of a blocking file becomes a bottleneck. Mitigated by the frozen API
contract and `window.ASHA_MOCK`, so nobody waits on anybody.
**Explains it:** M1.

---

## 2. Risk register

Ordered by how much of the project each one can take down. "Owner" is the person who acts if it
happens, not the person to blame.

| # | Risk | Likelihood | Impact | What we do about it | Owner |
|---|---|---|---|---|---|
| R1 | Venue Wi-Fi fails and Supabase is unreachable | Medium | **Fatal** — nothing works | Two mobile hotspots on two different networks, decided in advance with a named person responsible for switching. Local Flask so only the database needs the network. A local-Postgres fallback was considered and rejected — see Q5. | M1 |
| R2 | Render free tier cold-starts during the demo | High | Looks broken | Demo from `127.0.0.1:5000`; show the Vercel URL as proof of deployment. Keep a health-check tab refreshing. Visible "Waking server…" message. | M1 |
| R3 | A teammate cannot explain their own file | Medium | **Severe** — the jury concludes it was dumped | The rehearsal drill in [13 §9](13-VIVA-DOSSIER.md#9-rehearsal-drill--30-minutes-twice), run twice, a week before. Every "why" that cannot be answered goes into the dossier. | all six |
| R4 | GitHub Insights shows fewer than six contributors | Medium | **Severe** — the specific thing the jury checks | Collect and verify six real GitHub-registered emails **before** the first commit. Check Insights after merging, not on demo morning. **Outstanding — see Q4.** | M1 |
| R5 | Supabase free project pauses after ~7 days idle | Medium | Total, until restored | Open the dashboard weekly. Written into the pre-demo checklist so nobody panics. | M2 |
| R6 | Microphone fails in the demo room | High | Minor | Voice is a feature, not the spine. Type the same phrase instead; the line is scripted in [12 §4](12-DEMO-SCRIPT.md#4-when-something-breaks-on-stage). Never debug a mic on stage. | M5 |
| R7 | Glass renders as flat grey on an old Android | Medium | Cosmetic | The `@supports not (backdrop-filter)` fallback is mandatory and tested. Demo on a known device. | M6 |
| R8 | Timezone confusion makes a countdown look wrong | Low | Confusing on stage | All storage UTC, countdown from `expires_at − server_time`, display converted once. ADR-12. | M5 |
| R9 | The seeded coordinates are visibly wrong on the map | Low | Embarrassing | Verify all 12 against a map before seeding; label distance `~` everywhere. | M2 |
| R10 | A judge asks for authentication and it is absent | High | Minor **if volunteered**, damaging if discovered | ADR-14. Say it first, in the pitch. | M1 |
| R11 | Two members edit the same file and lose work | Medium | Hours | One owner per file (ADR-16). Frozen API contract removes the need. | M1 |
| R12 | The rush script fails live because the ward is not at 1 bed | Medium | Undermines the best moment | Pre-set the ward during setup and re-check after every practice run. The reset SQL is in [10 §6](10-DEPLOYMENT-GUIDE.md#6-reset-the-demo-data-between-runs). | M4 |
| R13 | A Supabase key is committed | Low | **Irreversible** | `.gitignore` before the first commit; `git log -p --all -S 'SUPABASE_KEY='` in the post-merge checklist. If it happens: rotate the key immediately, do not just delete the file. | M1 |
| R14 | Someone raises Gunicorn `--workers` to "make it faster" | Low | Confusing logs, misleading health check | Documented in [10 §1](10-DEPLOYMENT-GUIDE.md#--workers-1-is-deliberate--do-not-raise-it) with the reason. | M1 |
| R15 | The LLM enhancer is enabled late and slows or breaks triage | Low | Moderate | Ships disabled (`TRIAGE_LLM_ENABLED=0`). 4-second timeout and keyword fallback mean the worst case is `engine: "KEYWORD"`. Do not enable it in the week before. | M3 |
| R16 | Demo data left in a strange state from the previous run | High | Wastes the first minute | Run the reset SQL between every practice run and immediately before the real one. | M4 |

**The three that deserve real attention:** R1, R3 and R4. R1 is the only one that can end the
demo outright; R3 and R4 are the only two that can make honest work look dishonest.

---

<a id="open-questions"></a>

## 3. Open questions

**Answered by the team lead on 2026-09-05.** Four of the five are now settled and recorded below
as decisions. One remains outstanding and is the only thing that blocks anything.

### ✅ Q1 — Hosting: **Render + Vercel.** Confirmed.

Flask on Render as a persistent process, Vercel serving `public/`, one Supabase database behind
both. The TTL worker thread runs as designed and Member 4 keeps the live console log as a
demonstrable artefact. Cold start is handled by the three defences in
[10 §4](10-DEPLOYMENT-GUIDE.md#4-the-render-cold-start-problem-and-the-demo-day-plan). No change
to any document.

### ✅ Q2 — LLM triage: **provider-agnostic, shipped disabled.** Confirmed.

`triage_service.py` gets one `call_llm(prompt)` function behind `TRIAGE_LLM_PROVIDER`, with
`TRIAGE_LLM_ENABLED=0` as the shipped default. The keyword engine handles 100% of classification
on its own. Nothing about the demo depends on a key existing, and a provider can be added later by
filling in one function and one environment variable — no restructuring.

### ✅ Q3 — City: **Kolkata.** Twelve facilities, simulated capacity.

Changed from Bengaluru. The twelve are listed with coordinates, type, trauma capability and blood
bank in [03 §7](03-DATABASE-SCHEMA.md#7-seed-data) — eight government and four private, spread
from Shyambazar in the north to Tollygunge and Mukundapur in the south. Specialities are seeded to
match reality, so the triage engine's ward recommendation lands somewhere a Kolkata jury will
recognise as sensible: paediatric strength at B.C. Roy and Chittaranjan Seva Sadan, cardiac at
R.N. Tagore, trauma at SSKM / Medical College / NRS / R.G. Kar / Apollo / Medica.

Every bed and blood number is invented, and ADR-15 still applies in full: the permanent
`SIMULATED DATA · DEMONSTRATION ONLY` badge is not optional, and the coordinates get checked
against a map before the seed is finalised (risk R9).

Documents updated for the change: `03 §7`, `04` (all example payloads), `05 §9.3`, `07`, `08`,
`12`, `14`.

### ✅ Q5 — Offline fallback: **not built.** Hotspots are the plan.

*The question as asked was unclear — restated plainly here, because it is worth understanding.*

The database lives on Supabase's servers, so the app needs **an internet connection to reach it**.
It does not need good internet — a single phone's mobile data is plenty, because all that travels
is small pieces of text. But with *no* connection at all, nothing works.

There were two ways to handle that, and the answer to "it should just work" is the first one:

1. **Two mobile hotspots on two different networks** (say one Jio, one Airtel), agreed in advance,
   with a named person responsible for switching. Costs nothing, adds no code, and covers every
   realistic venue. **This is what we are doing.**
2. Install PostgreSQL on the demo laptop as a second copy of the database. Works with literally no
   internet — but from that day on, every schema change and all six SQL functions must be kept
   identical in two places for the rest of the project. That is a permanent tax on a team of six
   first-years, paid to insure against a venue with no mobile signal.

The app *does* work reliably. Triage is entirely local and needs no network at all. Everything
else needs one working data connection, and a hotspot is one. Recorded as risk R1 with the
mitigation named.

### ⏳ Q4 — The six GitHub emails — still outstanding, and the only real blocker

**What I need:** for each of the six members, a display name and the email **registered on their
GitHub account** (Settings → Emails), or their `<id>+<username>@users.noreply.github.com`
address. Six lines, in the form `Display Name|email`.

**Why it blocks:** an email that is not registered to a GitHub account produces commits that
appear in `git log` but count toward nobody in Insights — which is precisely the tab the jury
opens. One wrong address means one member shows zero contributions, which is worse than not
attempting attribution at all. Fixing it afterwards means rewriting history.

**What it does *not* block:** everything else. All the code can be written, tested and deployed
first; `scripts/setup_git_history.sh` is the last step and needs these six lines the moment you
have them.

---

## 4. Decisions I have deliberately left to implementation

Small enough that documenting them first would be busywork, listed so they are not forgotten:

- Exact keyword weights and the score thresholds for RED / YELLOW (M3 tunes these against the
  40-phrase test table until every case passes).
- Whether the facility list sorts by distance or by "distance among those with capacity" — try
  both with real seeded data and pick what reads better.
- Toast duration, and whether a `NO_CAPACITY` toast auto-dismisses or waits for a tap.
- Whether the desk shows a 12-hour or 24-hour clock. (24, for a hospital — but see it first.)
- The precise wording of the SMS preview payload.
