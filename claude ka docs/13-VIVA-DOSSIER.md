# 13 — VIVA DOSSIER

**Purpose:** every member can explain their own files well enough to survive cross-examination
by someone who writes software for a living.

**How to use this document.** The role summaries, the plain-English explanations and every
scripted answer below are final — study them now. The line-number tables marked
`⟨fill after code⟩` get completed once the code exists, because a line number you have not
verified is worse than no line number at all. When the code is written, each member fills
their own table by actually opening their file.

**The standard to hit:** you can be asked to open your file at a random point and say what
that part does and why it is there. Not memorised recitation — understanding.

---

## 1. What every one of the six must know

These come up regardless of whose file is on screen. Nobody gets to say "that's not my part."

**Q: In one sentence, what is ASHA?**

> "A reservation system for emergency hospital capacity — beds and blood — that holds a
> resource for a specific patient for fifteen minutes so an ambulance can arrive to something
> that is actually still there."

**Q: Why is it called ASHA?**

> "It means *hope* — `आशा` in Hindi, `আশা` in Bengali. Same word in both languages of the city
> we built it for."

If the follow-up is *"as in the ASHA workers?"*, the answer is no affiliation, then:

> "Same intent, different layer. They carry care to the patient; we carry the patient to a bed
> that is actually free."

Never imply a link to the National Health Mission programme. Claiming a government association
you do not have is the one kind of exaggeration a jury can check on their phone in ten seconds.

**Q: How is availability calculated?**

> "Staffed beds, minus occupied, minus active holds that have not yet expired. It is computed
> every time it is read, never stored."

**Q: Why does that matter?**

> "Because it means an expired hold releases the bed with no code running. Nothing has to
> wake up and remember. If a stored counter were used instead, a crash would lose a bed
> permanently."

**Q: What stops two ambulances taking the same bed?**

> "A row-level lock inside a single PostgreSQL function. The second request waits for the
> first to finish, then sees the real number and is refused."

**Q: What did each of you actually build?**

Everyone knows the one-sentence version of all six roles, not just their own. Rehearse this as
a round: each person says their sentence, in order, in under fifteen seconds total each.

**Q: What are you not building, and why?**

> "Hospital HIS integration, a real SMS gateway, and authentication. Those are procurement and
> integration problems, not design problems. We chose to make four things work completely
> instead of ten things partly."

---

## 2. M1 — API and deployment

**Pitch:** *"I built the API surface and the deployment: thirteen endpoints, input validation,
CORS, and the two-host setup."*

**Files:** `app.py`, `validators.py`, `requirements.txt`, `render.yaml`, `vercel.json`,
`.env.example`, `.gitignore`, `public/js/config.js`

### What it does, plainly

`app.py` is the front door. A browser sends an HTTP request; Flask matches the URL to one
function; that function checks the input, calls exactly one service function in
`database.py` or `triage_service.py`, and turns the result into JSON. It contains no medical
logic and no SQL — it is routing and translation only. Every response has the same shape,
`{"ok": true, "data": …}` or `{"ok": false, "error_code": …, "message": …}`, so the frontend
has exactly one thing to handle. `validators.py` is the gate: a phone number must be ten
digits starting 6–9, a ward code must be one of four exact strings, an id must be a real UUID.
Anything else is rejected with 400 before it can reach the database.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| The `/api/health` route and what `ttl_worker_alive` reads | `app.py` | line ___ |
| One route that shows the full pattern: validate → call → envelope | `app.py` | line ___ |
| The CORS setup reading `ALLOWED_ORIGINS` | `app.py` | line ___ |
| The `error_code → HTTP status` mapping | `app.py` | line ___ |
| The phone validator, and why `+91` is stripped | `validators.py` | line ___ |
| The line that serves `public/` so one command runs everything | `app.py` | line ___ |

### Scripted answers

**Q: Why Flask and not FastAPI or Django?**

> "Flask is a URL, a function, and a return value. A first-year can read the whole file top to
> bottom and know what happens. FastAPI's dependency injection and Django's ORM are both
> better tools for a bigger team — they would also mean five of us couldn't explain our own
> repository. That trade was deliberate."

**Q: Your CORS is a wildcard, isn't it?**

> "No — it reads a comma-separated allowlist from `ALLOWED_ORIGINS`. In production that is
> exactly our Vercel domain. And `localhost` and `127.0.0.1` are different origins, so both
> are listed for development."

**Q: Where are your secrets?**

> "Environment variables only. `.env` is gitignored, the Supabase key is set by hand in the
> Render dashboard with `sync: false` in `render.yaml`, and nothing under `public/` ever sees
> it — the browser talks to our API, never to the database. You can check: view-source the
> deployed page and search for `eyJ`. Zero hits."

