# Viva Preparation Guide: TTL Worker Developer

**Role:** "I built the background worker that automatically frees expired bed holds"

**Elevator Pitch:**
I engineered the background TTL (Time-To-Live) worker that runs continuously alongside our server. It automatically monitors the database and releases expired bed reservations in real-time, ensuring that critical hospital beds are never locked up by no-shows.

## Code Walkthrough: `ttl_worker.py`
The `ttl_worker.py` file maintains database efficiency.
- **`_worker_loop`**: This is an infinite `while True` loop that sleeps for 10 seconds, wakes up, and calls `db_module.release_expired_holds()`. It logs the number of stale holds released and handles any unexpected exceptions.
- **`start_ttl_worker`**: This function is called when the Flask app starts. It initializes a Python `threading.Thread` targeting the worker loop and explicitly sets it as a daemon thread before starting it.

## Technical Explanations
**Daemon Threads vs Regular Threads:**
A daemon thread runs in the background and is tied to the lifecycle of the main program. If the main Flask server shuts down or crashes, the daemon thread is automatically killed. A regular thread would block the program from exiting, causing hanging processes.

**Why a 10-Second Interval?**
We chose a 10-second interval because it strikes the perfect balance. It ensures expired holds are returned to the available bed pool almost instantly during fast-paced emergencies, while being long enough to prevent overloading the Supabase database with excessive queries.

## Tough Judge Questions & Winning Answers

**1. "What is a daemon thread and why did you use one?"**
*Answer:* A daemon thread is a background thread that automatically dies when the main program exits. We used it so our TTL worker could run continuously alongside the Flask server without preventing the server from gracefully shutting down when we restart it.

**2. "Why 10 seconds instead of 1 second or 1 minute?"**
*Answer:* One second would spam the database with unnecessary API calls and cause rate-limiting, while one minute is too long to keep a critical ICU bed locked if a hold has expired. Ten seconds provides near real-time bed availability with minimal server overhead.

**3. "What happens if the worker crashes?"**
*Answer:* The worker loop is wrapped in a robust `try-except` block. If a database timeout or error occurs, the exception is caught and logged, and the loop simply sleeps and tries again in the next cycle, ensuring the worker never permanently crashes.

**4. "How does this compare to a cron job or scheduled task?"**
*Answer:* A cron job typically runs every minute at best, which isn't fast enough for emergency logistics. Our threaded worker runs every 10 seconds, providing much tighter real-time synchronization between expired holds and bed availability on the frontend.

**5. "Could you use Supabase scheduled functions instead?"**
*Answer:* Yes, Supabase supports pg_cron for scheduled functions, which would be ideal for production. However, for this hackathon, building it in Python gave us immediate control, easier debugging, and allowed us to log the worker's real-time actions directly in our Flask console.
