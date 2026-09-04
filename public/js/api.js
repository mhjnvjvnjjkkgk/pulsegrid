// ============================================================
// PulseGrid - Frontend API Client
// Member 5's Domain
//
// This file handles ALL communication between the browser
// and the Flask backend. It uses the native fetch() API.
// ============================================================

// Where the Flask backend is running.
// Change this to your Render URL when deploying.
const BASE_URL = 'http://localhost:5000';


// ============================================================
// TRIAGE: Send symptom text, get severity classification
// ============================================================
async function submitTriage(text) {
    try {
        const res = await fetch(`${BASE_URL}/api/triage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Triage error:', err);
        return null;
    }
}


// ============================================================
// FACILITIES: Get list of hospitals with available beds
// ============================================================
async function fetchFacilities(specialty, ward) {
    try {
        const url = new URL(`${BASE_URL}/api/facilities`);
        if (specialty) url.searchParams.append('specialty', specialty);
        if (ward) url.searchParams.append('ward', ward);
        
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Fetch facilities error:', err);
        return [];
    }
}


// ============================================================
// HOLDS: Create a new bed reservation (atomic operation)
// Returns: { otp, hold_id, expires_at } on success
// ============================================================
async function createHold(hospitalId, resourceType, holdType, phone, severity) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hospital_id: hospitalId,
                resource_type: resourceType,
                hold_type: holdType,
                requester_phone: phone,   // Must match backend field name
                severity: severity
            })
        });
        if (!res.ok) {
            const errorData = await res.json();
            return { error: true, message: errorData.error || 'Failed to create hold' };
        }
        return await res.json();
    } catch (err) {
        console.error('[API] Create hold error:', err);
        return { error: true, message: err.message };
    }
}


// ============================================================
// REDEEM: Nurse enters OTP to admit patient
// ============================================================
async function redeemHold(hospitalId, otpCode) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/redeem`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hospital_id: hospitalId,
                otp_code: otpCode
            })
        });
        if (!res.ok) {
            const errorData = await res.json();
            return { error: true, message: errorData.error || 'Redemption failed' };
        }
        return await res.json();
    } catch (err) {
        console.error('[API] Redeem hold error:', err);
        return { error: true, message: err.message };
    }
}


// ============================================================
// COUNTER: Nurse taps [+] or [-] to adjust bed count
// ============================================================
async function updateCounter(hospitalId, ward, delta) {
    try {
        const res = await fetch(`${BASE_URL}/api/hospital/counter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hospital_id: hospitalId,
                ward: ward,
                delta: delta
            })
        });
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Update counter error:', err);
        return { error: true, message: err.message };
    }
}


// ============================================================
// ACTIVE HOLDS: Get incoming patients for a hospital
// ============================================================
async function fetchActiveHolds(hospitalId) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/active?hospital_id=${encodeURIComponent(hospitalId)}`);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Fetch active holds error:', err);
        return [];
    }
}


// ============================================================
// BLOOD: Get blood inventory for a hospital
// ============================================================
async function fetchBloodInventory(hospitalId) {
    try {
        let url = `${BASE_URL}/api/blood`;
        if (hospitalId) url += `?hospital_id=${encodeURIComponent(hospitalId)}`;
        
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Fetch blood error:', err);
        return [];
    }
}


// ============================================================
// POLLING ENGINE: Auto-refresh data every N milliseconds
// ============================================================
let pollingInterval = null;

function startPolling(callback, interval) {
    if (pollingInterval) stopPolling();
    pollingInterval = setInterval(callback, interval || 4000);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}
