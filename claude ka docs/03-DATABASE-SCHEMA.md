# 03 — DATABASE SCHEMA

**Owner:** Member 2. **File it becomes:** `supabase_schema.sql` (+ `supabase_seed.sql`).

Run the schema file once in **Supabase → SQL Editor → New query → Run**. It is safe to
re-run: it drops and rebuilds everything.

---

## 1. Mental model in five sentences

1. `hospitals` — who they are and where they are. Slow-changing.
2. `ward_capacity` — one row per hospital per ward type. Holds the **physical** and the
   **staffed** bed counts, and how many are **occupied** right now.
3. `blood_inventory` — one row per hospital per blood group per component.
4. `holds` — one row per reservation, ever. This is the heart of the system and the only
   table that grows quickly.
5. **There is no `held` column anywhere.** How many beds are held is *counted* from
   `holds` every time we look. That is what makes expiry automatic — see
   [02 §4](02-SYSTEM-ARCHITECTURE.md#4-hard-problem-1--availability-must-be-correct-even-when-the-worker-is-dead).

The one formula the whole product rests on:

```
available_now  =  total_staffed  −  occupied  −  (count of ACTIVE holds whose expires_at is still in the future)
```

Note what is *absent* from that formula: `total_physical`. A bed nobody is staffed to
attend is not a bed. That single omission is our answer to the Ghost Bed problem.

---

## 2. The four ward codes

We use exactly these strings, everywhere, forever. No plurals, no capitals, no spaces.

| `ward_code` | Display name | Triage severity that routes here |
|---|---|---|
| `adult_icu` | Adult ICU | RED — trauma, poisoning, stroke, general critical |
| `pediatric_icu` | Pediatric ICU | RED — patient under 12 |
| `cardiac_icu` | Cardiac ICU / CCU | RED — chest pain, cardiac arrest, arrhythmia |
| `general_oxygen` | General Oxygen Ward | YELLOW — breathlessness, fever with hypoxia, stable fractures |

GREEN never routes to a ward. GREEN patients are advised to a local clinic and are **not
offered a hold** — protecting ICU capacity from non-emergencies is a feature, and judges
notice it.

---

## 3. Full schema SQL

```sql
-- ============================================================================
--  ASHA — PostgreSQL / Supabase schema
--  Run the whole file. Safe to re-run (it drops first).
-- ============================================================================

-- ---------- 0. Drop everything, so this file is repeatable -------------------
drop view     if exists v_ward_availability   cascade;
drop view     if exists v_blood_availability  cascade;
drop function if exists create_live_hold      cascade;
drop function if exists redeem_hold           cascade;
drop function if exists cancel_hold           cascade;
drop function if exists release_expired_holds cascade;
drop function if exists update_quick_counter  cascade;
drop function if exists set_staffed_beds      cascade;
drop table    if exists holds                 cascade;
drop table    if exists triage_logs           cascade;
drop table    if exists blood_inventory       cascade;
drop table    if exists ward_capacity         cascade;
drop table    if exists hospitals             cascade;


-- ---------- 1. hospitals -----------------------------------------------------
create table hospitals (
  id               uuid primary key default gen_random_uuid(),
  name             text not null,
  short_name       text,                       -- shown on small mobile cards
  city             text not null,
  address          text,
  lat              double precision not null,  -- for distance ranking
  lng              double precision not null,
  phone            text,
  is_trauma_center boolean not null default false,
  has_blood_bank   boolean not null default false,
  is_govt          boolean not null default false,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
```

```sql
-- ---------- 2. ward_capacity -------------------------------------------------
create table ward_capacity (
  id             uuid primary key default gen_random_uuid(),
  hospital_id    uuid not null references hospitals(id) on delete cascade,
  ward_code      text not null,
  total_physical int  not null default 0,   -- beds that exist as furniture
  total_staffed  int  not null default 0,   -- beds with a nurse assigned THIS SHIFT
  occupied       int  not null default 0,   -- patients physically in a bed now
  updated_at     timestamptz not null default now(),

  constraint ward_code_valid
    check (ward_code in ('adult_icu','pediatric_icu','cardiac_icu','general_oxygen')),

  -- You cannot staff more beds than you own.
  constraint staffed_within_physical
    check (total_staffed >= 0 and total_staffed <= total_physical),

  -- THE SAFETY CONSTRAINT: the database itself refuses to overbook a ward.
  -- Even a future bug in a Flask route cannot violate this.
  constraint occupied_sane
    check (occupied >= 0 and occupied <= total_staffed),

  constraint one_row_per_ward unique (hospital_id, ward_code)
);


-- ---------- 3. blood_inventory ----------------------------------------------
create table blood_inventory (
  id              uuid primary key default gen_random_uuid(),
  hospital_id     uuid not null references hospitals(id) on delete cascade,
  blood_group     text not null,
  component       text not null,
  units_available int  not null default 0,

  -- TRUE  = emergency trauma stock, released with no replacement donor needed.
  -- FALSE = ordinary stock.  This distinction is the difference between blood
  --         you can actually obtain at 3 a.m. and blood you cannot.
  is_trauma_reserve          boolean not null default false,
  requires_replacement_donor boolean not null default true,
  updated_at      timestamptz not null default now(),

  constraint blood_group_valid
    check (blood_group in ('O-','O+','A-','A+','B-','B+','AB-','AB+')),
  constraint component_valid
    check (component in ('PRBC','PLATELETS','PLASMA')),
  constraint units_sane   check (units_available >= 0),
  constraint one_row_per_stock unique (hospital_id, blood_group, component)
);
```

```sql
-- ---------- 4. holds  (the heart of ASHA) -------------------------------
create table holds (
  id              uuid primary key default gen_random_uuid(),
  hospital_id     uuid not null references hospitals(id) on delete cascade,
  resource_kind   text not null,               -- 'BED' or 'BLOOD'
  ward_code       text,                        -- filled when resource_kind = 'BED'
  blood_group     text,                        -- filled when resource_kind = 'BLOOD'
  component       text,                        -- filled when resource_kind = 'BLOOD'
  units           int  not null default 1,     -- always 1 for a bed
  hold_type       text not null,               -- 'CITIZEN' (15 min) | 'PARAMEDIC' (20 min)
  severity        text,                        -- carried over from triage, for the nurse
  requester_name  text,
  requester_phone text not null,               -- our only identity check
  otp_code        text not null,               -- 4 digits, TEXT so '0042' keeps its zeros
  status          text not null default 'ACTIVE',
  created_at      timestamptz not null default now(),
  expires_at      timestamptz not null,        -- set by the database, never by Python
  resolved_at     timestamptz,                 -- when it left ACTIVE, whatever the reason

  constraint resource_kind_valid check (resource_kind in ('BED','BLOOD')),
  constraint hold_type_valid     check (hold_type in ('CITIZEN','PARAMEDIC')),
  constraint status_valid        check (status in ('ACTIVE','REDEEMED','EXPIRED','CANCELLED')),
  constraint severity_valid      check (severity is null or severity in ('RED','YELLOW','GREEN')),
  constraint otp_is_four_digits  check (otp_code ~ '^[0-9]{4}$'),
  constraint units_positive      check (units > 0),

  -- A bed hold must name a ward; a blood hold must name group + component.
  constraint bed_needs_ward
    check (resource_kind <> 'BED'   or ward_code is not null),
  constraint blood_needs_group
    check (resource_kind <> 'BLOOD' or (blood_group is not null and component is not null))
);

-- Fast lookup of live holds for a hospital (used by the availability views).
create index holds_live_lookup on holds (hospital_id, status, expires_at);
create index holds_ward_lookup on holds (hospital_id, ward_code, status);

-- No two ACTIVE holds at the same hospital may share a check-in code.
-- A PARTIAL unique index: the rule applies only to ACTIVE rows, so a code is
-- automatically reusable once the hold expires or is redeemed.
create unique index one_active_otp_per_hospital
  on holds (hospital_id, otp_code) where status = 'ACTIVE';

-- One phone number = at most one live reservation. Stops a single caller from
-- hoarding ICU beds across the city. Enforced by the database, not by a route.
create unique index one_active_hold_per_phone
  on holds (requester_phone) where status = 'ACTIVE';
```

```sql
-- ---------- 5. triage_logs  (evidence that the classifier works) -------------
create table triage_logs (
  id               uuid primary key default gen_random_uuid(),
  raw_text         text,
  input_mode       text not null default 'TEXT',   -- TEXT | VOICE | TAP
  language         text,                           -- 'en' | 'hi' | 'mixed'
  severity         text not null,
  recommended_ward text,
  engine           text not null,                  -- KEYWORD | LLM | KEYWORD+LLM
  score            int,
  matched_keywords text[],
  created_at       timestamptz not null default now(),

  constraint tl_severity_valid check (severity in ('RED','YELLOW','GREEN')),
  constraint tl_mode_valid     check (input_mode in ('TEXT','VOICE','TAP')),
  constraint tl_engine_valid   check (engine in ('KEYWORD','LLM','KEYWORD+LLM'))
);
```

### 3.1 The two availability views

These are the only thing the frontend ever reads capacity from.

```sql
-- ---------- 6. v_ward_availability ------------------------------------------
-- Availability is COUNTED, never stored. The `expires_at > now()` line is what
-- makes a reservation release itself with no code running anywhere.
create or replace view v_ward_availability as
select
  w.hospital_id,
  h.name             as hospital_name,
  h.short_name,
  h.city, h.lat, h.lng, h.phone,
  h.is_trauma_center, h.has_blood_bank, h.is_govt,
  w.ward_code,
  w.total_physical,
  w.total_staffed,
  w.occupied,
  coalesce(live.n, 0)                                            as held_now,
  greatest(w.total_staffed - w.occupied - coalesce(live.n, 0), 0) as available_now,
  (w.total_physical - w.total_staffed)                           as ghost_gap,
  w.updated_at
from ward_capacity w
join hospitals h on h.id = w.hospital_id
left join (
  select hospital_id, ward_code, count(*) as n
  from holds
  where resource_kind = 'BED'
    and status        = 'ACTIVE'
    and expires_at    > now()          -- ← the entire TTL mechanism, in one line
  group by hospital_id, ward_code
) live on live.hospital_id = w.hospital_id
      and live.ward_code   = w.ward_code;
```

```sql
-- ---------- 7. v_blood_availability -----------------------------------------
create or replace view v_blood_availability as
select
  b.hospital_id,
  h.name as hospital_name, h.lat, h.lng, h.has_blood_bank,
  b.blood_group,
  b.component,
  b.units_available,
  coalesce(live.n, 0)                                       as units_held_now,
  greatest(b.units_available - coalesce(live.n, 0), 0)       as units_free_now,
  b.is_trauma_reserve,
  b.requires_replacement_donor,
  b.updated_at
from blood_inventory b
join hospitals h on h.id = b.hospital_id
left join (
  select hospital_id, blood_group, component, sum(units) as n
  from holds
  where resource_kind = 'BLOOD'
    and status        = 'ACTIVE'
    and expires_at    > now()
  group by hospital_id, blood_group, component
) live on live.hospital_id = b.hospital_id
      and live.blood_group = b.blood_group
      and live.component   = b.component;
```

---

## 4. Row Level Security

```sql
alter table hospitals       enable row level security;
alter table ward_capacity   enable row level security;
alter table blood_inventory enable row level security;
alter table holds           enable row level security;
alter table triage_logs     enable row level security;

-- We deliberately create NO policies.
-- Effect: Supabase's public "anon" key can read and write NOTHING.
-- Flask connects with the service_role key, which bypasses RLS entirely.
-- Therefore the only path to this data is through our own API. If someone finds
-- our Supabase URL, they still get an empty result set.
```

This is worth 30 seconds in the viva: *"We locked the database down to zero public access
and put all logic behind our own API, so the browser never holds a database credential."*

---

## 5. The atomic hold — the most important half-page in this project

Everyone on the team should be able to explain the two commented lines marked **★**.

```sql
create or replace function create_live_hold(
  p_hospital_id     uuid,
  p_resource_kind   text,     -- 'BED' | 'BLOOD'
  p_ward_code       text,     -- null for blood
  p_blood_group     text,     -- null for bed
  p_component       text,     -- null for bed
  p_units           int,      -- 1 for a bed
  p_hold_type       text,     -- 'CITIZEN' | 'PARAMEDIC'
  p_severity        text,
  p_requester_name  text,
  p_requester_phone text
)
returns jsonb
language plpgsql
as $$
declare
  v_row_id     uuid;
  v_available  int;
  v_minutes    int;
  v_otp        text;
  v_hold_id    uuid;
  v_expires_at timestamptz;
  v_attempt    int := 0;
begin
  -- STEP 1 ── How long does this hold last?
  --           A paramedic is already moving, so they get 5 extra minutes.
  if p_hold_type = 'PARAMEDIC' then
    v_minutes := 20;
  else
    v_minutes := 15;
  end if;

  -- STEP 2 ── One live reservation per phone number.
  if exists (
    select 1 from holds
    where requester_phone = p_requester_phone
      and status = 'ACTIVE'
      and expires_at > now()
  ) then
    return jsonb_build_object(
      'ok', false, 'error_code', 'DUPLICATE_HOLD',
      'message', 'This phone number already has an active reservation.');
  end if;

  -- STEP 3 ── ★ LOCK THE RESOURCE ROW, THEN MEASURE.
  --           `for update` makes every other transaction that wants this same
  --           row WAIT here until we finish. Two ambulances therefore cannot
  --           both read "1 available" — the second one waits, then reads 0.
  if p_resource_kind = 'BED' then

    select id into v_row_id
      from ward_capacity
     where hospital_id = p_hospital_id
       and ward_code   = p_ward_code
     for update;                                        -- ★ the lock

    if v_row_id is null then
      return jsonb_build_object('ok', false, 'error_code', 'NO_SUCH_WARD',
        'message', 'That ward does not exist at this hospital.');
    end if;

    -- Read availability only AFTER the lock is ours, so the number is the truth.
    select available_now into v_available
      from v_ward_availability
     where hospital_id = p_hospital_id and ward_code = p_ward_code;

  else

    select id into v_row_id
      from blood_inventory
     where hospital_id = p_hospital_id
       and blood_group = p_blood_group
       and component   = p_component
     for update;                                        -- ★ the lock

    if v_row_id is null then
      return jsonb_build_object('ok', false, 'error_code', 'NO_SUCH_STOCK',
        'message', 'That blood component is not stocked at this hospital.');
    end if;

    select units_free_now into v_available
      from v_blood_availability
     where hospital_id = p_hospital_id
       and blood_group = p_blood_group
       and component   = p_component;
  end if;

  -- STEP 4 ── Is there enough?
  if v_available < p_units then
    return jsonb_build_object(
      'ok', false, 'error_code', 'NO_CAPACITY',
      'available', v_available,
      'message', 'That resource was just taken. Showing you the next hospital.');
  end if;

  -- STEP 5 ── Generate a 4-digit check-in code that no other ACTIVE hold at this
  --           hospital is using. Loop because random numbers can collide.
  loop
    v_attempt := v_attempt + 1;
    v_otp := lpad((floor(random() * 10000))::int::text, 4, '0');

    exit when not exists (
      select 1 from holds
       where hospital_id = p_hospital_id
         and otp_code    = v_otp
         and status      = 'ACTIVE'
    );

    if v_attempt >= 25 then
      return jsonb_build_object('ok', false, 'error_code', 'OTP_EXHAUSTED',
        'message', 'Could not allocate a check-in code. Please try again.');
    end if;
  end loop;

  -- STEP 6 ── The clock comes from the DATABASE, not from Python or the phone.
  v_expires_at := now() + (v_minutes || ' minutes')::interval;

  -- STEP 7 ── Write the hold. ★ If this insert fails for any reason, PostgreSQL
  --           rolls back the whole function including the lock, so the ward is
  --           never left in a half-reserved state. All-or-nothing.
  insert into holds (
    hospital_id, resource_kind, ward_code, blood_group, component,
    units, hold_type, severity, requester_name, requester_phone,
    otp_code, status, expires_at
  ) values (
    p_hospital_id, p_resource_kind,
    case when p_resource_kind = 'BED'   then p_ward_code   else null end,
    case when p_resource_kind = 'BLOOD' then p_blood_group else null end,
    case when p_resource_kind = 'BLOOD' then p_component   else null end,
    p_units, p_hold_type, p_severity, p_requester_name, p_requester_phone,
    v_otp, 'ACTIVE', v_expires_at
  )
  returning id into v_hold_id;

  return jsonb_build_object(
    'ok',            true,
    'hold_id',       v_hold_id,
    'otp_code',      v_otp,
    'expires_at',    v_expires_at,
    'seconds_left',  v_minutes * 60,
    'hold_minutes',  v_minutes,
    'left_after',    v_available - p_units
  );
end;
$$;
```

### Why this is the whole ballgame

`supabase-py` talks to the database over HTTP. Two HTTP calls — one to read, one to write —
have a gap between them, and **that gap is where the double-booking bug lives.** No amount
of careful Python closes it. Moving the decision into a single database function removes
the gap entirely, because a PostgreSQL function is one transaction.

Python's whole contribution shrinks to:

```python
response = supabase.rpc("create_live_hold", payload).execute()
```

Simple in Python. Provably correct in SQL. That is the trade we made on purpose.

---

## 6. The other four functions

### 6.1 `redeem_hold` — the nurse types the 4-digit code

```sql
create or replace function redeem_hold(p_hospital_id uuid, p_otp_code text)
returns jsonb
language plpgsql
as $$
declare
  v_hold     holds;
  v_staffed  int;
  v_occupied int;
begin
  -- Find the single ACTIVE hold with this code at this hospital, and lock it so
  -- two nurses tapping "Verify" at once cannot admit the same patient twice.
  select * into v_hold
    from holds
   where hospital_id = p_hospital_id
     and otp_code    = p_otp_code
     and status      = 'ACTIVE'
   for update;

  if v_hold.id is null then
    return jsonb_build_object('ok', false, 'error_code', 'INVALID_CODE',
      'message', 'No active reservation with that code at this hospital.');
  end if;

  -- Late arrival: the code was real but the clock ran out. Close it honestly.
  if v_hold.expires_at <= now() then
    update holds set status = 'EXPIRED', resolved_at = now() where id = v_hold.id;
    return jsonb_build_object('ok', false, 'error_code', 'EXPIRED',
      'message', 'That reservation expired. Create a fresh one at the desk.');
  end if;

  if v_hold.resource_kind = 'BED' then
    select total_staffed, occupied into v_staffed, v_occupied
      from ward_capacity
     where hospital_id = p_hospital_id and ward_code = v_hold.ward_code
     for update;

    -- Edge case worth knowing: staffing can fall between hold and arrival
    -- (a nurse goes off shift). We refuse silently corrupting the count and
    -- escalate to a human instead.
    if v_occupied + 1 > v_staffed then
      return jsonb_build_object('ok', false, 'error_code', 'CAPACITY_SHRANK',
        'message', 'This ward lost staffed capacity. Escalate to the duty officer.');
    end if;

    -- The patient is now physically in the bed: a held bed becomes an occupied bed.
    update ward_capacity
       set occupied = occupied + 1, updated_at = now()
     where hospital_id = p_hospital_id and ward_code = v_hold.ward_code;
  else
    -- Blood is consumed, not occupied.
    update blood_inventory
       set units_available = units_available - v_hold.units, updated_at = now()
     where hospital_id = p_hospital_id
       and blood_group  = v_hold.blood_group
       and component    = v_hold.component;
  end if;

  update holds set status = 'REDEEMED', resolved_at = now() where id = v_hold.id;

  return jsonb_build_object(
    'ok', true, 'hold_id', v_hold.id,
    'resource_kind', v_hold.resource_kind, 'ward_code', v_hold.ward_code,
    'severity', v_hold.severity, 'requester_name', v_hold.requester_name,
    'hold_type', v_hold.hold_type,
    'message', 'Patient admitted. Bed marked occupied.');
end;
$$;
```

### 6.2 `release_expired_holds` — what the TTL worker calls every 10 seconds

```sql
create or replace function release_expired_holds()
returns jsonb
language plpgsql
as $$
declare
  v_released int;
  v_active   int;
begin
  update holds
     set status = 'EXPIRED', resolved_at = now()
   where status     = 'ACTIVE'
     and expires_at <= now();

  get diagnostics v_released = row_count;   -- how many rows the UPDATE touched

  select count(*) into v_active from holds where status = 'ACTIVE';

  return jsonb_build_object('ok', true,
    'released', v_released, 'still_active', v_active, 'checked_at', now());
end;
$$;
```

Remember: this function is **housekeeping only**. `v_ward_availability` already ignores
expired holds. If this never ran, the numbers would still be right.

### 6.3 `cancel_hold` — the citizen taps "Cancel / Reroute"

```sql
create or replace function cancel_hold(p_hold_id uuid, p_requester_phone text)
returns jsonb
language plpgsql
as $$
declare v_n int;
begin
  -- The phone number acts as a cheap ownership proof, so a stranger who guesses
  -- a hold id cannot free somebody else's bed.
  update holds
     set status = 'CANCELLED', resolved_at = now()
   where id = p_hold_id
     and requester_phone = p_requester_phone
     and status = 'ACTIVE';

  get diagnostics v_n = row_count;

  if v_n = 0 then
    return jsonb_build_object('ok', false, 'error_code', 'NOT_CANCELLABLE',
      'message', 'That reservation is not active, or the phone number does not match.');
  end if;

  return jsonb_build_object('ok', true, 'message', 'Reservation released.');
end;
$$;
```

### 6.4 `update_quick_counter` — the one-tap `[+]` / `[-]` nurse button

```sql
create or replace function update_quick_counter(
  p_hospital_id uuid, p_ward_code text, p_delta int)
returns jsonb
language plpgsql
as $$
declare
  v_staffed   int;
  v_occupied  int;
  v_new_occ   int;
  v_available int;
  v_held      int;
begin
  -- Only ever one bed at a time. A fat-finger cannot move the count by 50.
  if p_delta <> 1 and p_delta <> -1 then
    return jsonb_build_object('ok', false, 'error_code', 'BAD_DELTA',
      'message', 'Delta must be exactly +1 or -1.');
  end if;

  select total_staffed, occupied into v_staffed, v_occupied
    from ward_capacity
   where hospital_id = p_hospital_id and ward_code = p_ward_code
   for update;

  if v_staffed is null then
    return jsonb_build_object('ok', false, 'error_code', 'NO_SUCH_WARD',
      'message', 'Ward not found for this hospital.');
  end if;

  v_new_occ := v_occupied + p_delta;

  if v_new_occ < 0 then
    return jsonb_build_object('ok', false, 'error_code', 'ALREADY_EMPTY',
      'message', 'Occupancy is already zero.');
  end if;

  if v_new_occ > v_staffed then
    return jsonb_build_object('ok', false, 'error_code', 'ABOVE_STAFFED',
      'message', 'Cannot exceed staffed beds. Raise staffed capacity first.');
  end if;

  update ward_capacity
     set occupied = v_new_occ, updated_at = now()
   where hospital_id = p_hospital_id and ward_code = p_ward_code;

  select available_now, held_now into v_available, v_held
    from v_ward_availability
   where hospital_id = p_hospital_id and ward_code = p_ward_code;

  return jsonb_build_object('ok', true, 'ward_code', p_ward_code,
    'occupied', v_new_occ, 'total_staffed', v_staffed,
    'available_now', v_available, 'held_now', v_held);
end;
$$;
```

### 6.5 `set_staffed_beds` — the anti-Ghost-Bed control (shift change)

```sql
create or replace function set_staffed_beds(
  p_hospital_id uuid, p_ward_code text, p_staffed int)
returns jsonb
language plpgsql
as $$
declare
  v_physical int;
  v_occupied int;
begin
  select total_physical, occupied into v_physical, v_occupied
    from ward_capacity
   where hospital_id = p_hospital_id and ward_code = p_ward_code
   for update;

  if v_physical is null then
    return jsonb_build_object('ok', false, 'error_code', 'NO_SUCH_WARD',
      'message', 'Ward not found.');
  end if;

  if p_staffed < 0 or p_staffed > v_physical then
    return jsonb_build_object('ok', false, 'error_code', 'OUT_OF_RANGE',
      'message', format('Staffed beds must be between 0 and %s.', v_physical));
  end if;

  -- You cannot un-staff a bed that has a patient in it.
  if p_staffed < v_occupied then
    return jsonb_build_object('ok', false, 'error_code', 'PATIENTS_PRESENT',
      'message', format('%s patients are currently admitted here.', v_occupied));
  end if;

  update ward_capacity
     set total_staffed = p_staffed, updated_at = now()
   where hospital_id = p_hospital_id and ward_code = p_ward_code;

  return jsonb_build_object('ok', true, 'total_staffed', p_staffed,
    'ghost_gap', v_physical - p_staffed);
end;
$$;
```

This is the function that makes the Ghost Bed story *demonstrable*: on stage, drop
`total_staffed` from 4 to 1 and watch every ambulance immediately stop being routed there,
while `total_physical` never changed. Existing portals cannot do that.

---

## 7. Seed data

`supabase_seed.sql` populates a realistic city. **City: Kolkata**, 12 facilities — which matches
the `12 Hospitals Connected` badge on the citizen screen.

### The twelve facilities

Eight government and four private, spread north to south so the distance sort has something real
to sort. Coordinates below are approximate to about 200 m and **must be checked against a map
before the seed is finalised** — a pin visibly in the wrong neighbourhood in front of a Kolkata
jury is an avoidable embarrassment (risk R9 in [15 §2](15-DECISIONS-AND-RISKS.md#2-risk-register)).

| # | Facility | Area | Type | Lat | Lon | Trauma | Blood bank |
|---|---|---|---|---|---|---|---|
| 1 | S.S.K.M. Hospital (IPGMER) | Bhowanipore | Govt · tertiary | 22.5390 | 88.3430 | ✔ | ✔ |
| 2 | Calcutta Medical College & Hospital | College Street | Govt · tertiary | 22.5745 | 88.3639 | ✔ | ✔ |
| 3 | N.R.S. Medical College & Hospital | Sealdah | Govt · tertiary | 22.5648 | 88.3717 | ✔ | ✔ |
| 4 | R.G. Kar Medical College & Hospital | Shyambazar | Govt · tertiary | 22.6182 | 88.3792 | ✔ | ✔ |
| 5 | Calcutta National Medical College | Park Circus | Govt | 22.5395 | 88.3712 | — | ✔ |
| 6 | Dr. B.C. Roy Institute of Paediatric Sciences | Phoolbagan | Govt · paediatric | 22.5762 | 88.3983 | — | — |
| 7 | Chittaranjan Seva Sadan | Bhowanipore | Govt · maternity & child | 22.5262 | 88.3452 | — | — |
| 8 | M.R. Bangur Hospital | Tollygunge | Govt | 22.4948 | 88.3452 | — | ✔ |
| 9 | Apollo Multispeciality Hospitals | Canal Circular Rd | Private | 22.5713 | 88.4003 | ✔ | ✔ |
| 10 | R.N. Tagore Institute of Cardiac Sciences | Mukundapur | Private · cardiac | 22.4893 | 88.4024 | — | — |
| 11 | Medica Superspecialty Hospital | Mukundapur | Private | 22.4930 | 88.3999 | ✔ | ✔ |
| 12 | AMRI Hospital | Dhakuria | Private | 22.5062 | 88.3665 | — | — |

Five trauma-capable, seven with a blood bank. The specialities matter for routing: #6 and #7
should have the strongest `pediatric_icu` staffing, and #10 the strongest `cardiac_icu`, so the
triage engine's ward recommendation visibly lands somewhere sensible.

City centre for the distance calculation and the map mock: **22.5726 N, 88.3639 E** (Esplanade /
BBD Bagh). Geolocation is used when the citizen grants it; this is the fallback.

### The numbers

- **Wards:** 4 rows per hospital = 48 rows. `total_physical` between 4 and 22; `total_staffed`
  set 0–4 lower to create a visible `ghost_gap`; `occupied` set so that roughly one third of
  wards read 0 available. A full city is far more convincing than an empty one.
- **Blood:** the 7 facilities with `has_blood_bank = true` get 8 groups × 3 components = 24 rows
  each. `O-` PRBC is deliberately scarce (0–4 units), because O-negative shortage is the
  real-world crisis and it makes the demo bite.

> **Honesty requirement.** These hospital names and locations are public information, but every
> capacity number is invented. The UI must therefore carry a permanent
> `SIMULATED DATA · DEMONSTRATION ONLY` badge, and the team must say so unprompted in the
> pitch. Presenting fabricated bed counts as live government data would be the fastest way
> to lose credibility with a jury that includes medical professionals.

---

## 8. How to verify the schema in 60 seconds

Paste into the Supabase SQL editor after running the schema and seed:

```sql
-- 1. Every hospital has exactly 4 wards?
select count(*) = 48 as wards_ok from ward_capacity;

-- 2. Availability view returns sane numbers?
select hospital_name, ward_code, total_physical, total_staffed,
       occupied, held_now, available_now, ghost_gap
  from v_ward_availability
 order by hospital_name, ward_code
 limit 12;

-- 3. Atomic hold works? (replace the uuid with a real one from step 2)
select create_live_hold(
  '00000000-0000-0000-0000-000000000000', 'BED', 'adult_icu',
  null, null, 1, 'CITIZEN', 'RED', 'Test Patient', '9999900001');

-- 4. Same phone again must be refused with DUPLICATE_HOLD
select create_live_hold(
  '00000000-0000-0000-0000-000000000000', 'BED', 'adult_icu',
  null, null, 1, 'CITIZEN', 'RED', 'Test Patient', '9999900001');

-- 5. The hold is visible and counted
select otp_code, status, expires_at from holds order by created_at desc limit 1;
select ward_code, held_now, available_now from v_ward_availability
 where hospital_id = '00000000-0000-0000-0000-000000000000';

-- 6. Housekeeping runs clean
select release_expired_holds();
```

If step 4 returns `DUPLICATE_HOLD` and step 5 shows `held_now = 1`, the database layer is
finished and Member 2 can start writing `database.py`.