**Q: Why is the frontend on a different host from the API?**

> "Because our background thread needs a process that stays alive. Vercel's serverless
> functions freeze between requests, so a thread there would silently stop. Render runs an
> ordinary long-lived process. Vercel serves the static files, which is what it is genuinely
> best at."

**Volunteer before asked:** there is no authentication, it is deliberate, and here is what
production would need.

---

## 3. M2 — database and data layer

**Pitch:** *"I built the data layer and the PostgreSQL function that makes double-booking a bed
mathematically impossible."*

**Files:** `database.py`, `supabase_schema.sql`, `supabase_seed.sql`

### What it does, plainly

Five tables: hospitals, ward capacity, blood inventory, holds, triage logs. Two views that
calculate live availability. Six functions that do all the writing. The important idea is that
`ward_capacity` stores three different numbers — `total_physical` (beds that exist),
`total_staffed` (beds with a nurse tonight), `occupied` (patients in them) — and availability
is computed from the *staffed* number, never the physical one. Held beds are not stored as a
count; they are counted from the `holds` table at read time, filtered to `status = 'ACTIVE'
and expires_at > now()`. `database.py` is a thin wrapper: it is the only file in the project
that imports the Supabase library, and each function does one query and returns a plain
dictionary.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| The three bed columns and their constraints | `supabase_schema.sql` | line ___ |
| `occupied_sane` — the CHECK that makes overselling unwritable | `supabase_schema.sql` | line ___ |
| The `expires_at > now()` line in `v_ward_availability` | `supabase_schema.sql` | line ___ |
| `select … for update` inside `create_live_hold` | `supabase_schema.sql` | line ___ |
| The OTP retry loop and `OTP_EXHAUSTED` | `supabase_schema.sql` | line ___ |
| `one_active_hold_per_phone` partial unique index | `supabase_schema.sql` | line ___ |
| The single `.rpc()` call that creates a hold | `database.py` | line ___ |

### Scripted answers

**Q: Walk me through `create_live_hold`.**

> "Seven steps. One: work out the TTL — twenty minutes for a paramedic, fifteen for a citizen.
> Two: refuse if this phone already has an active hold. Three — and this is the important one:
> `select id from ward_capacity where … for update`. That takes a lock on that one ward row.
> Four: *now* read availability, after the lock, and refuse with `NO_CAPACITY` if it is zero.
> Five: generate a four-digit OTP, retrying if it collides with another active hold at the
> same hospital. Six: compute `expires_at` as `now()` plus the interval — database time, never
> Python time. Seven: insert the row and return the OTP and expiry as JSON.
>
> The order of three and four is the whole thing. Lock first, then measure."

**Q: Why not just do that in Python?**

> "Because `supabase-py` talks to PostgREST over HTTP, and there is no transaction spanning
> two HTTP calls. If Python reads 'one bed free' and then inserts, another request can read
> the same 'one bed free' in the gap. That gap cannot be closed from the client. Inside a
> database function, the lock and the insert are one transaction, so the gap does not exist."

**Q: What if your function has a bug and inserts too many?**

> "Then the CHECK constraint `occupied >= 0 and occupied <= total_staffed` rejects the write
> and the transaction rolls back. Three layers: the lock prevents it, the constraint makes it
> unwritable, and the test suite proves both. It should be impossible in two independent ways
> before I'd call a bed count trustworthy."

**Q: Why is `held` not a column? Wouldn't that be faster?**

> "Marginally, and it would be wrong. A stored counter has to be decremented by something, and
> if that something dies between the expiry and the decrement, the bed is lost forever. There
> are forty-eight ward rows in this system — counting is free. I traded a microsecond for
> correctness that does not depend on any process staying alive."

**Q: `service_role` key? That bypasses your row-level security.**

> "Yes, and that is why it lives only on the server. RLS is enabled on all five tables with
> zero policies, which means the public `anon` key can read nothing at all. The browser never
> holds either key — every request goes through our Flask API. If the anon key leaked
> tomorrow, it would grant access to nothing."

**Volunteer before asked:** the seed data's capacity numbers are invented; the hospital names
and coordinates are public.

---

## 4. M3 — triage engine

**Pitch:** *"I built the classifier that turns 'seene mein dard' into RED · Cardiac ICU in six
milliseconds, with or without internet."*

**Files:** `triage_service.py`, `triage_keywords.py`, `tests/test_triage.py`

### What it does, plainly

