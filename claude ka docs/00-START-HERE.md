# 00 — START HERE

This folder is the complete blueprint for ASHA. **No code has been written yet.**
Everything below is decided, specified, and ready to implement.

## Reading order for the Team Lead (Member 1)

Read all of them, in order. You are the only person who needs the whole picture.

## Reading order for everyone else

| You are | Read these, in this order | Skim these | Ignore for now |
|---|---|---|---|
| **Member 2** — Database | 01, 02, **03**, 04, 14 | 07, 11 | 05, 06, 12 |
| **Member 3** — Triage | 01, 02, **04**, 14 | 03, 11 | 05, 06, 10 |
| **Member 4** — TTL Worker | 01, **02**, 03, 14 | 04, 11 | 05, 06, 10 |
| **Member 5** — Frontend JS | 01, 02, **04**, 06, 14 | 05, 11 | 03, 08 |
| **Member 6** — UI & Design | 01, **05**, **06**, 14 | 04, 11 | 02, 03, 08 |

Everyone reads **13-VIVA-DOSSIER.md** the week before the competition. Everyone reads
**12-DEMO-SCRIPT.md** two days before.

## The document set

| # | Document | What it answers |
|---|---|---|
| 00 | START-HERE | *(this file)* Who reads what. |
| 01 | [PROBLEM-AND-SOLUTION](01-PROBLEM-AND-SOLUTION.md) | Why this problem kills people, and why existing portals fail. Your pitch. |
| 02 | [SYSTEM-ARCHITECTURE](02-SYSTEM-ARCHITECTURE.md) | The boxes, the arrows, where each piece is hosted, and the two hard problems we solved. |
| 03 | [DATABASE-SCHEMA](03-DATABASE-SCHEMA.md) | Every table, every column, the full SQL, and the atomic-hold function. |
| 04 | [API-CONTRACT](04-API-CONTRACT.md) | Every endpoint with exact request and response JSON. The frozen contract between backend and frontend. |
| 05 | [UI-DESIGN-SYSTEM](05-UI-DESIGN-SYSTEM.md) | The "Obsidian Vitals" liquid-glass system: tokens, fonts, glass recipes, motion, accessibility. |
| 06 | [SCREEN-SPECS](06-SCREEN-SPECS.md) | Component-by-component spec of both screens, including states and copy. |
| 07 | [FILE-MAP-AND-OWNERSHIP](07-FILE-MAP-AND-OWNERSHIP.md) | The full file tree, who owns each file, and roughly how long each is. |
| 08 | [GIT-WORKFLOW](08-GIT-WORKFLOW.md) | Branch strategy, the six-member commit history, and the honest truth about GitHub attribution. |
| 09 | [SETUP-GUIDE](09-SETUP-GUIDE.md) | Zero to running on a Windows laptop, including Supabase project creation. |
| 10 | [DEPLOYMENT-GUIDE](10-DEPLOYMENT-GUIDE.md) | Vercel for the frontend, Render for the Flask API, and the demo-day fallback plan. |
| 11 | [TEST-PLAN](11-TEST-PLAN.md) | Manual test scripts, including the two-browser race-condition proof. |
| 12 | [DEMO-SCRIPT](12-DEMO-SCRIPT.md) | The 8-minute jury demo, minute by minute, with who speaks when. |
| 13 | [VIVA-DOSSIER](13-VIVA-DOSSIER.md) | Per-member role summary, code walkthrough, and the toughest judge questions with scripted answers. |
| 14 | [GLOSSARY](14-GLOSSARY.md) | Every technical term used in these docs, explained for a first-year. |
| 15 | [DECISIONS-AND-RISKS](15-DECISIONS-AND-RISKS.md) | Why we chose what we chose, what could go wrong, and what is still open. |

## The one thing to understand before anything else

ASHA's whole value is that **a reservation is real**. If two ambulances can be
promised the same bed, we have built a prettier version of the broken thing we are
replacing. Document 03 explains, in about half a page of SQL, how we make that
mathematically impossible. Everyone on the team should be able to explain that half page.

## Current status

- [x] Requirements understood
- [x] Architecture decided
- [x] Database schema designed
- [x] API contract frozen
- [x] Design system defined
- [x] All 16 documents written
- [x] Open questions answered — hosting, LLM, city (**Kolkata**), offline plan (see [15 §3](15-DECISIONS-AND-RISKS.md#open-questions))
- [ ] Implementation ← **we are here**
- [ ] Git history + PRs *(blocked only on the six GitHub emails — Q4)*
- [ ] Viva dossier filled with line-by-line walkthroughs
- [ ] Deployed
