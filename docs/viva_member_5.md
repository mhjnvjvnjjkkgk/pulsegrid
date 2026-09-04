# Viva Preparation Guide: Frontend API Developer

**Role:** "I built the frontend JavaScript that connects the browser to the backend and handles voice input"

**Elevator Pitch:**
I developed the critical frontend logic that powers PulseGrid's interactivity. I implemented robust API fetch wrappers, a reliable background polling engine for real-time updates, and integrated the Web Speech API to allow hands-free voice triage for paramedics and patients.

## Code Walkthrough
**`api.js`:**
This file encapsulates all backend communication using the native `fetch` API. It includes functions like `submitTriage`, `fetchFacilities`, and `createHold` which parse JSON payloads and gracefully handle HTTP errors. It also contains the `startPolling` engine that runs a callback function on a set interval.

**`triage.js`:**
This file bridges the UI with the API. 
- **`initSpeechRecognition`**: Wires up the microphone button to capture voice input.
- **`processTriage`**: Sends the text to the backend and updates the UI with the severity badge.
- **`loadHospitals` & `renderHospitalCards`**: Fetches the latest hospital data and dynamically injects HTML cards into the grid.
- **`startCountdown`**: Manages the circular SVG timer in the transit modal.

## Technical Explanations
**Web Speech API:**
The Web Speech API is a native browser feature that provides speech recognition without needing external libraries. I used it to capture both interim (in-progress) and final voice transcripts, allowing users to speak their symptoms directly into the search bar.

**Polling vs WebSockets:**
We implemented a 4-second polling mechanism to repeatedly fetch the latest hospital data. While WebSockets provide true push-based real-time updates, polling was chosen because it is incredibly reliable, easier to implement in a hackathon timeframe, and sufficiently fast for our use case.

## Tough Judge Questions & Winning Answers

**1. "Why fetch() and not Axios or jQuery AJAX?"**
*Answer:* The native `fetch` API is built directly into modern browsers, so it requires zero external dependencies, keeping our frontend lightweight and fast. It natively supports Promises and async/await, making our code clean and easy to read.

**2. "How does the 4-second polling work and why not use WebSockets?"**
*Answer:* The polling engine uses `setInterval` to fetch hospital data every 4 seconds. We chose polling over WebSockets because it was much faster to implement securely, avoids complex socket state management, and updates the UI fast enough for emergency tracking without heavy server load.

**3. "Explain how the Web Speech Recognition API works"**
*Answer:* It taps into the browser's native recognition engine. When activated, it listens to the microphone and triggers an `onresult` event. I parse the event results, combining the interim and final transcripts, and inject that text directly into the triage search input.

**4. "What happens if the browser doesn't support speech recognition?"**
*Answer:* I implemented a feature check at the start of the function. If `window.SpeechRecognition` and `window.webkitSpeechRecognition` are undefined, the code gracefully degrades by simply hiding the microphone button, allowing the user to type their symptoms manually.

**5. "How does the countdown timer work in the transit modal?"**
*Answer:* It uses `setInterval` to decrement a total seconds variable every second. I update the text display and mathematically calculate the `stroke-dashoffset` for the circular SVG ring, creating a smooth visual progress bar that alerts the user when the hold expires.