`triage_keywords.py` is a dictionary of symptom phrases with weights and a target ward —
English, Hindi in Devanagari, and Hinglish in Roman letters, because that is how people
actually type. `triage_service.py` lowercases the input, scans for those phrases, adds up the
weights, and maps the total to RED, YELLOW or GREEN. Before counting a match it checks the
words immediately before it for a negation — "no chest pain" must not score as chest pain.
The ward comes from the highest-weighted match, with an age override: anything mentioning a
child under twelve routes to paediatric ICU. It returns the severity, the ward, the matched
phrases so the user can see the reasoning, and a flag for whether a hold may be offered at
all — GREEN never gets one.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| A keyword entry with its weight and ward | `triage_keywords.py` | line ___ |
| The Hinglish block | `triage_keywords.py` | line ___ |
| The negation window check | `triage_service.py` | line ___ |
| The score → severity thresholds | `triage_service.py` | line ___ |
| The paediatric age override | `triage_service.py` | line ___ |
| The `offer_hold = False` for GREEN | `triage_service.py` | line ___ |
| The LLM timeout and fallback | `triage_service.py` | line ___ |
| The negation test cases | `tests/test_triage.py` | line ___ |

### Scripted answers

**Q: So it is not really AI, it is just keyword matching.**

Do not get defensive. This is your best answer in the whole viva.

> "It is a deterministic weighted classifier, and that was the correct choice for triage
> specifically. Three reasons. It is auditable — I can tell you exactly why any input got the
> answer it got, which a hospital will require and a neural net cannot give you. It works with
> no internet, which is the situation an ambulance in a dead zone is actually in. And it takes
> six milliseconds instead of two seconds.
>
> There *is* an optional LLM enhancer, and it is architecturally interesting: it runs with a
> four-second timeout, it can never block the response, and if it disagrees with the keyword
> engine we take **the more severe** of the two. Over-triage wastes a bed. Under-triage kills a
> patient. That asymmetry is not something I would leave to a model."

**Q: What happens on input you have never seen?**

> "It scores zero and returns GREEN with `matched_keywords` empty and advice to describe the
> symptom differently or call 108. It never guesses RED from nothing, and it never crashes —
> empty string, five hundred characters, emoji only, and an injection attempt are all in the
> test file."

**Q: How do you know your Hindi is right?**

> "Forty phrases in `tests/test_triage.py`, roughly a third of them Hindi or Hinglish, each
> asserting severity and ward. Pick one and I will run it. The lexicon was written from how
> people actually speak, not from a medical textbook — 'saans nahi aa rahi' is in there
> because that is what a relative says on the phone."

**Q: Someone could type nonsense and hold a bed.**

> "Yes — that is an authentication problem, not a triage problem, and we disclose it. The one
> control we built is the unique index limiting a phone number to one active hold, so a single
> person cannot lock up a ward. Production adds phone OTP verification."

---

## 5. M4 — time, expiry and the proofs

**Pitch:** *"I own time in this system: reservations that release themselves, and the tests
that prove three ambulances cannot take one bed."*

**Files:** `ttl_worker.py`, `tests/test_ttl_expiry.py`, `tests/test_holds_race.py`,
`scripts/simulate_ambulance_rush.py`

### What it does, plainly

`ttl_worker.py` is a background thread that wakes every ten seconds, calls
`release_expired_holds()`, and prints one line. That function flips rows whose `expires_at`
has passed from `ACTIVE` to `EXPIRED`. The thread also records a heartbeat timestamp that
`/api/health` reports as `ttl_worker_alive`. The crucial point — and the thing to lead with —
is that **the thread is not what makes expiry work.** Availability already excludes holds
whose `expires_at` has passed, because the view filters on it at read time. So the bed comes
back at the exact second it expires whether or not the worker is running. The worker only
tidies the status column so the desk queue and the history are clean.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| The loop and its `sleep` interval | `ttl_worker.py` | line ___ |
| The `try/except` that keeps a failed cycle from killing the thread | `ttl_worker.py` | line ___ |
| The heartbeat variable `/api/health` reads | `ttl_worker.py` | line ___ |
| `daemon = True` and why | `ttl_worker.py` | line ___ |
| The assertion that the bed returns with the worker stopped | `tests/test_ttl_expiry.py` | line ___ |
| The assertion that the row is still ACTIVE at that moment | `tests/test_ttl_expiry.py` | line ___ |
| The eight-thread barrier | `tests/test_holds_race.py` | line ___ |
| The `granted == 1` assertion | `tests/test_holds_race.py` | line ___ |

### Scripted answers

**Q: What happens if your worker crashes?**

