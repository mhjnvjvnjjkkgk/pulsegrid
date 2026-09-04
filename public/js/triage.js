// ============================================================
// PulseGrid - Triage & UI Logic
// Member 5's Domain
//
// This file handles:
// 1. Web Speech Recognition (voice input)
// 2. Triage flow (quick buttons + text search)
// 3. Hospital card rendering
// 4. Countdown timer for active holds
// 5. Transit modal with OTP display
// 6. Leaflet.js map with hospital markers
// 7. Citizen/Paramedic mode switching
// ============================================================

// ---- Global State ----
let currentMode = 'citizen';           // 'citizen' or 'paramedic'
let mapInstance = null;                 // Leaflet map object
let mapMarkers = [];                   // Array of map markers
let userLocation = null;               // User's GPS position
let currentHoldTimer = null;           // setInterval ID for countdown
let currentTriageWard = '';            // Last triage recommended ward key
let currentTriageSeverity = 'YELLOW';  // Last triage severity
let allHospitals = [];                 // Cached hospital list


// ============================================================
// INITIALIZATION (runs when page loads)
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    initSpeechRecognition();
    setupEventListeners();
    initMap();

    // Try to get user's location for distance calculation
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                console.log('[TRIAGE] Got user location:', userLocation);
            },
            (err) => console.log('[TRIAGE] Geolocation denied, showing all hospitals')
        );
    }

    // Load hospitals on startup
    await loadHospitals();

    // Start polling every 4 seconds for live bed updates
    startPolling(async () => {
        // Only poll with the current triage ward filter if one is active
        await loadHospitals(null, currentTriageWard || null);
    }, 4000);
});


// ============================================================
// EVENT LISTENERS
// ============================================================
function setupEventListeners() {
    // Mode switcher button
    document.getElementById('mode-switcher').addEventListener('click', toggleMode);

    // Quick-tap emergency buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const query = e.currentTarget.dataset.query;
            document.getElementById('search-input').value = query;
            await processTriage(query);
        });
    });

    // Search button
    document.getElementById('search-btn').addEventListener('click', async () => {
        const query = document.getElementById('search-input').value.trim();
        if (query) await processTriage(query);
    });

    // Search input - Enter key
    document.getElementById('search-input').addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) await processTriage(query);
        }
    });

    // Cancel hold button
    document.getElementById('cancel-hold-btn').addEventListener('click', closeTransitModal);
}


// ============================================================
// MODE SWITCHING (Citizen ↔ Paramedic)
// ============================================================
function toggleMode() {
    currentMode = currentMode === 'citizen' ? 'paramedic' : 'citizen';
    const switcher = document.getElementById('mode-switcher');

    if (currentMode === 'paramedic') {
        switcher.innerHTML = '<span class="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span> Paramedic 108';
        switcher.className = 'glass-panel px-4 py-2 flex items-center gap-2 cursor-pointer border-purple-500/30 text-purple-300 transition-colors';
    } else {
        switcher.innerHTML = '<span class="w-2 h-2 rounded-full bg-blue-500"></span> Citizen';
        switcher.className = 'glass-panel px-4 py-2 flex items-center gap-2 cursor-pointer border-blue-500/30 text-blue-300 transition-colors';
    }
}


// ============================================================
// WEB SPEECH RECOGNITION (Voice Input)
// ============================================================
function initSpeechRecognition() {
    const micBtn = document.getElementById('mic-btn');
    const searchInput = document.getElementById('search-input');

    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.title = 'Speech recognition not supported in this browser';
        micBtn.style.opacity = '0.3';
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;      // Single utterance mode
    recognition.interimResults = true;   // Show live preview
    recognition.lang = 'en-IN';          // Indian English

    let isRecording = false;
    let finalTranscript = '';

    micBtn.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            finalTranscript = '';
            try {
                recognition.start();
            } catch (e) {
                console.error('[SPEECH] Failed to start:', e);
            }
        }
    });

    recognition.onstart = () => {
        isRecording = true;
        micBtn.style.animation = 'micPulse 1.5s infinite';
        micBtn.style.color = '#ef4444';
        searchInput.placeholder = '🎙️ Listening... speak now';
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        searchInput.value = finalTranscript || interimTranscript;
    };

    recognition.onerror = (event) => {
        console.warn('[SPEECH] Error:', event.error);
        if (event.error === 'not-allowed') {
            alert('Microphone access denied. Please allow microphone permissions in your browser settings.');
        }
        isRecording = false;
        micBtn.style.animation = 'none';
        micBtn.style.color = 'var(--text-secondary)';
        searchInput.placeholder = 'Describe symptom or injury...';
    };

    recognition.onend = () => {
        isRecording = false;
        micBtn.style.animation = 'none';
        micBtn.style.color = 'var(--text-secondary)';
        searchInput.placeholder = 'Describe symptom or injury...';

        // Auto-submit after speech ends
        const text = searchInput.value.trim();
        if (text) {
            processTriage(text);
        }
    };
}


