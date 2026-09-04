# Viva Preparation Guide: Database Engineer

**Role:** "I designed the database and built the atomic bed reservation system"

**Elevator Pitch:**
I engineered the database architecture using Supabase and implemented a bulletproof atomic reservation system. My code dynamically calculates bed availability and uses OTP verification to ensure that beds are securely held and managed without double-booking during critical emergencies.

## Code Walkthrough: `database.py`
The `database.py` file manages all interactions with our Supabase PostgreSQL database. 
- **`get_all_hospitals`**: Dynamically calculates available beds by subtracting occupied and held beds from the total capacity.
- **`create_live_hold`**: Verifies if a bed is available, generates a 4-digit OTP, atomically inserts a hold record with an expiration time, and increments the hospital's held counter.
- **`redeem_hold`**: Verifies the OTP, updates the hold status to 'REDEEMED', and atomically moves the bed from 'held' to 'occupied'.
- **`release_expired_holds`**: Scans for active holds past their `expires_at` timestamp, updates them to 'EXPIRED', and decrements the held counter.

## Technical Explanations
**Atomic Hold Operation:**
The atomic hold operation ensures data integrity by verifying availability right before allocating the bed. It inserts a new active hold record and increments the `held` counter in a structured way, guaranteeing that a bed is fully reserved before returning the OTP to the user.

**Race Condition Prevention:**
By calculating availability dynamically and updating counters relative to their current state (e.g., adding +1 to the existing value), we prevent race conditions. This ensures that if two users request a bed simultaneously, the database accurately reflects the available inventory.

**TTL Expiry Mechanism:**
Holds have a strict time-to-live (15 or 20 minutes). A background worker repeatedly calls the `release_expired_holds` function, which queries for holds where the current time is past `expires_at`. It then automatically frees up the bed by decrementing the held counter, ensuring resources aren't locked up by no-shows.

## Tough Judge Questions & Winning Answers

**1. "What is a race condition and how does your system prevent it?"**
*Answer:* A race condition happens when two users try to book the same last bed at the exact same millisecond. We prevent it by dynamically checking availability and atomically updating the hospital's held counter, ensuring the database acts as the single source of truth and prevents double-booking.

**2. "Why Supabase and not SQLite or MongoDB?"**
*Answer:* Supabase provides a powerful, cloud-hosted PostgreSQL database with real-time capabilities and a great Python SDK. We chose it over SQLite for true concurrency support, and over MongoDB because our hospital inventory and reservation data is highly relational and benefits from strict SQL schemas.

**3. "Explain the atomic hold operation step by step"**
*Answer:* First, it queries the hospital to confirm available beds. Second, it generates a random 4-digit OTP and calculates an expiration timestamp. Finally, it inserts the new hold record into the database and immediately increments the hospital's held counter to lock the bed for that user.

**4. "What happens if the OTP is entered after the hold expires?"**
*Answer:* The background worker will have already marked the hold as 'EXPIRED' and returned the bed to the available pool. If a nurse tries to enter the OTP, the `redeem_hold` function will fail to find an 'ACTIVE' hold and will return an error, preventing the patient from taking a bed they lost.

**5. "How does the 1-tap nurse counter work technically?"**
*Answer:* The `update_quick_counter` function takes a hospital ID, a ward, and a delta value (like +1 or -1). It queries the current occupied count, adds the delta, ensures the value doesn't drop below zero or exceed total capacity, and directly updates the database record.
