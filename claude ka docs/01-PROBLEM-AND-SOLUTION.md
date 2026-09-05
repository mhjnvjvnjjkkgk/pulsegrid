# 01 — PROBLEM AND SOLUTION

> **The name.** **ASHA** — `आशा` in Hindi, `আশা` in Bengali — means **hope**. It is one of
> the few words that is the same in both languages of the city we built this for, and it is
> what a family is holding on to in the hour this system exists to protect. Say the meaning
> out loud in the pitch; it takes four seconds and it is the only branding we have.
>
> One thing to know before a judge says it: **ASHA is also the name of India's one-million-strong
> cadre of Accredited Social Health Activists.** That collision is an advantage, not a problem —
> ASHA workers are the last mile of Indian public health, and this is a last-mile tool. If asked,
> the answer is: *"Same intent, different layer. They carry care to the patient; we carry the
> patient to a bed that is actually free."* Do not claim any affiliation with the NHM programme.

## 1. The clinical fact we are built around

For cardiac arrest, polytrauma, stroke and maternal haemorrhage, survival probability
falls steeply during the first 60 minutes after injury — the **Golden Hour**. Time lost is
not recoverable by better treatment later.

In Indian emergency transport, a large share of that hour is spent on a specific, fixable
failure: **the ambulance arrives at a hospital that cannot admit the patient.** The driver
then re-routes, and the clock keeps running.

## 2. Why that happens — four distinct failures

### Failure 1: Directories, not reservation systems

Public tools such as bed dashboards and blood-stock portals are **read-only**. They answer
"how many beds existed at the last update?" They cannot answer "is one held for me?"
Reading a number is not the same as owning a resource. A flight-booking site that only
*displayed* seat counts without letting you book would be useless — that is the current
state of emergency capacity in India.

### Failure 2: The Ghost Bed

A bed is only usable if there is a **nurse and a doctor assigned to it**. Portals count
physical beds. So a hospital can truthfully report "6 ICU beds" while being able to admit
zero patients, because the night shift is short-staffed. The ambulance is rejected at the
gate and the portal was never technically lying.

> **ASHA's answer:** we store `total_physical` **and** `total_staffed` as separate
> columns, and every availability calculation uses `total_staffed` only. We also surface
> the gap between them (`ghost_gap`) so district administrators can see where staffing,
> not construction, is the bottleneck.

### Failure 3: The Race Condition

Three ambulances load the same page. All three see `ICU: 1 available`. All three drive.
One patient is admitted; two are turned away having burned 20 minutes each. Nothing in the
system was broken — the data was *accurate for everyone and useful to nobody*, because
reading is not reserving.

> **ASHA's answer:** the **Live Token Hold**. The first request to arrive receives a
> lock on that bed plus a 4-digit code. The second request sees `0 available` within
> milliseconds and is routed elsewhere *before* the ambulance moves. The correctness of
> this is enforced inside PostgreSQL, not in application code — see
> [03-DATABASE-SCHEMA](03-DATABASE-SCHEMA.md#5-the-atomic-hold--the-most-important-half-page-in-this-project).

### Failure 4: Update friction

An emergency-ward nurse at 2 a.m. will not open a browser, log into a state portal, find
her facility, and edit a spreadsheet cell. Any system that requires her to do so contains
stale data by design. **Data freshness is a user-experience problem, not a database
problem.**

> **ASHA's answer:** a tablet screen mounted at the nursing station showing four
> giant ward tiles with `[+]` and `[-]` buttons. One tap, no login, no navigation, sub-second
> confirmation. Plus a simulated SMS / WhatsApp fallback path for facilities with no tablet.

## 3. What ASHA is

A **triage and resource-reservation engine** with four capabilities:

1. **Live Token Hold (TTL reservation).** A soft lock on a bed or blood unit —
   15 minutes for a citizen request, 20 minutes for a verified paramedic — released
   automatically if the patient does not arrive, so a no-show cannot freeze capacity.

2. **Multimodal triage.** The patient's condition is classified **RED / YELLOW / GREEN**
   from typed text, spoken voice (browser speech recognition, English + Hindi), or a
   single category tap. Severity determines *which ward* we search, not just how fast.

3. **Component-specific blood tracking.** PRBC, platelets and plasma are tracked
   separately per blood group, because "2 units of O-negative" means nothing until you know
   whether it is red cells or plasma. We also flag **trauma-reserve** stock (issued with no
   replacement donor required) versus stock that needs a donor — the practical difference
   between blood you can actually get at 3 a.m. and blood you cannot.

4. **Zero-overhead hospital integration.** The one-tap tablet desk described above.

## 4. Scope discipline — what we are deliberately NOT building

Saying this out loud to judges is a strength, not a weakness. It shows engineering
judgement.

| Not building | Why | What we do instead |
|---|---|---|
| Real hospital HIS/EMR integration | Requires government MoUs and hospital IT access; impossible in a hackathon | A clean `POST /api/hospital/counter` endpoint that any HIS could call — integration-ready, not integrated |
| Real SMS/WhatsApp gateway | Needs a paid provider and DLT registration in India | The message payload is generated and logged verbatim, so the pipe is the only missing piece |
| Payments / insurance | Not the bottleneck in the Golden Hour | — |
| Real GPS routing engine | Google Maps Directions API is paid at scale | Straight-line (haversine) distance for ranking + a map link that opens the user's own maps app |
| Native mobile apps | A responsive web app installs nowhere and works on every phone | Mobile-first responsive layout |
| Doctor/patient login accounts | Authentication is a solved, boring problem and would eat our build time | Phone number + OTP proof-of-hold, which is the only identity the workflow actually needs |

## 5. The measurable claim

> If hospital capacity is *reservable* rather than merely *visible*, the number of gate
> rejections per emergency transport approaches zero, and the minutes saved come directly
> out of the Golden Hour.

That is the sentence to say in the first 20 seconds of the pitch.