> "Nothing that matters. Beds still release on time, because availability is derived at read
> time — the worker is not in that path. What you lose is tidiness: expired rows keep saying
> ACTIVE until it comes back. `/api/health` reports `ttl_worker_alive: false` so we know. I
> can show you: I'll turn the worker off, expire a hold, and you'll watch the bed come back
> with nothing running."

**Q: Two servers means two of these threads.**

> "Correct, and it is harmless — both call the same function, one flips the rows, the other
> finds nothing to flip. It is redundant work, not a conflict, precisely because expiry does
> not depend on the flip. In production I'd delete the thread entirely and use `pg_cron`
> inside PostgreSQL, which is one scheduler no matter how many servers you run."

**Q: Why not `time.sleep(1)` for a tighter loop?**

> "No benefit. Nothing is waiting on the flip. Ten seconds is a hundred fewer database calls a
> minute for a cosmetic update, and the countdown the user sees is computed from `expires_at`
> minus server time, not from anything the worker does."

**Q: How do I know your race test isn't just running eight requests one after another?**

> "The threads are released by a barrier — they all block until every thread is ready, then go
> at once. The script prints total wall time; eight sequential HTTP round trips could not
> finish in two hundred milliseconds. And the final assertion is on the database, not on the
> responses: exactly one ACTIVE row, and `available_now` is zero and never negative."

**Volunteer before asked:** offer to run the rush script. It is the most persuasive four
seconds in the entire presentation.

---

## 6. M5 — the browser client

**Pitch:** *"I built everything the browser does: the live four-second polling, Hindi voice
input, and the countdown driven by server time."*

**Files:** `public/js/api.js`, `triage.js`, `transit.js`, `ui.js`

### What it does, plainly

`api.js` is the only file in the project that calls `fetch`. It attaches the base URL, unwraps
the `{ok, data}` envelope, retries a failed GET once, and after three seconds of silence shows
"Waking server…" instead of leaving a button looking broken. `triage.js` runs the symptom bar
and the microphone, using the browser's built-in `webkitSpeechRecognition` with `hi-IN` when
Hindi is selected — no audio ever leaves as a file, the browser returns text. `transit.js` owns
the cockpit after a hold succeeds: it computes the countdown from `expires_at` minus the
`server_time` the API returned, so a laptop with a wrong clock still counts down correctly.
`ui.js` renders — cards, ward tiles, toasts — and every piece of text that came from a human
is inserted with `textContent`, never by building an HTML string.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| The single `fetch` wrapper and envelope unwrapping | `api.js` | line ___ |
| The 3-second "waking server" hook | `api.js` | line ___ |
| The 4-second poll and how it avoids flicker | `api.js` | line ___ |
| Where the timer id is stored and cleared | `api.js` / `transit.js` | line ___ |
| `webkitSpeechRecognition` feature detection | `triage.js` | line ___ |
| The `hi-IN` / `en-IN` language switch | `triage.js` | line ___ |
| `expires_at − server_time` — the clock-skew fix | `transit.js` | line ___ |
| A `textContent` assignment on user-supplied text | `ui.js` | line ___ |

### Scripted answers

**Q: Why polling instead of WebSockets?**

> "Bed availability changes every few minutes, not every few milliseconds. A four-second poll
> is one line of code that reconnects itself after the laptop lid closes. A WebSocket needs
> reconnection logic, heartbeats and a different server model — real complexity for latency
> nobody would notice. If this were a trading system I would answer differently."

**Q: Why compute the countdown from server time?**

> "Because a phone's clock can be minutes off. If I counted from the local clock, the user's
> timer and the hospital's timer would disagree, and the one thing a fifteen-minute reservation
> cannot do is show two different numbers. So the server sends `expires_at` *and* its own
> `server_time`, I take the difference once, and count down from that."

**Q: Is the voice input sending audio to a server?**

> "The browser's speech engine does the recognition and hands back text. We never touch an
> audio file, never store one, and never send one to our API — only the transcript, and only
> when the user submits it. If the browser has no speech support the microphone button is not
> rendered at all, rather than sitting there disabled."

**Q: How is your XSS handled?**

> "Anything typed by a human goes into the DOM through `textContent`, never through
> `innerHTML`. It is a project-wide rule in `CLAUDE.md`. The symptom text is the obvious
> vector, and `<script>alert(1)</script>` is one of the cases in the triage test file — it
> renders as literal text."

---

## 7. M6 — design system and the nurse desk

**Pitch:** *"I built the Obsidian Vitals design system and the nurse's one-tap desk that a
hospital can actually use at 3 a.m."*

**Files:** `public/index.html`, `public/hospital.html`, `public/css/custom.css`,
`public/js/desk.js`, `public/fonts/`