// ============================================================
// TRIAGE PROCESSING
// ============================================================
async function processTriage(query) {
    const triagePanel = document.getElementById('triage-result-panel');
    const badge = document.getElementById('triage-badge');
    const wardTxt = document.getElementById('triage-ward');
    const reasonTxt = document.getElementById('triage-reason');

    // Show panel with loading state
    triagePanel.classList.remove('hidden');
    triagePanel.style.animation = 'fadeInUp 0.4s ease-out';
    badge.textContent = 'Analyzing...';
    badge.className = 'px-3 py-1 rounded-full text-sm font-semibold bg-white/10 text-white';

    // Call the backend triage API
    const result = await submitTriage(query);

    if (!result || result.error) {
        badge.textContent = 'YELLOW Priority';
        badge.className = 'px-3 py-1 rounded-full text-sm font-semibold uppercase status-pill-amber';
        wardTxt.textContent = 'Recommended: General Ward';
        reasonTxt.textContent = 'Could not connect to triage engine. Defaulting to general observation.';
        currentTriageWard = 'general_ward';
        currentTriageSeverity = 'YELLOW';
        await loadHospitals(null, 'general_ward');
        return;
    }

    // Map severity to CSS class
    const severity = (result.severity || 'YELLOW').toUpperCase();
    let severityClass = 'status-pill-green';
    let borderClass = 'border-l-emerald-500';
    if (severity === 'RED') {
        severityClass = 'status-pill-red';
        borderClass = 'border-l-red-500';
    } else if (severity === 'YELLOW') {
        severityClass = 'status-pill-amber';
        borderClass = 'border-l-amber-500';
    }

    // Update the triage result panel
    badge.className = `px-3 py-1 rounded-full text-sm font-semibold uppercase ${severityClass}`;
    badge.textContent = `${severity} Priority`;
    wardTxt.textContent = `Recommended: ${result.ward || result.recommended_ward || 'General Ward'}`;
    reasonTxt.textContent = result.explanation || result.reason || 'Analysis complete.';

    // Update the border color of the triage panel
    const panelDiv = triagePanel.querySelector('.glass-panel');
    if (panelDiv) {
        panelDiv.className = `glass-panel p-6 border-l-4 ${borderClass} flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4`;
    }

    // Store triage results for hold creation
    currentTriageWard = result.recommended_ward || 'general_ward';
    currentTriageSeverity = severity;

    // Reload hospitals filtered by recommended ward
    await loadHospitals(null, currentTriageWard);
}


// ============================================================
// HOSPITAL LOADING & CARD RENDERING
// ============================================================
async function loadHospitals(specialty, ward) {
    const hospitals = await fetchFacilities(specialty || '', ward || '');
    if (hospitals && hospitals.length > 0) {
        allHospitals = hospitals;
    }
    renderHospitalCards(allHospitals);
    updateMapMarkers(allHospitals);
}


