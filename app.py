# ============================================================
# PulseGrid - Flask API Server
# Member 1's Domain
#
# This is the main server file. It creates a Flask web server
# with API endpoints that the frontend calls. It also starts
# the TTL background worker that auto-expires stale holds.
#
# Tech: Flask + flask-cors + python-dotenv
# ============================================================

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import our other modules
import database
import triage_service
import ttl_worker

# Load environment variables from .env file
load_dotenv()

# Create the Flask app
app = Flask(__name__)

# Enable CORS so the frontend (on a different URL like Vercel)
# can make API calls to this backend without browser blocking
CORS(app)

# Initialize the Supabase database connection
database.init_supabase()

# Start the background worker that auto-expires stale holds
ttl_worker.start_ttl_worker(database)


# ============================================================
# ROUTE: Health Check
# GET /
# Returns: server status and version
# ============================================================
@app.route("/", methods=["GET"])
def health_check():
    """Simple health check to verify the API is running."""
    return jsonify({
        "status": "PulseGrid API Online",
        "version": "1.0.0",
        "message": "Emergency Bed & Blood Triage Engine"
    })


# ============================================================
# ROUTE: Triage & Unified Search
# POST /api/triage & POST /api/search
# Body: { "text": "patient has chest pain", "lat": 22.5, "lng": 88.3 }
# Returns: { severity, recommended_ward, ward, explanation, is_blood_query, blood_group, recommended_hospitals }
# ============================================================
@app.route("/api/triage", methods=["POST"])
@app.route("/api/search", methods=["POST"])
def triage_and_search():
    """Classifies patient symptoms and blood terms, returning urgency & hospital matches."""
    data = request.get_json() or {}
    text = data.get("text") or data.get("query") or ""
    if not text:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    # 1. Symptom classification
    result = triage_service.classify_symptoms(text)

    # 2. Blood search parsing
    blood_group = triage_service.parse_blood_search(text)
    is_blood_query = blood_group is not None

    # 3. Facilities query
    specialty = data.get("specialty")
    ward = result.get("recommended_ward")
    hospitals = database.get_all_hospitals(specialty_filter=specialty, ward_filter=ward)

    blood_matches = []
    if is_blood_query:
        inventory = database.get_blood_inventory()
        blood_matches = [b for b in inventory if b.get("blood_group") == blood_group]

    response = {
        "success": True,
        "ok": True,
        "severity": result.get("severity"),
        "recommended_ward": result.get("recommended_ward"),
        "ward": result.get("ward"),
        "explanation": result.get("explanation"),
        "matched_keywords": result.get("matched_keywords", []),
        "is_blood_query": is_blood_query,
        "blood_group": blood_group,
        "recommended_hospitals": hospitals,
        "hospitals": hospitals,
        "blood_matches": blood_matches
    }
    return jsonify(response)


# ============================================================
# ROUTE: Facilities
# GET /api/facilities?specialty=cardiac&ward=adult_icu
# Returns: list of hospitals with bed availability
# ============================================================
@app.route("/api/facilities", methods=["GET"])
def facilities():
    """Gets hospitals with available beds, optionally filtered."""
    specialty = request.args.get("specialty")
    ward = request.args.get("ward")
    hospitals = database.get_all_hospitals(specialty, ward)
    return jsonify(hospitals)


# ============================================================
# ROUTE: Create Hold (Soft-Lock)
# POST /api/holds/create
# Body: { hospital_id, resource_type/ward_code, hold_type, phone/requester_phone, severity }
# Returns: { success, hold_id, otp_code, expires_at, bed_count }
# ============================================================
@app.route("/api/holds/create", methods=["POST"])
def create_hold():
    """Creates a temporary bed soft-lock reservation with a 4-digit OTP."""
    data = request.get_json() or {}
    hospital_id = data.get("hospital_id")
    resource_type = data.get("resource_type") or data.get("ward_code") or "general_ward"
    hold_type = data.get("hold_type", "CITIZEN")
    phone = data.get("requester_phone") or data.get("phone", "9999999999")
    severity = data.get("severity", "RED")

    if not hospital_id:
        return jsonify({"error": "Missing required field: hospital_id"}), 400

    result = database.create_live_hold(
        hospital_id,
        resource_type,
        hold_type,
        phone,
        severity
    )

    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


