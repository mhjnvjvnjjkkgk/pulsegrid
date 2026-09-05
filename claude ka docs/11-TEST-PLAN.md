# 11 — TEST PLAN

Three layers: automated tests that must pass, manual scenarios that must be walked before the
demo, and the two proofs that are worth showing a judge live.

---

## 1. Automated tests

`python -m pytest tests/ -v`

### `tests/test_triage.py` — Member 3

A table of 40 real phrases with expected severity and ward. Table-driven so adding a case is
one line.

| Phrase | Expected |
|---|---|
| `severe chest pain radiating to left arm` | RED · `cardiac_icu` |
| `seene mein bahut dard hai` | RED · `cardiac_icu` |
| `saans nahi aa rahi, hoth neele pad gaye` | RED · `adult_icu` |
| `road accident, heavy bleeding from leg` | RED · `adult_icu`, `needs_blood: true` |
| `behosh ho gaya hai, jawab nahi de raha` | RED · `adult_icu` |
| `2 saal ka bacha, tez bukhar aur jhatke` | RED · `pediatric_icu` |
| `labour pain since 3 hours with bleeding` | RED · `adult_icu` (maternity → trauma-capable) |
| `breathless while walking, oxygen 91` | YELLOW · `general_oxygen` |
| `fractured wrist, conscious and stable` | YELLOW · `general_oxygen` |
| `mild fever since morning` | GREEN · `null` |
| `small cut on finger` | GREEN · `null` |
| `no chest pain, just acidity` | GREEN · `null` ← **negation must work** |
| `patient had chest pain last week, fine now` | GREEN or YELLOW, **not RED** ← past-tense handling |

Assertions on every case: `severity`, `recommended_ward`, `offer_hold`, and that
`matched_keywords` is non-empty whenever severity is not GREEN.

Plus these properties, checked over all 40:

- The classifier never returns 5xx, for any input including empty string, 500 chars of
  `"a"`, emoji-only, and `"<script>alert(1)</script>"`.
- Response time under 50 ms with the LLM disabled.
- With the LLM enabled and the key deliberately invalid, every case still returns a valid
  result with `engine: "KEYWORD"`.

### `tests/test_ttl_expiry.py` — Member 4

