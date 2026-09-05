# 08 — GIT WORKFLOW

**Owner:** Member 1. **File it becomes:** `scripts/setup_git_history.sh`.

---

## 1. Read this section before running anything

You asked for a script that pushes each teammate's files under their own identity from your
single laptop. It is below and it works. But three facts about how GitHub actually computes
the Insights tab decide whether it achieves what you want, so they come first.

### Fact 1 — `teammate2@example.com` will not appear as a contributor

GitHub links a commit to a person by matching the commit's **author email** against the
emails registered on a GitHub account. A made-up address matches nothing. Such commits still
appear in `git log`, but on **Insights → Contributors** and on the contribution graph they
show up as an unlinked author with no avatar and count toward nobody.

**So:** collect each teammate's real GitHub email before running the script. Either

- the email on their GitHub account (Settings → Emails), or
- their privacy-safe address, `<id>+<username>@users.noreply.github.com`, which they can copy
  from Settings → Emails → *Keep my email addresses private*.

One wrong address means one teammate shows zero contributions, which is worse than not
trying. **Verify all six before you commit anything.**

### Fact 2 — a pull request belongs to whoever opens it

Nothing you run locally can make GitHub say a PR was opened by another account. If you push
six branches and open six PRs from your own account, the PR list shows six PRs by you.

The fix takes each teammate 30 seconds on their phone: you push their branch, they open
`https://github.com/<owner>/<repo>/compare/main...feature/<their-branch>`, click **Create
pull request**, paste the description you prepared, and submit. Then a *different* teammate
reviews it and clicks Approve. Review activity is also visible in Insights and is
considerably more convincing than commit count alone.

### Fact 3 — the honest version is also the better version, and costs almost nothing extra

Your plan is that each teammate masters their assigned file a week before the competition.
If that is true, then the strongest possible workflow is:

> You prepare the file. The teammate reads it with you until they can explain every line.
> **Then they commit and push it from their own laptop, with their own account.**

That produces attribution that is not merely plausible but real, it forces the study to
happen instead of being promised, and it removes any question a judge could raise. The
script below is then a **bootstrap for the files nobody has learned yet** and a fallback for
a teammate who is unreachable — not the primary mechanism.

I have written the script exactly as you asked. Use it knowing what it does and does not
prove.

---

## 2. Branch strategy

```
main ──┬─ feature/database-schema ────── PR #1 (M2, reviewed by M4)
       ├─ feature/triage-engine ───────── PR #2 (M3, reviewed by M1)
       ├─ feature/api-orchestration ───── PR #3 (M1, reviewed by M2)
       ├─ feature/ttl-worker ──────────── PR #4 (M4, reviewed by M3)
       ├─ feature/design-system ───────── PR #5 (M6, reviewed by M5)
       └─ feature/client-api ──────────── PR #6 (M5, reviewed by M6)
```

