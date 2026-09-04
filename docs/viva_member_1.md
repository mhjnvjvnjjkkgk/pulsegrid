# Viva Preparation Guide: Team Lead (Flask Server)

**Role:** "I built the Flask API server that connects the frontend to the database"

**Elevator Pitch:**
I built the robust backend API for PulseGrid using Flask. It serves as the main communication hub, handling requests from the frontend, delegating AI triage, and securely interacting with our Supabase database to manage real-time bed holds.

## Code Walkthrough: `app.py`
The `app.py` file initializes the Flask application and configures CORS to allow frontend communication. It starts by connecting to the Supabase database and launching a background thread for the TTL worker.
- **`/api/triage`**: Accepts symptom text and calls the triage service to classify the severity.
- **`/api/facilities`**: Fetches hospitals, optionally filtering them by specialty and ward.
- **`/api/holds/create` & `/api/holds/redeem`**: Handles the creation of new bed holds and redeems active holds using a generated OTP.
- **`/api/hospital/counter`**: Updates the occupied count for a specific hospital ward.
- **`/api/holds/active` & `/api/blood`**: Retrieves active holds and current blood inventory data.

## Technical Explanations
**CORS (Cross-Origin Resource Sharing):**
CORS is a security feature that restricts web applications from making requests to a different domain. I enabled it using `flask_cors` so our frontend (which might run on a different port or domain) can successfully communicate with this backend API without being blocked by the browser.

**TTL Worker Background Thread:**
The TTL worker is started as a background thread right after app initialization. It continuously runs independently of the main API threads, periodically checking and cleaning up expired bed holds without blocking any incoming HTTP requests.

## Tough Judge Questions & Winning Answers

**1. "Why Flask and not Django or FastAPI?"**
*Answer:* We chose Flask because it is lightweight and highly flexible, which is perfect for building a focused API for a hackathon. Unlike Django, it doesn't force a monolithic structure, and it allowed us to get our endpoints up and running extremely quickly while integrating perfectly with Supabase.

**2. "How does your backend handle concurrent requests?"**
*Answer:* Flask handles concurrent requests through its underlying WSGI server, which spins up multiple worker threads. Combined with our atomic database operations in Supabase, our backend safely manages multiple users requesting beds at the exact same time without data corruption.

**3. "What is CORS and why did you enable it?"**
*Answer:* CORS stands for Cross-Origin Resource Sharing. Because our frontend and backend run on different ports during development and potentially different domains in production, we enabled CORS so the browser's security policies wouldn't block our frontend from fetching data.

**4. "How do you handle errors in your API?"**
*Answer:* Our API proactively validates incoming JSON payloads, ensuring required fields are present before processing. If data is missing or a database operation fails, we catch the exception and return a clear JSON error message with a 400 status code, preventing the server from crashing.

**5. "Why did you choose Render instead of deploying the whole app on Vercel?"**
*Answer:* While Vercel is fantastic for static frontends, Render is better suited for our Flask backend because it supports long-running background processes. We need a persistent environment to keep our daemon TTL worker running continuously to clear expired bed holds.
