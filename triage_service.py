# ============================================================
# PulseGrid - AI Triage Service
# Member 3's Domain
#
# This file classifies patient symptoms into urgency levels:
#   RED    = Critical (needs ICU immediately)
#   YELLOW = Moderate (needs oxygen ward / observation)
#   GREEN  = Mild (can go to local clinic)
#
# It uses keyword matching, not a neural network or LLM.
# This makes it 100% reliable with zero API dependencies.
# ============================================================


# ============================================================
# SYMPTOM DATABASE
# Each keyword maps to: (severity, ward_type, explanation)
#
# Keywords are searched inside the patient's text description.
# Longer keywords are checked FIRST so "child seizure" matches
# before "seizure" alone.
# ============================================================

SYMPTOM_DATABASE = {
    # ---- RED: CARDIAC EMERGENCIES → cardiac_icu ----
    "cardiac arrest":     ("RED", "cardiac_icu", "Possible cardiac arrest. Immediate CPR and defibrillation required."),
    "heart attack":       ("RED", "cardiac_icu", "Suspected myocardial infarction. Needs immediate cardiac intervention."),
    "chest pain":         ("RED", "cardiac_icu", "Acute chest pain may indicate cardiac event. Urgent ECG required."),
    "chest tightness":    ("RED", "cardiac_icu", "Chest tightness with possible cardiac origin. Needs monitoring."),
    "palpitations":       ("RED", "cardiac_icu", "Severe palpitations may indicate arrhythmia. Cardiac monitoring needed."),
    "angina":             ("RED", "cardiac_icu", "Angina episode. Needs nitroglycerin and cardiac evaluation."),

    # ---- RED: NEUROLOGICAL / SYSTEMIC → adult_icu ----
    "not breathing":      ("RED", "adult_icu", "Respiratory arrest. Immediate airway management required."),
    "stopped breathing":  ("RED", "adult_icu", "Respiratory failure. Urgent ventilator support needed."),
    "unconscious":        ("RED", "adult_icu", "Patient unconscious. Assess airway, breathing, circulation."),
    "unresponsive":       ("RED", "adult_icu", "Unresponsive patient. Full trauma assessment needed."),
    "seizure":            ("RED", "adult_icu", "Active seizure. Anti-epileptic medication and monitoring required."),
    "stroke":             ("RED", "adult_icu", "Suspected stroke. CT scan and thrombolysis evaluation needed."),
    "paralysis":          ("RED", "adult_icu", "Sudden paralysis may indicate stroke or spinal injury."),
    "choking":            ("RED", "adult_icu", "Airway obstruction. Heimlich maneuver and emergency care needed."),

    # ---- RED: TRAUMA / INJURY → adult_icu ----
    "severe bleeding":    ("RED", "adult_icu", "Severe hemorrhage. Immediate pressure and transfusion may be needed."),
    "heavy bleeding":     ("RED", "adult_icu", "Major blood loss. Urgent surgical intervention likely."),
    "gunshot":            ("RED", "adult_icu", "Gunshot wound. Trauma surgery required immediately."),
    "stab wound":         ("RED", "adult_icu", "Penetrating trauma. Emergency surgical assessment needed."),
    "road accident":      ("RED", "adult_icu", "Road traffic accident victim. Full trauma workup required."),
    "car accident":       ("RED", "adult_icu", "Motor vehicle accident. Assess for internal injuries."),
    "major fracture":     ("RED", "adult_icu", "Major bone fracture. Ortho assessment and possible surgery."),
    "compound fracture":  ("RED", "adult_icu", "Open fracture with bone exposure. Surgery required."),
    "head injury":        ("RED", "adult_icu", "Traumatic head injury. CT scan and neuro monitoring needed."),
    "crush injury":       ("RED", "adult_icu", "Crush injury. Risk of rhabdomyolysis and renal failure."),
    "fall from height":   ("RED", "adult_icu", "Fall from height. Spinal precautions and full assessment."),
    "electrocution":      ("RED", "adult_icu", "Electrical injury. Cardiac monitoring required."),
    "drowning":           ("RED", "adult_icu", "Near-drowning. Airway management and pulmonary assessment."),
    "burn":               ("RED", "adult_icu", "Severe burn injury. Fluid resuscitation and burn care needed."),

    # ---- RED: MATERNITY EMERGENCIES → adult_icu ----
    "eclampsia":              ("RED", "adult_icu", "Eclampsia with seizures. Magnesium sulfate and delivery needed."),
    "hemorrhage postpartum":  ("RED", "adult_icu", "Postpartum hemorrhage. Urgent uterotonic and possible surgery."),
    "placenta abruption":     ("RED", "adult_icu", "Placental abruption. Emergency caesarean may be needed."),
    "ectopic pregnancy":      ("RED", "adult_icu", "Ruptured ectopic pregnancy. Emergency surgery required."),

    # ---- YELLOW: PEDIATRIC EMERGENCIES → pediatric_icu ----
    "child breathing difficulty": ("YELLOW", "pediatric_icu", "Pediatric respiratory distress. Nebulization and monitoring."),
    "child seizure":              ("YELLOW", "pediatric_icu", "Pediatric seizure. Anti-epileptic and fever management."),
    "child high fever":           ("YELLOW", "pediatric_icu", "Pediatric high fever. Antipyretics and workup needed."),
    "infant not feeding":         ("YELLOW", "pediatric_icu", "Infant feeding failure. Assess for dehydration and infection."),
    "baby not breathing well":    ("YELLOW", "pediatric_icu", "Neonatal respiratory distress. Urgent pediatric assessment."),
    "child vomiting":             ("YELLOW", "pediatric_icu", "Persistent pediatric vomiting. Assess dehydration."),

    # ---- YELLOW: MODERATE URGENCY → general_ward ----
    "breathing difficulty":   ("YELLOW", "general_ward", "Respiratory distress. Oxygen supplementation and monitoring."),
    "shortness of breath":    ("YELLOW", "general_ward", "Dyspnea requiring assessment. May need oxygen support."),
    "breathlessness":         ("YELLOW", "general_ward", "Breathlessness. Assess oxygen saturation and lung function."),
    "high fever":             ("YELLOW", "general_ward", "High fever requiring investigation. May indicate infection."),
    "persistent vomiting":    ("YELLOW", "general_ward", "Persistent vomiting. Risk of dehydration. IV fluids may be needed."),
    "severe vomiting":        ("YELLOW", "general_ward", "Severe vomiting episode. Antiemetics and observation."),
    "moderate pain":          ("YELLOW", "general_ward", "Moderate pain requiring assessment and management."),
    "severe pain":            ("YELLOW", "general_ward", "Severe pain. Analgesics and diagnostic workup needed."),
    "abdominal pain":         ("YELLOW", "general_ward", "Acute abdominal pain. Needs imaging and assessment."),
    "dehydration":            ("YELLOW", "general_ward", "Dehydration. IV fluid replacement needed."),
    "asthma attack":          ("YELLOW", "general_ward", "Acute asthma exacerbation. Bronchodilators and steroids."),
    "allergic reaction":      ("YELLOW", "general_ward", "Allergic reaction. Antihistamines, monitor for anaphylaxis."),
    "diabetic emergency":     ("YELLOW", "general_ward", "Diabetic crisis. Blood sugar management and monitoring."),
    "fainting":               ("YELLOW", "general_ward", "Syncopal episode. Cardiac and neurological assessment."),
    "blood in urine":         ("YELLOW", "general_ward", "Hematuria. Urological assessment needed."),
    "blood in stool":         ("YELLOW", "general_ward", "GI bleeding. Endoscopic evaluation may be needed."),
    "difficulty swallowing":  ("YELLOW", "general_ward", "Dysphagia. ENT or GI assessment required."),
    "labor pain":             ("YELLOW", "general_ward", "Active labor. Obstetric assessment and delivery preparation."),
    "water broke":            ("YELLOW", "general_ward", "Premature rupture of membranes. Obstetric assessment."),
    "contractions":           ("YELLOW", "general_ward", "Labor contractions. Monitor frequency and prepare for delivery."),

    # ---- GREEN: NON-URGENT → general_ward ----
    "mild fever":       ("GREEN", "general_ward", "Low-grade fever. Rest, fluids, and over-the-counter medication."),
    "low fever":        ("GREEN", "general_ward", "Mild temperature elevation. Monitor and treat symptomatically."),
    "headache":         ("GREEN", "general_ward", "Headache. Analgesics and monitoring. Seek care if worsening."),
    "cold":             ("GREEN", "general_ward", "Common cold. Rest and symptomatic treatment."),
    "runny nose":       ("GREEN", "general_ward", "Upper respiratory symptoms. Symptomatic treatment."),
    "cough":            ("GREEN", "general_ward", "Cough. Monitor for worsening. Antitussives may help."),
    "sore throat":      ("GREEN", "general_ward", "Sore throat. Gargle, lozenges, see GP if persistent."),
    "minor cut":        ("GREEN", "general_ward", "Minor laceration. Clean, apply antiseptic, bandage."),
    "scratch":          ("GREEN", "general_ward", "Superficial scratch. Clean and apply antiseptic."),
    "sprain":           ("GREEN", "general_ward", "Mild sprain. Rest, ice, compression, elevation (RICE)."),
    "muscle pain":      ("GREEN", "general_ward", "Muscular pain. Rest and anti-inflammatory medication."),
    "back pain":        ("GREEN", "general_ward", "Back pain. Rest, analgesics, physiotherapy if needed."),
    "diarrhea":         ("GREEN", "general_ward", "Diarrhea. Oral rehydration. Seek care if bloody or prolonged."),
    "nausea":           ("GREEN", "general_ward", "Nausea. Monitor, rest, antiemetics if needed."),
    "toothache":        ("GREEN", "general_ward", "Dental pain. Analgesics and dental referral."),
    "ear pain":         ("GREEN", "general_ward", "Otalgia. ENT assessment if persistent."),
    "rash":             ("GREEN", "general_ward", "Skin rash. Dermatological assessment if spreading."),
    "insect bite":      ("GREEN", "general_ward", "Insect bite. Clean, antihistamine, monitor for reaction."),
    "eye irritation":   ("GREEN", "general_ward", "Eye irritation. Rinse with clean water, see ophthalmologist."),
}