### What it does, plainly

`custom.css` holds the design tokens — colours, spacing, durations — and the glass recipe:
four layers, a translucent tint, a backdrop blur, an inset highlight on the top edge, and a
masked hairline border. Every colour in the project comes from a variable there; no HTML file
contains a hex code. There is a mandatory `@supports not (backdrop-filter: blur(2px))` block
so a phone that cannot blur gets solid panels instead of unreadable ones. The desk page is a
deliberate divergence: the same design language but with the glass turned nearly opaque,
because a nursing station is a bright room and a nurse reading a number under fluorescent
light is not the same problem as a citizen on a phone. `desk.js` handles four-box OTP entry
that auto-advances and submits on the fourth digit, and the `[+]` / `[-]` ward taps.

### Be able to point at

| Thing | Where | ⟨fill after code⟩ |
|---|---|---|
| The token block | `custom.css` | line ___ |
| The four layers of `.glass` | `custom.css` | line ___ |
| The `@supports not` fallback | `custom.css` | line ___ |
| The `prefers-reduced-motion` block | `custom.css` | line ___ |
| The ECG keyframes and `--pulse-period` | `custom.css` | line ___ |
| `body.desk` overriding glass alpha | `custom.css` | line ___ |
| The 72px ward buttons | `hospital.html` | line ___ |
| OTP auto-advance and auto-submit | `desk.js` | line ___ |

### Scripted answers

**Q: Isn't glassmorphism an accessibility problem?**

> "It usually is, which is why there are four specific rules. Nothing is ever text on the
> moving background — text sits on a panel with measured contrast. Focus rings are doubled,
> one dark and one light, so they survive on any backdrop. No status is ever colour alone;
> every pill carries a word, so red-green colour blindness loses nothing. And there is a
> `@supports not` fallback to solid panels. Body text measures at least 8:1 against the
> panel it sits on, well past the 4.5:1 requirement."

**Q: Why is the desk page a different shade?**

> "Because it is a different room. A nursing station is brightly lit and the tablet may be at
> arm's length on a counter. Heavy blur behind a number that a nurse reads under fluorescent
> light is decoration working against the user. Same tokens, same components, glass alpha
> raised to 0.90 and blur cut to 10 pixels. It is one documented override, not a second design
> system."

**Q: Does all this animation not make it slow?**

> "There is a budget. Never more than eight blurred elements on screen at once — blur is the
> expensive property, and it is the only one that actually costs. Animations only touch
> `transform` and `opacity`, which the compositor handles, and nothing animates a blur value
> ever. All motion collapses under `prefers-reduced-motion`. It was tested on a mid-range
> Android phone, not just on a laptop."

**Q: Would a nurse actually use this?**

> "It replaces a twelve-field admin form with four buttons. Seventy-two-pixel targets, usable
> with gloves on, no free text to type, and numbers big enough to read from a metre away. The
> honest test is what happens when she is busy: the current system gets ignored at 3 a.m.,
> which is exactly when the data matters most. Ours needs one tap."

---

## 8. When you do not know

You will be asked something nobody prepared for. There is a correct move and it is not
bluffing — engineers on a jury detect invented answers instantly and remember them.

> "I don't know that offhand — that is *(name)*'s file and they can answer it precisely."

or, if it is genuinely your area:

> "I haven't tested that case. My instinct is *(reasoning)*, but I would want to run it before
> telling you it works."

That second answer scores better than a confident wrong one. Saying "I would want to test it"
about your own code is a sign of someone who ships things that work.

**Never do these:** claim a feature that does not exist; say "the AI handles it" about the
keyword engine; blame a teammate for something visibly broken; argue with a judge who has
found a real flaw. Say "that is a real gap, here is what I would do about it," and move on.

---

## 9. Rehearsal drill — 30 minutes, twice

Do this at least a week before, with the code open.

**Round 1 — solo (5 min each).** Each member opens their main file and talks through it
top to bottom to the other five. Anyone may interrupt with "why?" at any line. If a "why"
cannot be answered, the answer goes into the table in this document.

**Round 2 — cross-examination (5 min each).** Each member is questioned by the teammate who
reviewed their pull request — that person has already read the file and will ask real
questions. Reviewer pairs are in
[08 §2](08-GIT-WORKFLOW.md#2-branch-strategy): M2←M4, M3←M1, M1←M2, M4←M3, M6←M5, M5←M6.

**Round 3 — the whole demo, timed, no notes.** Someone who is not presenting holds the
stopwatch and calls out the eight-minute mark. Run it three times total with a data reset
between runs. The third run is when you find the thing the first two hid.