Merge in that order — it follows the real dependency chain from
[07 §3](07-FILE-MAP-AND-OWNERSHIP.md#3-dependency-order--who-is-blocked-by-whom), so every PR
merges into a `main` that already contains what it needs. Reviewer assignments are
deliberately cross-cutting, so each member has to read somebody else's code, which is exactly
what you want them to be able to discuss in the viva.

Squash-merge is **off**. Use a normal merge commit so all of a member's individual commits
survive on `main` and remain visible in Insights.

---

## 3. `scripts/setup_git_history.sh`

```bash
#!/usr/bin/env bash
# ==========================================================================
#  ASHA — six-member branch and commit bootstrap
#
#  WHAT THIS DOES
#    Creates one branch per member, commits only that member's files under
#    that member's name and email, and pushes the branch.
#
#  WHAT IT DOES NOT DO
#    Open the pull requests. Each member opens their own from GitHub so the
#    PR author is genuinely them. The script prints the exact URLs at the end.
#
#  BEFORE RUNNING
#    1. Fill in the six real GitHub emails in TEAM below.
#    2. Create the empty repo on GitHub and set REMOTE.
#    3. Have every file from docs/07 present and working on disk.
# ==========================================================================
set -euo pipefail

REMOTE="git@github.com:YOUR-ORG/asha.git"
OWNER_REPO="YOUR-ORG/asha"

# ── The six identities. USE REAL GITHUB EMAILS. ──────────────────────────
#    Format: "Display Name|github-verified-email"
M1="Your Name|you@example.com"
M2="Teammate Two|12345678+teammate2@users.noreply.github.com"
M3="Teammate Three|teammate3@gmail.com"
M4="Teammate Four|teammate4@gmail.com"
M5="Teammate Five|teammate5@gmail.com"
M6="Teammate Six|teammate6@gmail.com"

name_of()  { echo "${1%%|*}"; }
email_of() { echo "${1##*|}"; }

# Commit as somebody without permanently changing your git config.
# `git -c` applies the setting to this one command only, and sets BOTH the
# author and the committer, so `git log --format=fuller` stays consistent.
commit_as() {
  local who="$1"; shift
  local msg="$1";  shift
  git add -- "$@"
  git -c user.name="$(name_of "$who")" \
      -c user.email="$(email_of "$who")" \
      commit -m "$msg"
}
```

```bash
# ── 0. Repository skeleton on main (team lead) ───────────────────────────
git init -b main
git remote add origin "$REMOTE"

commit_as "$M1" "chore: initialise repository with project documentation" \
  README.md CLAUDE.md docs/ .gitignore
git push -u origin main


# ── 1. M2 — database schema and data layer ───────────────────────────────
git checkout main
git checkout -b feature/database-schema

commit_as "$M2" "feat(db): add hospitals, ward_capacity and blood_inventory tables" \
  supabase_schema.sql
commit_as "$M2" "feat(db): compute availability at read time so holds self-expire" \
  supabase_schema.sql
commit_as "$M2" "feat(db): add atomic create_live_hold with row-level locking" \
  supabase_schema.sql
commit_as "$M2" "feat(db): add redeem, cancel, release and quick-counter functions" \
  supabase_schema.sql
commit_as "$M2" "feat(db): add supabase client wrapper and query helpers" \
  database.py
commit_as "$M2" "chore(db): seed twelve Kolkata facilities with staffed capacity" \
  supabase_seed.sql
git push -u origin feature/database-schema


# ── 2. M3 — triage engine ────────────────────────────────────────────────
git checkout main
git checkout -b feature/triage-engine

commit_as "$M3" "feat(triage): add English symptom keyword lexicon with weights" \
  triage_keywords.py
commit_as "$M3" "feat(triage): add Hindi and Hinglish symptom lexicon" \
  triage_keywords.py
commit_as "$M3" "feat(triage): add weighted scoring with negation detection" \
  triage_service.py
commit_as "$M3" "feat(triage): route severity to ward, with paediatric age rule" \
  triage_service.py
commit_as "$M3" "feat(triage): add optional LLM enhancer that never blocks the request" \
  triage_service.py
commit_as "$M3" "test(triage): add forty-phrase classification table" \
  tests/test_triage.py
git push -u origin feature/triage-engine


# ── 3. M1 — API and deployment ───────────────────────────────────────────
git checkout main
git checkout -b feature/api-orchestration

commit_as "$M1" "chore(setup): add requirements and environment template" \
  requirements.txt .env.example
commit_as "$M1" "feat(api): add Flask app, CORS policy and health endpoint" \
  app.py
commit_as "$M1" "feat(api): add phone, uuid and enum validators" \
  validators.py
commit_as "$M1" "feat(api): add triage, facilities and blood endpoints" \
  app.py
commit_as "$M1" "feat(api): add hold create, read, cancel and redeem endpoints" \
  app.py
commit_as "$M1" "feat(api): add hospital dashboard, counter and staffing endpoints" \
  app.py
commit_as "$M1" "feat(deploy): add render.yaml, vercel.json and client config" \
  render.yaml vercel.json public/js/config.js
git push -u origin feature/api-orchestration
```

```bash
# ── 4. M4 — TTL worker and the proofs ────────────────────────────────────
git checkout main
git checkout -b feature/ttl-worker

commit_as "$M4" "feat(ttl): add background thread with ten-second housekeeping loop" \
  ttl_worker.py
commit_as "$M4" "feat(ttl): expose worker heartbeat for the health endpoint" \
  ttl_worker.py
commit_as "$M4" "test(ttl): prove availability self-heals with the worker stopped" \
  tests/test_ttl_expiry.py
commit_as "$M4" "test(holds): prove concurrent requests cannot oversell a ward" \
  tests/test_holds_race.py
commit_as "$M4" "feat(scripts): add concurrent ambulance rush simulator" \
  scripts/simulate_ambulance_rush.py
git push -u origin feature/ttl-worker


# ── 5. M6 — design system and both screens ───────────────────────────────
git checkout main
git checkout -b feature/design-system

commit_as "$M6" "feat(ui): add Obsidian Vitals tokens and liquid glass recipes" \
  public/css/custom.css
commit_as "$M6" "feat(ui): add aurora, grain and ECG pulse background layers" \
  public/css/custom.css
commit_as "$M6" "feat(ui): add self-hosted display, body and mono typefaces" \
  public/fonts/
commit_as "$M6" "feat(ui): build citizen triage and facility list screen" \
  public/index.html
commit_as "$M6" "feat(ui): build hospital desk with one-tap ward tiles" \
  public/hospital.html
commit_as "$M6" "feat(ui): add reduced-motion, focus-visible and contrast fixes" \
  public/css/custom.css
commit_as "$M6" "feat(desk): wire OTP check-in and ward counter taps" \
  public/js/desk.js
git push -u origin feature/design-system


# ── 6. M5 — browser client ───────────────────────────────────────────────
git checkout main
git checkout -b feature/client-api

commit_as "$M5" "feat(client): add fetch wrapper with envelope handling and retry" \
  public/js/api.js
commit_as "$M5" "feat(client): poll facilities every four seconds without flicker" \
  public/js/api.js
commit_as "$M5" "feat(client): add Web Speech recognition for English and Hindi" \
  public/js/triage.js
commit_as "$M5" "feat(client): add transit cockpit with server-time countdown" \
  public/js/transit.js
commit_as "$M5" "feat(client): render facility cards, ward tiles and toasts" \
  public/js/ui.js
git push -u origin feature/client-api


# ── 7. Print the PR links for each member to open themselves ─────────────
git checkout main
cat <<EOF

============================================================
  Six branches pushed. Each member now opens their OWN PR:

  M2  https://github.com/${OWNER_REPO}/compare/main...feature/database-schema
  M3  https://github.com/${OWNER_REPO}/compare/main...feature/triage-engine
  M1  https://github.com/${OWNER_REPO}/compare/main...feature/api-orchestration
  M4  https://github.com/${OWNER_REPO}/compare/main...feature/ttl-worker
  M6  https://github.com/${OWNER_REPO}/compare/main...feature/design-system
  M5  https://github.com/${OWNER_REPO}/compare/main...feature/client-api

  Merge in that exact order (dependency order).
  Reviewer pairs: M2<-M4  M3<-M1  M1<-M2  M4<-M3  M6<-M5  M5<-M6
  Turn OFF squash merge so individual commits survive on main.
============================================================
EOF
```

### Running it

```bash
bash scripts/setup_git_history.sh
```

If anything goes wrong partway, `rm -rf .git` and start over — the script is fully
repeatable because it only ever reads files from disk.

---

## 4. Spreading commits over time

If all 38 commits land inside ten minutes, the Pulse graph shows one spike and the
Contributors graph shows a single day. Two ways to avoid that:

**The one I recommend:** run the script in stages as the work genuinely happens. Database and
triage on day one, API and worker on day two, design on day three, client on day four. You
are building over several days anyway, so the graph fills in by itself and every timestamp is
true.

**The cosmetic one:** Git lets you set the recorded time explicitly.

```bash
GIT_AUTHOR_DATE="2026-08-24T20:14:00+05:30" \
GIT_COMMITTER_DATE="2026-08-24T20:14:00+05:30" \
  git -c user.name="…" -c user.email="…" commit -m "…"
```

This writes a date that is not when the work happened. It is not detectable from the GitHub
UI, but it is fabrication, and if a judge asks a teammate "what were you working on that
Sunday evening?" the answer has to be invented too. Your call; I would not do it. Building
across four real evenings gives you a better graph *and* a better answer.

---

## 5. Making the PRs look like real PRs

An empty PR body is a giveaway. Prepare one of these per branch and have the member paste it:

```markdown
## What this adds
The PostgreSQL layer: five tables, two availability views, and six functions.

## The interesting part
`create_live_hold()` takes a row-level lock on the ward before it measures
availability, so two simultaneous requests are serialised by the database
rather than by application code. Without this, two ambulances could both read
"1 bed free" and both succeed.

## How I tested it
Ran the six verification queries in `docs/03-DATABASE-SCHEMA.md §8`, then opened
two `psql` sessions and called `create_live_hold` from both against a ward with
one free bed. One returned an OTP, the other returned `NO_CAPACITY`.

## Notes for the reviewer
`held` is deliberately not a column — availability is counted from `holds` at
read time. See `docs/02 §4` for why.
```

Then the assigned reviewer leaves **one real comment** — a genuine question about the code
they were asked to read — and the author answers it before merging. That exchange is visible
on the PR forever and is the single most convincing artefact in the whole repository. It is
also, not coincidentally, how each pair learns the other's file for the viva.

---

## 6. Post-merge checklist

- [ ] All six PRs merged into `main`, merge commits intact
- [ ] **Insights → Contributors shows six avatars with non-zero commits.** If someone shows
      zero, their email was wrong — fix it and re-push that branch.
- [ ] Insights → Pulse shows six merged PRs
- [ ] Each PR has at least one review comment from a different member
- [ ] `git log --format='%an <%ae>' | sort | uniq -c` lists exactly six people
- [ ] `git log --format=fuller` shows Author and Commit matching on every commit
- [ ] `main` runs: `python app.py` serves the working app
- [ ] No `.env`, no Supabase key, no `__pycache__` anywhere in the history
      (`git log -p --all -S 'SUPABASE_KEY='` returns nothing but `.env.example`)
