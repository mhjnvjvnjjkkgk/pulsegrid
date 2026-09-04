# Viva Preparation Guide: AI Triage Developer

**Role:** "I built the AI triage engine that classifies patient urgency"

**Elevator Pitch:**
I developed the AI triage engine that rapidly analyzes patient symptoms and categorizes them into severity levels. By using a weighted keyword and phrase-matching algorithm, it instantly recommends the appropriate hospital ward, drastically reducing intake delays during emergencies.

## Code Walkthrough: `triage_service.py`
The `triage_service.py` file powers the symptom classification logic.
- **Symptom Database**: A dictionary mapping critical phrases (e.g., "chest pain", "head injury") to a severity level (RED, YELLOW, GREEN), a recommended ward, and a medical explanation.
- **`classify_symptoms` Function**: It converts user input to lowercase and iterates through the database. It matches keywords and tracks the highest weight found, ensuring that the most severe symptom dictates the final classification and ward recommendation.

## Technical Explanations
**RED vs YELLOW vs GREEN Severity:**
- **RED**: Critical, life-threatening emergencies (e.g., cardiac arrest, severe bleeding) requiring immediate ICU care.
- **YELLOW**: Urgent cases (e.g., high fever, breathing difficulty) needing prompt attention in general or pediatric wards.
- **GREEN**: Non-urgent scenarios (e.g., mild fever, minor cuts) where standard care is appropriate.

**Keyword Weighting (3x, 2x, 1x):**
Symptoms are weighted by their severity: RED is weight 3, YELLOW is 2, and GREEN is 1. The algorithm tracks the `highest_weight_matched`. If a patient has multiple symptoms, the highest weight always wins, ensuring a minor symptom doesn't accidentally downgrade a critical emergency.

**Bigram/Trigram Matching:**
Instead of just matching single words, our database uses exact multi-word phrases (bigrams/trigrams) like "heart attack" or "chest pain". This provides much better context and accuracy than single words, preventing false positives and ensuring precise triage.

## Tough Judge Questions & Winning Answers

**1. "Why keyword matching instead of a neural network or LLM?"**
*Answer:* For this hackathon, we needed a solution that was blazingly fast, 100% deterministic, and didn't rely on expensive third-party API calls. A weighted keyword algorithm guarantees zero latency and predictable results, which is critical in life-or-death emergency triage.

**2. "How does your scoring algorithm handle mixed symptoms?"**
*Answer:* We implemented a hierarchical weighting system where RED is 3, YELLOW is 2, and GREEN is 1. The algorithm scans all symptoms and always locks in the highest weight found, ensuring that a critical symptom will always override minor ones.

**3. "What if a patient has symptoms from multiple severity levels?"**
*Answer:* The algorithm is designed to prioritize safety above all else. If a patient mentions a GREEN symptom like a "scratch" and a RED symptom like "unconscious", the RED weight (3) immediately supersedes the GREEN weight (1), correctly classifying the patient as a critical emergency.

**4. "How would you improve this system with real AI?"**
*Answer:* I would integrate a lightweight, fine-tuned NLP model like BERT or a specialized medical LLM. This would allow the system to understand complex nuances, negations (like "no chest pain"), and typos, providing a more robust contextual analysis than exact string matching.

**5. "How accurate is keyword-based classification in real medical scenarios?"**
*Answer:* It's highly effective as a rapid first-pass filter. While it cannot replace a doctor, standard emergency dispatch protocols already rely on specific keywords to dispatch ambulances. Our system digitizes that exact protocol for instant, automated preliminary triage.