The point of this file is to prove the claim in
[02 §4](02-SYSTEM-ARCHITECTURE.md#4-hard-problem-1--availability-must-be-correct-even-when-the-worker-is-dead).

1. Read `available_now` for a ward. Call it `A`.
2. Create a hold. Assert `available_now == A - 1`.
3. **With the worker never running**, force `expires_at` into the past:
   `update holds set expires_at = now() - interval '1 second' where id = …`
4. Assert `available_now == A` again. **The bed came back with no code executing.**
5. Assert the row is still `status = 'ACTIVE'` — proving that availability does not depend on
   the status flip.
6. Now call `release_expired_holds()`. Assert the row is `EXPIRED` and `available_now` is
   still `A`.

Step 4 is the whole test. If it fails, the architecture is wrong, not the test.

### `tests/test_holds_race.py` — Member 4

The double-booking proof.

1. Set a ward to exactly 1 available.
2. Fire **8 concurrent** `create_live_hold` calls from 8 threads, each with a different phone
   number.
3. Assert exactly **1** returned `ok: true` and exactly **7** returned `NO_CAPACITY`.
4. Assert `select count(*) from holds where status='ACTIVE' and ward_code=…` is exactly 1.
5. Assert `available_now == 0`, never negative.

Also in this file:

- Same phone twice → the second gets `DUPLICATE_HOLD`.
- Redeem the same OTP twice concurrently → exactly one succeeds, `occupied` increments by
  exactly 1.
- `update_quick_counter` with `delta = 5` → `BAD_DELTA`.
- `[-]` at `occupied = 0` → `ALREADY_EMPTY`, and `occupied` never goes negative.
- 200 sequential `[+]`/`[-]` taps → `occupied` lands exactly where arithmetic says, and the
  `CHECK` constraint is never violated.

---

## 2. Manual scenarios — walk all nine before the demo

Tick these on a printed sheet. Do not trust memory.

### S1 — The happy path
Type `severe chest pain`. Expect RED · Cardiac ICU. Pick a hospital with capacity. Create the
hold. Note the OTP. On the desk, enter that OTP. Expect green admit banner, and the ward
`occupied` up by 1 and `held` down by 1.

### S2 — The race (two browsers)
Set a ward to 1 available (`update ward_capacity set occupied = total_staffed - 1 where …`).
Open two browser windows side by side, both on that hospital. Click **Request Hold** in both
as close to simultaneously as you can. Expect one OTP and one `That resource was just taken`
toast with alternatives. **Rehearse this — it is your strongest live moment.**

### S3 — Expiry without the worker
Set `TTL_WORKER_ENABLED=0`, restart, create a hold, then in Supabase run
`update holds set expires_at = now() - interval '1 second' where status='ACTIVE';`
Refresh the citizen page. The bed is available again. The worker never ran.

### S4 — Expiry with the worker
`TTL_WORKER_ENABLED=1`. Create a hold. In Supabase set `expires_at` to 5 seconds from now.
Watch the console print `released 1 stale reservation` within 10 seconds, and the desk queue
card disappear.

### S5 — Ghost bed
On the desk, drop Adult ICU `total_staffed` from 14 to 11 while `occupied` is 11. The citizen
page immediately shows that ward as `FULL` and stops offering it, with the amber `⌀` chip
showing the gap. `total_physical` never changed.

### S6 — Voice, in Hindi
Click the mic. Say `saans nahi aa rahi hai`. Expect the transcript in the input and
RED · Adult ICU. Test in Chrome; note in advance which of your laptops has a working mic.

### S7 — GREEN protection
Type `mild fever`. Expect GREEN and **no hold button anywhere on the page**.

### S8 — Offline behaviour
With the app open, stop Flask (`Ctrl-C`). Within 8 seconds: ECG flatlines, offline banner
appears, the hospital list stays on screen dimmed with a data-age label. Restart Flask —
everything recovers with no page refresh.

### S9 — Phone
Load the deployed URL on a real Android phone over mobile data. Check: tap targets, glass
rendering, mic permission prompt, countdown legibility in sunlight, and that the layout holds
at 320 px.

---

## 3. The two live proofs

Rehearse these until they are boring. They are what separates a working prototype from a
convincing one.

### Proof 1 — `scripts/simulate_ambulance_rush.py`

```bash
python scripts/simulate_ambulance_rush.py --hospital-id <uuid> --ward adult_icu --requests 8
```

```
[RUSH] Ward adult_icu has 1 staffed bed free.
[RUSH] Firing 8 simultaneous hold requests from 8 threads…

  ambulance-1   ✓ GRANTED    otp 5821    expires 15:04:12
  ambulance-2   ✗ NO_CAPACITY
  ambulance-3   ✗ NO_CAPACITY
  ambulance-4   ✗ NO_CAPACITY
  ambulance-5   ✗ NO_CAPACITY
  ambulance-6   ✗ NO_CAPACITY
  ambulance-7   ✗ NO_CAPACITY
  ambulance-8   ✗ NO_CAPACITY

[RUSH] granted=1  refused=7  beds_oversold=0
[RUSH] Wall time for all 8: 214 ms
[RUSH] PASS — one bed, one patient.
```

Run this on stage. It takes four seconds and answers the hardest question before it is asked.

### Proof 2 — the Supabase table, projected live

Second laptop showing the Supabase `holds` table with auto-refresh on. When you tap **Request
Hold** on the phone, the row appears in front of the judges. When it expires, they watch
`status` change to `EXPIRED`. Nothing you can say is as convincing as a database row appearing
on its own.

---

## 4. Pre-demo smoke test — 3 minutes, run it the morning of

- [ ] `python -m pytest tests/ -q` → all pass
- [ ] `curl /api/health` → `ttl_worker_alive: true`
- [ ] Reset script from [10 §6](10-DEPLOYMENT-GUIDE.md#6-reset-the-demo-data-between-runs) has been run
- [ ] Citizen page: 12 hospitals visible
- [ ] One hold created and redeemed successfully
- [ ] `simulate_ambulance_rush.py` prints PASS
- [ ] Desk page: all four ward tiles respond to `[+]` and `[-]`
- [ ] Mic works on the demo laptop, in the demo room, with the demo browser
- [ ] Phone is charged, on the hotspot, and the page is already loaded
- [ ] Supabase tab open on the second laptop
- [ ] Browser zoom at 100%, DevTools closed, notifications silenced, dark room lights checked

---

## 5. Known limitations — write these down, do not be caught by them

Stating a limitation before a judge finds it converts a weakness into evidence of rigour.

| Limitation | The honest answer |
|---|---|
| No authentication on any endpoint | Deliberate prototype scope. Production needs paramedic device tokens and citizen phone OTP. The `one_active_hold_per_phone` index is the abuse control we *did* build. |
| Capacity numbers are simulated | Stated permanently on screen and in the pitch. Hospital names and coordinates are public; every bed count is invented. |
| Distance is straight-line, not road | Labelled `~` everywhere. Road routing is a paid API and does not change the reservation logic we are proving. |
| No SMS actually sends | The exact payload is generated and displayed. A gateway is a paid integration, not a design problem. |
| One Flask process | The design already tolerates multiple — see [10 §1](10-DEPLOYMENT-GUIDE.md#--workers-1-is-deliberate--do-not-raise-it). |
| Hospital desk has no login | Same as above; a real desk binds to a device certificate. |
| Free Supabase pauses after 7 days idle | Open the dashboard weekly. Note it now so nobody panics on the day. |
