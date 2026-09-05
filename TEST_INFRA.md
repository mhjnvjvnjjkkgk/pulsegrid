# PulseGrid E2E Test Infrastructure & Methodology Document

## Overview
This document outlines the test architecture, test tier categorization, methodology, and verification framework for the PulseGrid Emergency Web App test suite.

---

## 1. Test Architecture & Framework
- **Test Framework**: `pytest` (Python 3.12, Flask test client / WSGI test harness).
- **Execution Target**: `d:\HACKATHON\venv\Scripts\python.exe -m pytest d:\HACKATHON\tests`
- **Isolation**: Each test operates on controlled application context and mock database state to ensure reproducibility, thread-safety, and zero external network dependency (CODE_ONLY compliant).

---

## 2. Test Tier Taxonomy (Tiers 1 – 4)

### Tier 1: Feature Coverage & API Contracts
Validates individual API endpoints against exact schema contracts, status codes, and deterministic outputs.
- **Triage & Search API (`test_triage_api.py`)**:
  - Symptom keyword parsing (RED, YELLOW, GREEN severity levels).
  - Hinglish & Benglish emergency expression classification.
  - Blood search term parsing ("O negative", "A+", "B positive", "AB-", etc.).
  - Unified search endpoint returns category, severity, recommended hospitals, and blood matches.
- **Holds & Lock Engine API (`test_holds_api.py`)**:
  - Soft-lock creation: bed decrement (e.g. 30 -> 29), 15-minute countdown calculation, 4-digit OTP generation.
  - Hard-lock redemption: OTP verification at hospital, state transition from `ACTIVE` to `REDEEMED`, bed count remains claimed (29).
  - Manual cancellation: state transition to `CANCELLED`, bed restored to available pool (29 -> 30).
- **GPS Tracking & Vector Engine API (`test_gps_vector_api.py`)**:
  - GPS position updates (`user_lat`, `user_lng`).
  - Directional vector calculation: `TOWARD` (moving closer), `STATIONARY` (idle), `AWAY` (moving further).
  - Off-track wrong direction counter incrementing.
  - Auto-cancellation trigger when wrong direction counter reaches 3, releasing bed back to pool.

### Tier 2: Boundary & Corner Cases
Tests system behavior under edge conditions, malformed inputs, and resource limits.
- **Input Validation**:
  - Missing required fields (e.g., missing `hospital_id`, missing `otp_code`, missing `user_lat`/`user_lng`).
  - Invalid OTP codes and attempt with wrong hospital ID.
  - Empty or whitespace search queries.
- **Capacity Exhaustion**:
  - Bed reservation request when ward available capacity is 0 (returns error, no bed count underflow).
  - Redeeming already redeemed or cancelled holds.

### Tier 3: Cross-Feature Combinations & State Transitions
Validates stateful transitions across multi-step API sequences.
- **State Machine Integrity**:
  - `ACTIVE` -> `REDEEMED` (Hard lock success path).
  - `ACTIVE` -> `CANCELLED` (User manual release).
  - `ACTIVE` -> `CANCELLED` via GPS Vector Auto-Cancel (3x wrong direction).
- **Concurrency & Re-entrancy**:
  - Concurrent holds on limited bed stock.
  - Verification that bed count delta math is invariant across state transitions.

### Tier 4: Real-World Application Scenarios (E2E User Flows)
Simulates complete real-world emergency workflows end-to-end (`test_e2e_scenarios.py`).
- **Scenario A (Cardiac Patient Critical Path)**:
  1. Patient searches "chhati me bahut dard ho raha hai" via unified search.
  2. System triages to `RED` / `cardiac_icu` and returns available cardiac hospitals.
  3. Patient requests 15m soft lock -> bed count decrements (30 -> 29), 4-digit OTP generated.
  4. Patient streams GPS position moving `TOWARD` hospital -> dynamic ETA calculated, status `ACTIVE`.
  5. Patient arrives at hospital, nurse verifies OTP -> state transitions to `REDEEMED`, bed stays claimed at 29.
- **Scenario B (Wrong Direction Auto-Cancel Recovery Flow)**:
  1. Patient locks bed for emergency -> initial bed count decrements (30 -> 29).
  2. Patient moves away from target hospital 3 consecutive times -> wrong direction count reaches 3.
  3. System triggers auto-cancellation -> hold status set to `CANCELLED`, bed restored to 30.
  4. Patient performs new search and re-books alternate hospital.
- **Scenario C (Blood Emergency Search & Paramedic Lock Flow)**:
  1. Paramedic searches "O negative blood needed".
  2. System identifies blood group `O-`, lists hospitals with matching stock.
  3. Paramedic creates soft-lock reservation for emergency blood.

---

## 3. Verification Method
To independently execute and verify the test suite:
```bash
d:\HACKATHON\venv\Scripts\python.exe -m pytest d:\HACKATHON\tests -v
```
All tests must report `PASSED` with zero failures or errors.
