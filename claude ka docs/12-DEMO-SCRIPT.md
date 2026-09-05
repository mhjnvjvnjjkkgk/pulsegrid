# 12 — DEMO SCRIPT

Eight minutes, six speakers, one rehearsed sequence. Every member talks about the part they
built, which is also how the jury verifies that six people built it.

**Print this. Rehearse it three times end to end with a data reset between runs.**

---

## 1. Before you walk in

**Stage setup**

```
┌──────────────────────────┐   ┌──────────────────────────┐
│  LAPTOP 1 — projected    │   │  LAPTOP 2 — projected    │
│  127.0.0.1:5000          │   │  Supabase → holds table  │
│  the citizen screen      │   │  auto-refresh ON         │
└──────────────────────────┘   └──────────────────────────┘
        ┌────────────────────┐        ┌──────────────┐
        │ TABLET / LAPTOP 3  │        │ PHONE        │
        │ /hospital.html     │        │ citizen page │
        │ the nurse desk     │        │ already open │
        └────────────────────┘        └──────────────┘
```

**Checklist, ten minutes before the slot**

- [ ] Smoke test from [11 §4](11-TEST-PLAN.md#4-pre-demo-smoke-test--3-minutes-run-it-the-morning-of) done
- [ ] Reset SQL run — every ward back to 70% occupancy, `holds` empty
- [ ] One ward pre-set to exactly **1 available** for the race moment
- [ ] `TTL_WORKER_ENABLED=1`, console visible on an alt-tab
- [ ] Notifications off, zoom 100%, DevTools closed, screensaver off
- [ ] Phone on the hotspot, page loaded, screen brightness up
- [ ] Terminal open in a second tab, `simulate_ambulance_rush.py` command already typed but
      **not yet run**

---

## 2. The eight minutes

### 0:00 – 0:50 · **M1 — the problem**

Say this almost word for word. It is the only part of the demo that must be memorised.

> "A patient with a heart attack has about one hour. In that hour, an ambulance in Kolkata
> calls hospitals one at a time and asks 'do you have an ICU bed?' Every existing portal —
> e-RaktKosh, the municipal bed dashboards — can only *display* a number. None of them can
> *reserve* anything. So three ambulances read the same '1 bed free' and all three drive to
> the same hospital. Two of them lose the hour.
>
> ASHA — `আশা`, *hope* — is not another dashboard. It is a reservation system for emergency
> capacity. And everything you see in the next seven minutes is live — this is a real database,
> and one of my teammates will try to break it on purpose."

*(Say `আশা` in a Kolkata room and `आशा` in a Hindi-speaking one — the word is the same in both.
Four seconds, and it is the only piece of branding this project has.)*

Then point at the badge on screen: `SIMULATED DATA · DEMONSTRATION ONLY`.

> "The hospital names and locations are real and public. Every bed count is simulated — we are
> demonstrating the mechanism, not publishing clinical data."

**Why say that out loud:** a judge who spots it themselves wonders what else you hid. A judge
who hears it from you concludes you are careful.

---

### 0:50 – 1:40 · **M3 — triage**

Type into the box, do not paste:

```
seene mein bahut dard hai, saans nahi aa rahi
```

> "That is Hinglish — Hindi words in Roman letters — which is how people in most of India
> actually type. Six milliseconds, no internet, no AI service: **RED, Cardiac ICU.**"

Point at the matched-keywords chips.

> "It shows you *why*. `seene mein dard`, `saans nahi aa rahi`. A black box that says 'RED'
> is not usable in a hospital. A system that shows its reasoning is."

Then the one-line proof that it is not a lookup table:

```
no chest pain, just acidity
```

> "**GREEN.** The word 'chest pain' is right there and it still says green, because negation
> is handled. And notice — for green there is no reserve button anywhere on this page. You
> cannot hold an ICU bed for acidity. That is a design decision, not a missing feature."

---

### 1:40 – 3:00 · **M5 — the live map and the ghost bed**

> "Twelve facilities, sorted by distance, refreshing every four seconds."

Point to one card's staffed rail.

> "This hospital has 20 physical ICU beds. Only 14 are staffed tonight. Six beds exist and
> cannot take a patient — the industry calls them **ghost beds**, and they are the single
> biggest reason bed dashboards lie. We never show physical beds as availability. Ever."

**Now hand to M6 for four seconds** — M6 opens the desk on the tablet and drops staffed beds
from 14 to 11 while 11 patients are in. Back on the citizen screen, that ward flips to `FULL`
within four seconds, with the amber gap chip.

> "A nurse just told us three staff went home. The bed count on the public screen changed
> before she put the tablet down. No admin portal, no data-entry form, one control."

Then create the hold on the phone, held up to the judges:

> "Chest pain, cardiac ICU, one tap."

**OTP appears. Point at Laptop 2.**

> "Watch the database, not my phone."

The row appears in front of them.

---

### 3:00 – 3:50 · **M6 — the desk**

On the tablet:

> "This is what a nurse sees at 3 a.m. Big numbers, four buttons, no training. The inbound
> queue shows who is coming and how long the bed is held."

Type the OTP into the four boxes.

> "The ambulance arrives, reads out the code, one tap."

Green admit banner.

> "Held becomes occupied. The reservation is now a patient. Total time from symptom to
> confirmed bed: under forty seconds, and nobody made a phone call."

---

### 3:50 – 5:00 · **M4 — the two proofs**

This is the moment the demo is built around. Slow down.

> "Everything so far could be faked with a nice front end. So here is the part that cannot be."

Set the stage in one line, then run it:

```bash
python scripts/simulate_ambulance_rush.py --hospital-id <uuid> --ward adult_icu --requests 8
```

> "One staffed bed. Eight ambulances, eight threads, simultaneously."

```
granted=1  refused=7  beds_oversold=0
PASS — one bed, one patient.
```

> "One granted, seven refused with alternatives, zero oversold. That is not application code
> being careful — the winner is decided by a row lock inside PostgreSQL, so it is correct
> even if our Python is wrong."

Then the second proof:

> "Second question: what happens when your server dies holding a reservation?"

Turn off the worker, force one hold's expiry into the past in Supabase, refresh the citizen
page.

> "The bed is available again. **No code ran.** Availability is calculated at read time, so
> an expired hold stops counting the instant it expires. Our background cleaner is
> housekeeping — if it dies, nothing breaks. Most systems make the opposite choice and lose
> beds when a process crashes."

---

### 5:00 – 5:50 · **M2 — why it is correct**

One slide or one whiteboard line. No code on screen.

> "Availability is never stored. It is computed:
>
> **staffed − occupied − active holds that have not yet expired.**
>
> Three things follow from that one decision. Expiry needs no scheduler. A crashed process
> cannot leak a bed. And the number on the citizen's phone and the number on the nurse's
> tablet cannot disagree, because there is only one number and it lives in the database.
>
> On top of that there is a database constraint that makes occupancy above staffed capacity
> *impossible to write* — so even a bug in our own code cannot oversell a ward."

---

### 5:50 – 7:00 · **M1 — scope, honesty, and what comes next**

> "What this is: a working transactional allocation layer, twelve facilities, forty-eight
> wards, blood components tracked separately because platelets and packed cells are not
> interchangeable.
>
> What it is not: we do not integrate with hospital HIS systems, we do not send real SMS, and
> there is no login. Those are integrations and procurement, not architecture — and we would
> rather show you four things that work completely than ten that half work.
>
> To deploy this for real, a district needs three things from each hospital: a tablet, one
> nurse trained for ten minutes, and the staffed-bed number updated per shift. That is the
> whole adoption cost. Everything else is already here."

Close on the number:

> "Right now, across these twelve hospitals, there are **thirty-seven ghost beds** — beds that
> exist and cannot take a patient. Until somebody counts that number, nobody can fix it."

**Read the real figure off `GET /api/stats` (`ghost_beds_citywide`) on the morning of the demo
and say that number.** It changes with the seed and with anything the desk did during practice.
Quoting a stale number is the one way this line can backfire.

---

### 7:00 – 8:00 · buffer

Do not fill it. Stop early and let the questions start. A demo that ends 40 seconds early
looks controlled; one that runs 40 seconds over looks like it got away from you.

---

## 3. Q&A — who answers what

Assign these now. A member who answers about their own file sounds like an engineer; a lead
who answers everything sounds like a one-person project.

| Question | Answers | The core of the answer |
|---|---|---|
| "How do you stop double-booking?" | **M2** | Row lock inside one PostgreSQL function + a CHECK constraint. Offer to rerun the rush script. |
| "What if your background worker dies?" | **M4** | Availability is derived at read time. Show S3 from the test plan. |
| "What if you scale to two servers?" | **M4** | Already survives it — duplicate janitors are redundant, not dangerous. Production moves it to `pg_cron`. |
| "Is the AI real? What model?" | **M3** | Deterministic weighted keyword engine, deliberately: it is auditable, works offline, and 6 ms. The LLM is an optional enhancer that can never block or downgrade a result. |
| "Why not React / microservices?" | **M1** | Six first-years, five weeks. Vanilla JS ships and every one of us can explain every line. Name the tradeoff, do not apologise for it. |
| "Where is authentication?" | **M1** | Absent, deliberately, and disclosed. Production: device certs for desks, phone OTP for citizens. We built one abuse control — one active hold per phone number, enforced by a unique index. |
| "Real bed data?" | **M1** | Simulated, stated on screen. The mechanism is what is being demonstrated. |
| "Is this connected to the ASHA worker programme?" | **M1** | No, and we claim no affiliation. The word means *hope* in Hindi and Bengali. Then the one-liner: *"Same intent, different layer — they carry care to the patient, we carry the patient to a bed that is actually free."* |
| "Would a nurse actually use it?" | **M6** | Four buttons, 72-pixel targets, no free text, works in gloves. Compare to the twelve-field admin form it replaces. |
| "Hindi accuracy?" | **M3** | Lexicon covers Hindi and Hinglish; forty test phrases in the repo. Read one out and let them watch. |
| "What did *you* build?" | **each** | One sentence, from the pitch column in [07 §2](07-FILE-MAP-AND-OWNERSHIP.md#2-ownership-table-with-size-estimates). Everyone should be able to say theirs without thinking. |

---

## 4. When something breaks on stage

It will. What matters is the next ten seconds. Each of these is a line to say, not a thing to
debug in front of judges.

| Symptom | Say this, then do this |
|---|---|
| Page hangs on first click | "That is the free tier waking up — thirty seconds." Switch to the local laptop. |
| Hospital list empty | "Let me switch to the local build." Laptop 1 local is already running. |
| Mic does not work | "Voice needs Chrome and a mic permission — here it is typed instead." Never fight a mic on stage. |
| Hold button refuses | *Check the ward is not already full.* "That ward filled up during setup — here is another." A refusal is your feature working; say so. |
| Wi-Fi dies | Phone hotspot #2. Decided in advance who switches. |
| Total freeze | Alt-tab to the Supabase table. "While that recovers — here is the data model, which is the actual contribution." |

**The rule:** nobody troubleshoots silently. One person keeps talking while one person fixes.
Agree who does which before you walk in.

---

## 5. The three sentences that matter most

If the jury remembers nothing else:

1. **"Every other system displays capacity. Ours reserves it."**
2. **"One bed, eight ambulances, one winner — decided by the database, not by our code."**
3. **"A hold expires correctly even if every one of our processes is dead."**

Each of those maps to something you show them running. Say the sentence, then show the proof —
never the other way around.