def classify_symptoms(text):
    """
    Takes a text description of symptoms and returns the urgency level.
    
    How it works:
    1. Convert text to lowercase for matching
    2. Check each keyword against the text (longest keywords first)
    3. Score: RED keywords get 3 points, YELLOW gets 2, GREEN gets 1
    4. Return the highest-scoring severity with its ward recommendation
    
    If no keywords match, defaults to YELLOW (general observation)
    as a safety measure — we never send someone away without care.
    
    Returns a dictionary with:
    - severity: "RED", "YELLOW", or "GREEN"
    - recommended_ward: internal ward key (e.g., "cardiac_icu")
    - ward: display-friendly ward name (e.g., "Cardiac ICU")
    - explanation: plain-English medical reason
    - matched_keywords: list of keywords that matched
    """
    text_lower = (text or "").lower().strip()

    if not text_lower:
        return {
            "severity": "YELLOW",
            "recommended_ward": "general_ward",
            "ward": "General Ward",
            "explanation": "No symptoms provided. Please describe your condition.",
            "reason": "No symptoms provided.",
            "matched_keywords": []
        }

    matched_keywords = []
    best_severity = None
    best_ward = "general_ward"
    best_explanation = "No specific keywords matched. Defaulting to general ward for observation."
    highest_weight = 0

    # Weight map: RED is most critical, GREEN is least
    weight_map = {"RED": 3, "YELLOW": 2, "GREEN": 1}

    # Sort keywords by length (longest first) so "child seizure"
    # matches before "seizure", and "chest tightness" before "chest"
    sorted_keywords = sorted(SYMPTOM_DATABASE.items(), key=lambda x: len(x[0]), reverse=True)

    for keyword, (severity, ward, explanation) in sorted_keywords:
        if keyword in text_lower:
            # Skip if this keyword is a substring of an already matched longer keyword
            # e.g., "seizure" when "child seizure" was already matched
            if any(keyword in prev for prev in matched_keywords):
                continue

            matched_keywords.append(keyword)
            weight = weight_map.get(severity, 0)

            if weight > highest_weight:
                highest_weight = weight
                best_severity = severity
                best_ward = ward
                best_explanation = explanation

    # Default to YELLOW if nothing matched (safety measure)
    if best_severity is None:
        best_severity = "YELLOW"

    # Create display-friendly ward name
    ward_display_names = {
        "cardiac_icu": "Cardiac ICU",
        "adult_icu": "Adult ICU",
        "pediatric_icu": "Pediatric ICU",
        "general_ward": "General Ward"
    }
    ward_display = ward_display_names.get(best_ward, "General Ward")

    return {
        "severity": best_severity,
        "recommended_ward": best_ward,
        "ward": ward_display,
        "explanation": best_explanation,
        "reason": best_explanation,         # Alias for frontend compatibility
        "matched_keywords": matched_keywords
    }