function renderHospitalCards(hospitals) {
    const container = document.getElementById('hospital-grid');
    container.innerHTML = '';

    if (!hospitals || hospitals.length === 0) {
        container.innerHTML = `
            <div class="glass-panel p-8 text-center col-span-full">
                <p class="text-slate-400 text-lg">No hospitals found matching your criteria.</p>
                <p class="text-slate-500 text-sm mt-2">Try a different search or check back shortly.</p>
            </div>
        `;
        return;
    }

    hospitals.forEach((h, i) => {
        const card = document.createElement('div');
        card.className = `glass-panel p-5 fade-in-up`;
        card.style.animationDelay = `${(i % 6) * 80}ms`;

        // Build ward availability section
        let wardsHtml = '';
        if (h.wards) {
            for (const [wName, wData] of Object.entries(h.wards)) {
                if (wData.total === 0) continue; // Skip wards with no beds
                const avail = wData.available || 0;
                const total = wData.total || 0;
                const isFull = avail === 0;
                const color = isFull ? 'text-red-400' : 'text-emerald-400';
                const bgColor = isFull ? 'bg-red-500/5' : '';
                wardsHtml += `
                    <div class="flex justify-between items-center text-sm py-1 px-2 rounded ${bgColor}">
                        <span class="text-slate-300">${wName}</span>
                        <span class="font-mono font-bold ${color}">${avail}<span class="text-slate-500">/${total}</span></span>
                    </div>
                `;
            }
        } else {
            // Fallback: build from flat columns
            const wardTypes = [
                ['Adult ICU', 'adult_icu'],
                ['Pediatric ICU', 'pediatric_icu'],
                ['Cardiac ICU', 'cardiac_icu'],
                ['General', 'general_ward']
            ];
            for (const [name, prefix] of wardTypes) {
                const total = h[`${prefix}_total`] || 0;
                if (total === 0) continue;
                const occupied = h[`${prefix}_occupied`] || 0;
                const held = h[`${prefix}_held`] || 0;
                const avail = Math.max(0, total - occupied - held);
                const color = avail === 0 ? 'text-red-400' : 'text-emerald-400';
                wardsHtml += `
                    <div class="flex justify-between items-center text-sm py-1 px-2 rounded">
                        <span class="text-slate-300">${name}</span>
                        <span class="font-mono font-bold ${color}">${avail}<span class="text-slate-500">/${total}</span></span>
                    </div>
                `;
            }
        }

        // Calculate distance if user location is available
        let distanceText = '';
        if (userLocation && h.latitude && h.longitude) {
            const dist = calculateDistance(userLocation.lat, userLocation.lng, h.latitude, h.longitude);
            distanceText = `${dist.toFixed(1)} km`;
        }

        // Build card HTML — NOTE: h.id is quoted as a string because it's a UUID
        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div class="flex-1 min-w-0">
                    <h3 class="font-bold text-lg text-white mb-1 truncate">${escapeHtml(h.name)}</h3>
                    <p class="text-sm text-slate-400 truncate">${escapeHtml(h.address || '')}</p>
                </div>
                ${distanceText ? `
                    <div class="bg-blue-500/10 text-blue-400 px-2 py-1 rounded text-sm font-semibold border border-blue-500/20 ml-2 flex-shrink-0">
                        ${distanceText}
                    </div>
                ` : ''}
            </div>

            <div class="mb-4 bg-black/20 p-3 rounded-xl border border-white/5 space-y-1">
                ${wardsHtml || '<p class="text-sm text-slate-500">No ward data available</p>'}
            </div>

            <button onclick="requestHold('${h.id}', '${escapeHtml(h.name).replace(/'/g, "\\'")}')" 
                    class="w-full btn-primary flex justify-center items-center gap-2 py-3">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Request Bed Hold (${currentMode === 'paramedic' ? '20' : '15'} min)
            </button>
        `;
        container.appendChild(card);
    });
}


// ============================================================
// BED HOLD REQUEST (connects to real backend)
// ============================================================
async function requestHold(hospitalId, hospitalName) {
    // Prompt for phone number
    const phone = prompt('Enter emergency contact phone number:', '9876543210');
    if (!phone || !phone.trim()) return;

    const holdType = currentMode;  // 'citizen' or 'paramedic'
    const wardType = currentTriageWard || 'general_ward';
    const severity = currentTriageSeverity || 'YELLOW';

    // Show loading state
    const btns = document.querySelectorAll('.btn-primary');
    btns.forEach(b => { b.disabled = true; b.style.opacity = '0.5'; });

    // Call the backend API to create the hold
    const result = await createHold(hospitalId, wardType, holdType, phone, severity);

    // Reset buttons
    btns.forEach(b => { b.disabled = false; b.style.opacity = '1'; });

    if (result && result.otp) {
        // Success! Show the transit modal with OTP and countdown
        const holdMins = result.minutes || (holdType === 'paramedic' ? 20 : 15);
        openTransitModal({
            hospitalName: hospitalName,
            otp: result.otp,
            holdId: result.hold_id,
            expiresAt: result.expires_at,
            mins: holdMins
        });
    } else {
        // Show error
        const errorMsg = (result && result.message) ? result.message : 'No beds available or server error';
        alert('❌ Hold failed: ' + errorMsg);
    }
}


// ============================================================
// TRANSIT MODAL (OTP display + countdown timer)
// ============================================================
function openTransitModal(data) {
    const modal = document.getElementById('transit-modal');
    document.getElementById('modal-hospital-name').textContent = data.hospitalName;
    document.getElementById('modal-otp').textContent = data.otp;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.style.animation = 'fadeInUp 0.3s ease-out';

    // Set initial time display immediately
    const totalSeconds = data.mins * 60;
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    document.getElementById('countdown-text').textContent =
        `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    startCountdown(totalSeconds);
}

function closeTransitModal() {
    const modal = document.getElementById('transit-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    if (currentHoldTimer) clearInterval(currentHoldTimer);

    // Reset countdown text color
    const countdownText = document.getElementById('countdown-text');
    if (countdownText) countdownText.classList.remove('text-red-500');
}


function startCountdown(totalSeconds) {
    if (currentHoldTimer) clearInterval(currentHoldTimer);

    let remaining = totalSeconds;
    const timeDisplay = document.getElementById('countdown-text');

    // Target the second <circle> element (the progress ring), not the <svg>
    const svg = document.querySelector('.countdown-ring');
    const circles = svg ? svg.querySelectorAll('circle') : [];
    const progressCircle = circles.length >= 2 ? circles[1] : null;

    const circumference = 2 * Math.PI * 54; // r=54 from the SVG

    if (progressCircle) {
        progressCircle.style.strokeDasharray = circumference;
        progressCircle.style.strokeDashoffset = '0';
        progressCircle.style.transition = 'stroke-dashoffset 1s linear';
    }

    currentHoldTimer = setInterval(() => {
        remaining--;
        const mins = Math.floor(remaining / 60);
        const secs = remaining % 60;
        timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        // Update circular progress
        if (progressCircle) {
            const offset = circumference - (remaining / totalSeconds) * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }

        // Change color when < 2 minutes
        if (remaining < 120) {
            timeDisplay.classList.add('text-red-500');
            if (progressCircle) progressCircle.style.stroke = '#ef4444';
        }

        if (remaining <= 0) {
            clearInterval(currentHoldTimer);
            timeDisplay.textContent = '00:00';
            timeDisplay.classList.add('text-red-500');
        }
    }, 1000);
}


// ============================================================
// LEAFLET MAP
// ============================================================
function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    // Center on Kolkata
    mapInstance = L.map('map', {
        zoomControl: false
    }).setView([22.5726, 88.3639], 12);

    // Dark-themed map tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
        maxZoom: 19
    }).addTo(mapInstance);

    // Add zoom control to bottom-right
    L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
}