# ============================================================
# ROUTE: Redeem Hold (Hard-Lock)
# POST /api/holds/redeem
# Body: { hospital_id, otp_code } or { hold_id, otp_code }
# Returns: { success: true, status: "REDEEMED", bed_count }
# ============================================================
@app.route("/api/holds/redeem", methods=["POST"])
def redeem_hold():
    """Validates the 4-digit OTP when patient arrives at hospital, hard-locking the bed."""
    data = request.get_json() or {}
    otp_code = data.get("otp_code") or data.get("otp")
    hospital_id = data.get("hospital_id")
    hold_id = data.get("hold_id")

    if not otp_code:
        return jsonify({"error": "Missing otp_code"}), 400

    if hold_id and not hospital_id:
        hold_info = database.get_hold_by_id(hold_id)
        if "hospital_id" in hold_info:
            hospital_id = hold_info["hospital_id"]

    if not hospital_id:
        return jsonify({"error": "Missing hospital_id or valid hold_id"}), 400

    result = database.redeem_hold(hospital_id, str(otp_code))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


# ============================================================
# ROUTE: Manual Cancel Hold
# POST /api/holds/cancel
# Body: { hold_id, phone }
# Returns: { success: true, status: "CANCELLED", bed_count }
# ============================================================
@app.route("/api/holds/cancel", methods=["POST"])
def cancel_hold():
    """Manually cancels active soft lock and restores bed count to pool."""
    data = request.get_json() or {}
    hold_id = data.get("hold_id")
    phone = data.get("requester_phone") or data.get("phone")

    if not hold_id:
        return jsonify({"error": "Missing hold_id"}), 400

    result = database.cancel_hold(hold_id, phone)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


# ============================================================
# ROUTE: GPS Location & Vector Update
# POST /api/holds/location_update
# Body: { hold_id, user_lat, user_lng, heading, speed }
# Returns: { status, movement_direction, current_eta_minutes, wrong_direction_count }
# ============================================================
@app.route("/api/holds/location_update", methods=["POST"])
def update_location():
    """Processes patient GPS updates, tracking directional vector and auto-cancelling if off-track."""
    data = request.get_json() or {}
    hold_id = data.get("hold_id")
    user_lat = data.get("user_lat") if data.get("user_lat") is not None else data.get("lat")
    user_lng = data.get("user_lng") if data.get("user_lng") is not None else data.get("lng")
    heading = data.get("heading")
    speed = data.get("speed")

    if not hold_id or user_lat is None or user_lng is None:
        return jsonify({"error": "Missing required fields: hold_id, user_lat, user_lng"}), 400

    result = database.update_hold_location(hold_id, float(user_lat), float(user_lng), heading, speed)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


# ============================================================
# ROUTE: Get Hold Details
# GET /api/holds/<hold_id>
# Returns: hold details object
# ============================================================
@app.route("/api/holds/<hold_id>", methods=["GET"])
def get_hold_details(hold_id):
    """Gets details and live countdown status of a specific hold."""
    result = database.get_hold_by_id(hold_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)



# ============================================================
# ROUTE: Quick Counter
# POST /api/hospital/counter
# Body: { hospital_id, ward, delta }
# Returns: { success, new_occupied, total }
# ============================================================
@app.route("/api/hospital/counter", methods=["POST"])
def update_counter():
    """Nurse taps [+] or [-] to adjust occupied bed count."""
    data = request.get_json()
    if not data or not all(k in data for k in ["hospital_id", "ward", "delta"]):
        return jsonify({"error": "Missing hospital_id, ward, or delta"}), 400

    result = database.update_quick_counter(
        data["hospital_id"],
        data["ward"],
        int(data["delta"])
    )

    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


# ============================================================
# ROUTE: Active Holds
# GET /api/holds/active?hospital_id=...
# Returns: list of active holds for the hospital
# ============================================================
@app.route("/api/holds/active", methods=["GET"])
def active_holds():
    """Gets all active incoming holds for a hospital's queue."""
    hospital_id = request.args.get("hospital_id")
    if not hospital_id:
        return jsonify({"error": "Missing hospital_id parameter"}), 400

    holds = database.get_active_holds(hospital_id)
    return jsonify(holds)


# ============================================================
# ROUTE: Blood Inventory
# GET /api/blood?hospital_id=...
# Returns: blood inventory records
# ============================================================
@app.route("/api/blood", methods=["GET"])
def blood_inventory():
    """Gets blood inventory, optionally for a specific hospital."""
    hospital_id = request.args.get("hospital_id")
    inventory = database.get_blood_inventory(hospital_id)
    return jsonify(inventory)


# ============================================================
# START THE SERVER
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"[PULSEGRID] Starting server on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
