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
# ROUTE: Triage
# POST /api/triage
# Body: { "text": "patient has chest pain" }
# Returns: { severity, recommended_ward, ward, explanation }
# ============================================================
@app.route("/api/triage", methods=["POST"])
def triage():
    """Classifies patient symptoms into RED/YELLOW/GREEN urgency."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    result = triage_service.classify_symptoms(data["text"])
    return jsonify(result)


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
# ROUTE: Create Hold
# POST /api/holds/create
# Body: { hospital_id, resource_type, hold_type, phone/requester_phone, severity }
# Returns: { otp, hold_id, expires_at }
# ============================================================
@app.route("/api/holds/create", methods=["POST"])
def create_hold():
    """Creates a temporary bed reservation with a 4-digit OTP."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    # Accept both 'phone' and 'requester_phone' for compatibility
    phone = data.get("requester_phone") or data.get("phone", "")

    # Validate required fields
    required = ["hospital_id", "resource_type", "hold_type", "severity"]
    if not all(k in data for k in required) or not phone:
        return jsonify({"error": "Missing required fields: hospital_id, resource_type, hold_type, phone, severity"}), 400

    result = database.create_live_hold(
        data["hospital_id"],
        data["resource_type"],
        data["hold_type"],
        phone,
        data["severity"]
    )

    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


# ============================================================
# ROUTE: Redeem Hold
# POST /api/holds/redeem
# Body: { hospital_id, otp_code }
# Returns: { success: true } or { error: "..." }
# ============================================================
@app.route("/api/holds/redeem", methods=["POST"])
def redeem_hold():
    """Validates the 4-digit OTP when patient arrives at hospital."""
    data = request.get_json()
    if not data or "hospital_id" not in data or "otp_code" not in data:
        return jsonify({"error": "Missing hospital_id or otp_code"}), 400

    result = database.redeem_hold(data["hospital_id"], data["otp_code"])
    if "error" in result:
        return jsonify(result), 400
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
# ROUTE: Create Blood Hold
# POST /api/blood/hold
# Body: { "hospital_id": "...", "blood_group": "...", "component": "...", "units": 1, "requester_phone": "..." }
# ============================================================
@app.route("/api/blood/hold", methods=["POST"])
def blood_hold():
    """Reserves blood units."""
    data = request.json or {}
    hospital_id = data.get("hospital_id")
    blood_group = data.get("blood_group")
    component = data.get("component")
    units = int(data.get("units", 1))
    phone = data.get("requester_phone", "000-000-0000")

    if not all([hospital_id, blood_group, component]):
        return jsonify({"error": "Missing required fields"}), 400

    result = database.create_blood_hold(hospital_id, blood_group, component, units, phone)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

# ============================================================
# ROUTE: Redeem Blood Hold
# POST /api/blood/redeem
# Body: { "otp": "1234" }
# ============================================================
@app.route("/api/blood/redeem", methods=["POST"])
def redeem_blood_hold():
    """Redeems a blood hold with an OTP."""
    data = request.json or {}
    otp = data.get("otp")

    if not otp:
        return jsonify({"error": "Missing otp"}), 400

    result = database.redeem_blood_hold(otp)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

# ============================================================
# START THE SERVER
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"[PULSEGRID] Starting server on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