function updateMapMarkers(hospitals) {
    if (!mapInstance) return;

    // Clear existing markers
    mapMarkers.forEach(m => mapInstance.removeLayer(m));
    mapMarkers = [];

    // Add a marker for each hospital
    hospitals.forEach(h => {
        if (!h.latitude || !h.longitude) return;

        const marker = L.circleMarker([h.latitude, h.longitude], {
            radius: 8,
            fillColor: '#3b82f6',
            color: '#1e40af',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(mapInstance);

        // Popup with hospital info
        const popupHtml = `
            <div style="font-family: Inter, sans-serif; min-width: 180px;">
                <strong>${escapeHtml(h.name)}</strong><br>
                <small style="color: #666;">${escapeHtml(h.address || '')}</small>
            </div>
        `;
        marker.bindPopup(popupHtml);

        mapMarkers.push(marker);
    });

    // Add user location marker if available
    if (userLocation) {
        const userMarker = L.circleMarker([userLocation.lat, userLocation.lng], {
            radius: 10,
            fillColor: '#ef4444',
            color: '#fff',
            weight: 3,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(mapInstance);
        userMarker.bindPopup('<strong>📍 Your Location</strong>');
        mapMarkers.push(userMarker);
    }
}


// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Calculate distance between two GPS coordinates using the
 * Haversine formula. Returns distance in kilometers.
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}


/**
 * Escape HTML special characters to prevent XSS injection
 * when inserting user-provided data into innerHTML.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}
