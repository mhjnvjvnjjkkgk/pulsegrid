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
# SYMPTOM DATABASE  (200+ entries)
# Each keyword maps to: (severity, ward_type, explanation)
#
# Keywords are searched inside the patient's text description.
# Longer keywords are checked FIRST so "child seizure" matches
# before "seizure" alone.
# ============================================================

SYMPTOM_DATABASE = {
    # ---- RED: CARDIAC EMERGENCIES → cardiac_icu ----
    "cardiac arrest":          ("RED", "cardiac_icu", "Possible cardiac arrest. Immediate CPR and defibrillation required."),
    "heart attack":            ("RED", "cardiac_icu", "Suspected myocardial infarction. Needs immediate cardiac intervention."),
    "heart stopped":           ("RED", "cardiac_icu", "Possible cardiac arrest. Immediate CPR required."),
    "chest pain":              ("RED", "cardiac_icu", "Acute chest pain may indicate cardiac event. Urgent ECG required."),
    "chest tightness":         ("RED", "cardiac_icu", "Chest tightness with possible cardiac origin. Needs monitoring."),
    "chest pressure":          ("RED", "cardiac_icu", "Chest pressure — possible angina or MI. Urgent cardiac evaluation."),
    "crushing chest":          ("RED", "cardiac_icu", "Crushing chest sensation — high suspicion for MI. Emergency response needed."),
    "palpitations":            ("RED", "cardiac_icu", "Severe palpitations may indicate arrhythmia. Cardiac monitoring needed."),
    "heart racing":            ("RED", "cardiac_icu", "Tachycardia detected. Cardiac monitoring and ECG required."),
    "heart pounding":          ("RED", "cardiac_icu", "Possible arrhythmia or hypertensive crisis. Urgent evaluation."),
    "irregular heartbeat":     ("RED", "cardiac_icu", "Arrhythmia suspected. Requires ECG and cardiac monitoring."),
    "skipped heartbeat":       ("RED", "cardiac_icu", "Possible arrhythmia. Cardiac assessment needed."),
    "angina":                  ("RED", "cardiac_icu", "Angina episode. Needs nitroglycerin and cardiac evaluation."),
    "left arm pain":           ("RED", "cardiac_icu", "Left arm pain with possible cardiac origin. Rule out MI urgently."),
    "jaw pain":                ("RED", "cardiac_icu", "Jaw pain can be referred cardiac pain. Rule out MI."),

    # ---- RED: NEUROLOGICAL / RESPIRATORY → adult_icu ----
    "not breathing":           ("RED", "adult_icu", "Respiratory arrest. Immediate airway management required."),
    "stopped breathing":       ("RED", "adult_icu", "Respiratory failure. Urgent ventilator support needed."),
    "cannot breathe":          ("RED", "adult_icu", "Respiratory failure. Emergency airway management needed."),
    "no breathing":            ("RED", "adult_icu", "Apnea detected. Immediate resuscitation required."),
    "gasping":                 ("RED", "adult_icu", "Agonal breathing or severe hypoxia. Urgent airway intervention."),
    "unconscious":             ("RED", "adult_icu", "Patient unconscious. Assess airway, breathing, circulation."),
    "unresponsive":            ("RED", "adult_icu", "Unresponsive patient. Full trauma and neuro assessment needed."),
    "not responding":          ("RED", "adult_icu", "Patient unresponsive. Emergency evaluation required."),
    "passed out":              ("RED", "adult_icu", "Loss of consciousness. Assess for cardiac, neuro, metabolic causes."),
    "collapsed":               ("RED", "adult_icu", "Collapse — assess for cardiac arrest, stroke, hypoglycaemia."),
    "seizure":                 ("RED", "adult_icu", "Active seizure. Anti-epileptic medication and monitoring required."),
    "convulsion":              ("RED", "adult_icu", "Convulsive episode. Protect airway, administer anti-epileptics."),
    "fits":                    ("RED", "adult_icu", "Epileptic fit. Protect airway, administer anti-epileptics."),
    "epilepsy attack":         ("RED", "adult_icu", "Epileptic seizure. Airway protection and anti-epileptic therapy needed."),
    "stroke":                  ("RED", "adult_icu", "Suspected stroke. CT scan and thrombolysis evaluation needed."),
    "brain attack":            ("RED", "adult_icu", "Suspected stroke. Urgent CT and thrombolysis assessment."),
    "face drooping":           ("RED", "adult_icu", "Facial droop — FAST stroke sign. Urgent CT scan."),
    "slurred speech":          ("RED", "adult_icu", "Slurred speech — possible stroke or TIA. Urgent neuro evaluation."),
    "can't speak":             ("RED", "adult_icu", "Aphasia — possible stroke. Urgent CT and neuro assessment."),
    "sudden confusion":        ("RED", "adult_icu", "Acute confusion — possible stroke, sepsis or metabolic emergency."),
    "paralysis":               ("RED", "adult_icu", "Sudden paralysis may indicate stroke or spinal injury."),
    "arm weakness":            ("RED", "adult_icu", "Arm weakness — FAST stroke sign. Urgent CT scan required."),
    "leg weakness":            ("RED", "adult_icu", "Leg weakness — possible stroke or spinal emergency."),
    "choking":                 ("RED", "adult_icu", "Airway obstruction. Heimlich maneuver and emergency care needed."),
    "swallowed something":     ("RED", "adult_icu", "Possible airway foreign body. Immediate ENT/airway evaluation."),
    "anaphylaxis":             ("RED", "adult_icu", "Anaphylactic shock. Epinephrine immediately, airway support."),
    "anaphylactic":            ("RED", "adult_icu", "Anaphylactic reaction. Epinephrine and emergency monitoring."),
    "severe allergy":          ("RED", "adult_icu", "Severe allergic reaction — monitor for anaphylaxis."),
    "throat swelling":         ("RED", "adult_icu", "Angioedema or anaphylaxis. Airway at risk — emergency care."),
    "tongue swelling":         ("RED", "adult_icu", "Tongue swelling — airway compromise risk. Emergency care."),
    "worst headache":          ("RED", "adult_icu", "Thunderclap headache — urgent CT to rule out SAH."),

    # ---- RED: TRAUMA / INJURY → adult_icu ----
    "severe bleeding":         ("RED", "adult_icu", "Severe hemorrhage. Immediate pressure and transfusion may be needed."),
    "heavy bleeding":          ("RED", "adult_icu", "Major blood loss. Urgent surgical intervention likely."),
    "bleeding a lot":          ("RED", "adult_icu", "Significant hemorrhage. Apply pressure, urgent surgical review."),
    "blood pouring":           ("RED", "adult_icu", "Active hemorrhage. Immediate tourniquet or direct pressure."),
    "gunshot":                 ("RED", "adult_icu", "Gunshot wound. Trauma surgery required immediately."),
    "bullet wound":            ("RED", "adult_icu", "Penetrating ballistic trauma. Emergency surgery."),
    "stab wound":              ("RED", "adult_icu", "Penetrating trauma. Emergency surgical assessment needed."),
    "stabbed":                 ("RED", "adult_icu", "Stab injury — penetrating trauma. Emergency surgical care."),
    "knife wound":             ("RED", "adult_icu", "Knife injury with penetrating trauma. Urgent surgical review."),
    "road accident":           ("RED", "adult_icu", "Road traffic accident victim. Full trauma workup required."),
    "car accident":            ("RED", "adult_icu", "Motor vehicle accident. Assess for internal injuries."),
    "bike accident":           ("RED", "adult_icu", "Motorcycle accident. Trauma assessment and imaging needed."),
    "hit by vehicle":          ("RED", "adult_icu", "Pedestrian struck — high-energy trauma. Full assessment."),
    "run over":                ("RED", "adult_icu", "High-energy trauma. Emergency trauma workup."),
    "major fracture":          ("RED", "adult_icu", "Major bone fracture. Ortho assessment and possible surgery."),
    "compound fracture":       ("RED", "adult_icu", "Open fracture with bone exposure. Surgery required."),
    "bone sticking out":       ("RED", "adult_icu", "Open fracture — orthopedic emergency."),
    "head injury":             ("RED", "adult_icu", "Traumatic head injury. CT scan and neuro monitoring needed."),
    "head trauma":             ("RED", "adult_icu", "Head trauma. Neurosurgical and CT evaluation required."),
    "skull fracture":          ("RED", "adult_icu", "Skull fracture — neurosurgical emergency."),
    "crush injury":            ("RED", "adult_icu", "Crush injury. Risk of rhabdomyolysis and renal failure."),
    "fall from height":        ("RED", "adult_icu", "Fall from height. Spinal precautions and full assessment."),
    "fell from roof":          ("RED", "adult_icu", "High fall — spinal and internal injury risk. Full trauma care."),
    "electrocution":           ("RED", "adult_icu", "Electrical injury. Cardiac monitoring required."),
    "electric shock":          ("RED", "adult_icu", "Electric shock. Cardiac and burn assessment needed."),
    "drowning":                ("RED", "adult_icu", "Near-drowning. Airway management and pulmonary assessment."),
    "near drowning":           ("RED", "adult_icu", "Near-drowning. Respiratory and metabolic assessment."),
    "burn":                    ("RED", "adult_icu", "Severe burn injury. Fluid resuscitation and burn care needed."),
    "fire burn":               ("RED", "adult_icu", "Burns from fire. Fluid resuscitation and wound care."),
    "acid burn":               ("RED", "adult_icu", "Chemical burn. Flush with water, urgent surgical review."),

    # ---- RED: MATERNITY EMERGENCIES → adult_icu ----
    "eclampsia":               ("RED", "adult_icu", "Eclampsia with seizures. Magnesium sulfate and delivery needed."),
    "hemorrhage postpartum":   ("RED", "adult_icu", "Postpartum hemorrhage. Urgent uterotonic and possible surgery."),
    "postpartum bleeding":     ("RED", "adult_icu", "Postpartum hemorrhage — potentially life-threatening."),
    "placenta abruption":      ("RED", "adult_icu", "Placental abruption. Emergency caesarean may be needed."),
    "ectopic pregnancy":       ("RED", "adult_icu", "Ruptured ectopic pregnancy. Emergency surgery required."),
    "pregnancy bleeding":      ("RED", "adult_icu", "Antepartum haemorrhage — urgent obstetric assessment."),
    "miscarriage bleeding":    ("RED", "adult_icu", "Heavy bleeding in pregnancy. Urgent obstetric care."),
    "vomiting blood":          ("RED", "adult_icu", "Haematemesis — upper GI bleed. Urgent endoscopy."),
    "blood in vomit":          ("RED", "adult_icu", "Upper GI bleeding. Urgent endoscopic evaluation."),
    "bloody stool":            ("RED", "adult_icu", "PR bleeding — lower GI bleed. Urgent surgical assessment."),
    "black stool":             ("RED", "adult_icu", "Melaena — upper GI bleed. Urgent endoscopy."),

    # ---- RED: POISONING & BITES ----
    "overdose":                ("RED", "adult_icu", "Drug overdose. Airway, antidote, and monitoring required."),
    "drug overdose":           ("RED", "adult_icu", "Substance overdose. Naloxone if opioid, urgent ICU care."),
    "poison":                  ("RED", "adult_icu", "Poisoning. Identify substance, gastric lavage, antidote if available."),
    "poisoned":                ("RED", "adult_icu", "Toxic ingestion. Emergency toxicology and antidote therapy."),
    "rat poison":              ("RED", "adult_icu", "Rodenticide ingestion. Vitamin K and monitoring."),
    "insecticide":             ("RED", "adult_icu", "Organophosphate poisoning. Atropine and pralidoxime."),
    "snake bite":              ("RED", "adult_icu", "Envenomation. Antivenom and monitoring for coagulopathy."),

    # ---- YELLOW: PEDIATRIC EMERGENCIES → pediatric_icu ----
    "child breathing difficulty": ("YELLOW", "pediatric_icu", "Pediatric respiratory distress. Nebulization and monitoring."),
    "child seizure":              ("YELLOW", "pediatric_icu", "Pediatric seizure. Anti-epileptic and fever management."),
    "child convulsion":           ("YELLOW", "pediatric_icu", "Pediatric convulsion. Protect airway, anti-epileptic therapy."),
    "child high fever":           ("YELLOW", "pediatric_icu", "Pediatric high fever. Antipyretics and workup needed."),
    "child not eating":           ("YELLOW", "pediatric_icu", "Paediatric feeding failure. Assess for dehydration."),
    "infant not feeding":         ("YELLOW", "pediatric_icu", "Infant feeding failure. Assess for dehydration and infection."),
    "baby not breathing well":    ("YELLOW", "pediatric_icu", "Neonatal respiratory distress. Urgent pediatric assessment."),
    "newborn not breathing":      ("YELLOW", "pediatric_icu", "Neonatal apnea — urgent resuscitation and NICU."),
    "child vomiting":             ("YELLOW", "pediatric_icu", "Persistent pediatric vomiting. Assess dehydration."),
    "baby crying":                ("YELLOW", "pediatric_icu", "Inconsolable infant. Assess for pain, infection, bowel obstruction."),
    "child fell":                 ("YELLOW", "pediatric_icu", "Paediatric fall — assess for fracture and head injury."),
    "child not waking":           ("YELLOW", "pediatric_icu", "Altered consciousness in child. Urgent paediatric assessment."),
    "baby fever":                 ("YELLOW", "pediatric_icu", "Infant fever — sepsis risk. Urgent paediatric workup."),

    # ---- YELLOW: GASTROINTESTINAL ----
    "stomach pain":            ("YELLOW", "general_ward", "Acute abdominal pain. Assessment and imaging required."),
    "stomach ache":            ("YELLOW", "general_ward", "Abdominal pain requiring assessment and management."),
    "tummy pain":              ("YELLOW", "general_ward", "Abdominal pain. Clinical assessment and imaging if needed."),
    "belly pain":              ("YELLOW", "general_ward", "Abdominal pain. Assessment for surgical or GI cause."),
    "abdominal pain":          ("YELLOW", "general_ward", "Acute abdominal pain. Needs imaging and assessment."),
    "abdomen pain":            ("YELLOW", "general_ward", "Abdominal pain. Rule out appendicitis, obstruction."),
    "stomach cramps":          ("YELLOW", "general_ward", "Abdominal cramps. Assess for infection, obstruction."),
    "severe cramps":           ("YELLOW", "general_ward", "Severe abdominal cramps. Clinical evaluation needed."),
    "appendix pain":           ("YELLOW", "general_ward", "Right iliac fossa pain — rule out appendicitis urgently."),
    "right side pain":         ("YELLOW", "general_ward", "Right-sided pain — assess for appendicitis or renal colic."),
    "kidney pain":             ("YELLOW", "general_ward", "Flank pain — renal colic or infection. Assessment needed."),
    "kidney stone":            ("YELLOW", "general_ward", "Renal colic. Analgesia and urology assessment."),
    "gallstone":               ("YELLOW", "general_ward", "Biliary colic — assess for cholecystitis. Surgical review."),
    "vomiting":                ("YELLOW", "general_ward", "Vomiting. Assess for dehydration, cause. IV fluids if needed."),
    "throwing up":             ("YELLOW", "general_ward", "Vomiting. Assess for dehydration and underlying cause."),
    "puking":                  ("YELLOW", "general_ward", "Vomiting. Antiemetics and fluid assessment."),
    "can't keep food down":    ("YELLOW", "general_ward", "Persistent vomiting. IV fluids and antiemetics needed."),
    "persistent vomiting":     ("YELLOW", "general_ward", "Persistent vomiting. Risk of dehydration. IV fluids needed."),
    "severe vomiting":         ("YELLOW", "general_ward", "Severe vomiting episode. Antiemetics and observation."),
    "food poisoning":          ("YELLOW", "general_ward", "Food poisoning. Rehydration and supportive care."),
    "diarrhea":                ("YELLOW", "general_ward", "Diarrhea. Oral rehydration. Seek care if bloody or prolonged."),
    "diarrhoea":               ("YELLOW", "general_ward", "Diarrhoea. Oral rehydration and electrolyte replacement."),
    "loose motions":           ("YELLOW", "general_ward", "Loose stool. Oral rehydration and electrolyte replacement."),
    "loose stool":             ("YELLOW", "general_ward", "Diarrhoea. Oral rehydration and assessment if persistent."),
    "watery stool":            ("YELLOW", "general_ward", "Watery diarrhoea — assess for cholera or severe gastroenteritis."),
    "blood in stool":          ("YELLOW", "general_ward", "GI bleeding. Endoscopic evaluation may be needed."),
    "blood in urine":          ("YELLOW", "general_ward", "Hematuria. Urological assessment needed."),

    # ---- YELLOW: NEUROLOGICAL / GENERAL ----
    "dizziness":               ("YELLOW", "general_ward", "Dizziness. Assess for vertigo, cardiac, or metabolic cause."),
    "dizzy":                   ("YELLOW", "general_ward", "Dizziness. Vital signs, blood sugar, and cardiac check needed."),
    "vertigo":                 ("YELLOW", "general_ward", "Vertigo. ENT or neurological assessment needed."),
    "lightheaded":             ("YELLOW", "general_ward", "Lightheadedness. Assess for hypotension or dehydration."),
    "feeling faint":           ("YELLOW", "general_ward", "Pre-syncope. Assess for cardiac or metabolic cause."),
    "about to faint":          ("YELLOW", "general_ward", "Pre-syncopal symptoms. Lie flat, check vitals."),
    "blackout":                ("YELLOW", "general_ward", "Loss of consciousness. Cardiac and neurological assessment."),
    "blacked out":             ("YELLOW", "general_ward", "Syncopal episode. Cardiac and neurological workup."),
    "fainting":                ("YELLOW", "general_ward", "Syncopal episode. Cardiac and neurological assessment."),
    "fainted":                 ("YELLOW", "general_ward", "Syncope. Assess for cardiac, neuro, or metabolic cause."),
    "weakness":                ("YELLOW", "general_ward", "Generalised weakness. Assess for sepsis, metabolic, or neuro cause."),
    "feeling weak":            ("YELLOW", "general_ward", "Weakness. Blood tests and clinical assessment required."),
    "body weakness":           ("YELLOW", "general_ward", "General body weakness. Rule out sepsis, electrolyte imbalance."),
    "fatigue":                 ("YELLOW", "general_ward", "Severe fatigue. Assess for anaemia, infection, or cardiac cause."),
    "extreme tiredness":       ("YELLOW", "general_ward", "Extreme fatigue. Investigation for systemic cause."),
    "confusion":               ("YELLOW", "adult_icu", "Acute confusion. Assess for sepsis, stroke, or metabolic cause."),
    "disoriented":             ("YELLOW", "adult_icu", "Disorientation. Neuro and metabolic assessment."),
    "memory loss":             ("YELLOW", "adult_icu", "Acute memory loss. Neurological assessment required."),
    "loss of balance":         ("YELLOW", "adult_icu", "Ataxia. Cerebellar or vestibular assessment."),
    "severe headache":         ("YELLOW", "adult_icu", "Severe headache — rule out subarachnoid haemorrhage urgently."),
    "sudden headache":         ("YELLOW", "adult_icu", "Sudden severe headache. CT scan to rule out intracranial bleed."),
    "stiff neck":              ("YELLOW", "adult_icu", "Stiff neck with fever — rule out meningitis urgently."),
    "blurred vision":          ("YELLOW", "general_ward", "Blurred vision — assess for retinal, neuro or metabolic cause."),
    "eye bleeding":            ("YELLOW", "adult_icu", "Eye haemorrhage — ophthalmologic emergency."),

    # ---- YELLOW: RESPIRATORY ----
    "breathing difficulty":    ("YELLOW", "general_ward", "Respiratory distress. Oxygen supplementation and monitoring."),
    "shortness of breath":     ("YELLOW", "general_ward", "Dyspnea requiring assessment. May need oxygen support."),
    "breathlessness":          ("YELLOW", "general_ward", "Breathlessness. Assess oxygen saturation and lung function."),
    "breathing problem":       ("YELLOW", "general_ward", "Respiratory issue. Oxygen and clinical assessment."),
    "can't breathe properly":  ("YELLOW", "general_ward", "Respiratory distress. Oxygen and monitoring needed."),
    "cant breathe":            ("YELLOW", "general_ward", "Respiratory distress. Oxygen support needed."),
    "wheezing":                ("YELLOW", "general_ward", "Wheezing — possible asthma or airway obstruction. Bronchodilators."),
    "asthma attack":           ("YELLOW", "general_ward", "Acute asthma exacerbation. Bronchodilators and steroids."),
    "asthma":                  ("YELLOW", "general_ward", "Asthma exacerbation. Salbutamol nebulisation and steroids."),
    "pneumonia":               ("YELLOW", "general_ward", "Suspected pneumonia. Chest X-ray, antibiotics, oxygen."),
    "tuberculosis":            ("YELLOW", "general_ward", "TB symptoms. Sputum smear and infectious disease workup."),

    # ---- YELLOW: METABOLIC / SYSTEMIC ----
    "high fever":              ("YELLOW", "general_ward", "High fever requiring investigation. May indicate infection."),
    "very high temperature":   ("YELLOW", "general_ward", "High temperature. Antipyretics and workup for infection."),
    "temperature 103":         ("YELLOW", "general_ward", "High fever. Antipyretics, investigation for infection source."),
    "temperature 104":         ("YELLOW", "adult_icu", "Very high fever — risk of febrile convulsion. Urgent cooling."),
    "fever with rash":         ("YELLOW", "general_ward", "Fever with rash — assess for dengue, meningitis, drug reaction."),
    "dengue":                  ("YELLOW", "general_ward", "Suspected dengue. CBC, platelets, and supportive care."),
    "malaria":                 ("YELLOW", "general_ward", "Suspected malaria. Smear and antimalarial therapy."),
    "typhoid":                 ("YELLOW", "general_ward", "Typhoid fever. Blood culture and antibiotic therapy."),
    "dehydration":             ("YELLOW", "general_ward", "Dehydration. IV fluid replacement needed."),
    "not passing urine":       ("YELLOW", "general_ward", "Urinary retention — assess for obstruction or renal failure."),
    "no urine":                ("YELLOW", "adult_icu", "Anuria — renal failure risk. Urgent nephrology assessment."),
    "diabetic emergency":      ("YELLOW", "general_ward", "Diabetic crisis. Blood sugar management and monitoring."),
    "blood sugar high":        ("YELLOW", "general_ward", "Hyperglycaemia. Insulin and fluid management."),
    "blood sugar low":         ("YELLOW", "general_ward", "Hypoglycaemia. Oral glucose or IV dextrose."),
    "sugar crash":             ("YELLOW", "general_ward", "Hypoglycaemia — give oral glucose. Monitor blood sugar."),
    "diabetes problem":        ("YELLOW", "general_ward", "Diabetic emergency. Blood glucose check and management."),
    "jaundice":                ("YELLOW", "general_ward", "Jaundice. Liver function tests and hepatology review."),
    "yellow skin":             ("YELLOW", "general_ward", "Jaundice — assess for hepatitis or biliary obstruction."),
    "yellow eyes":             ("YELLOW", "general_ward", "Icterus — liver disease assessment."),

    # ---- YELLOW: PAIN ----
    "severe pain":             ("YELLOW", "general_ward", "Severe pain. Analgesics and diagnostic workup needed."),
    "moderate pain":           ("YELLOW", "general_ward", "Moderate pain requiring assessment and management."),
    "unbearable pain":         ("YELLOW", "general_ward", "Severe pain. Analgesics and urgent workup."),
    "chest discomfort":        ("YELLOW", "general_ward", "Chest discomfort. Rule out cardiac and respiratory causes."),
    "difficulty swallowing":   ("YELLOW", "general_ward", "Dysphagia. ENT or GI assessment required."),
    "cannot swallow":          ("YELLOW", "general_ward", "Dysphagia. ENT assessment for obstruction."),

    # ---- YELLOW: OBSTETRIC ----
    "labor pain":              ("YELLOW", "general_ward", "Active labor. Obstetric assessment and delivery preparation."),
    "water broke":             ("YELLOW", "general_ward", "Premature rupture of membranes. Obstetric assessment."),
    "contractions":            ("YELLOW", "general_ward", "Labor contractions. Monitor frequency and prepare for delivery."),
    "baby coming":             ("YELLOW", "general_ward", "Imminent delivery. Obstetric team required urgently."),
    "in labor":                ("YELLOW", "general_ward", "Active labor. Obstetric assessment and delivery preparation."),
    "miscarriage":             ("YELLOW", "general_ward", "Miscarriage — obstetric assessment and ultrasound."),
    "heavy period":            ("YELLOW", "general_ward", "Menorrhagia — gynaecological assessment and haemoglobin check."),

    # ---- YELLOW: MENTAL HEALTH ----
    "anxiety attack":          ("YELLOW", "general_ward", "Anxiety/panic attack. Calm environment, reassurance, vital signs."),
    "panic attack":            ("YELLOW", "general_ward", "Panic attack. Reassurance and monitoring. Rule out cardiac cause."),
    "suicidal":                ("YELLOW", "adult_icu", "Suicidal ideation. Psychiatric assessment and crisis support."),
    "self harm":               ("YELLOW", "adult_icu", "Self-harm — wound care and urgent psychiatric review."),
    "mental breakdown":        ("YELLOW", "general_ward", "Mental health crisis. Psychiatric assessment and support."),

    # ---- YELLOW: ALLERGY / SKIN ----
    "allergic reaction":       ("YELLOW", "general_ward", "Allergic reaction. Antihistamines, monitor for anaphylaxis."),
    "dog bite":                ("YELLOW", "adult_icu", "Animal bite — rabies risk. Wound care, rabies prophylaxis."),
    "animal bite":             ("YELLOW", "adult_icu", "Animal bite — rabies risk. Wound care and prophylaxis."),
    "swelling":                ("YELLOW", "general_ward", "Swelling — assess for allergy, DVT or inflammatory cause."),
    "joint swelling":          ("YELLOW", "general_ward", "Joint swelling — assess for infection, gout or injury."),
    "knee swelling":           ("YELLOW", "general_ward", "Knee swelling — assess for fracture, ligament or infection."),
    "eye swelling":            ("YELLOW", "general_ward", "Periorbital swelling — assess for allergy or cellulitis."),

    # ---- YELLOW: ORTHOPEDIC ----
    "broken bone":             ("YELLOW", "general_ward", "Suspected fracture. X-ray and orthopaedic assessment."),
    "fracture":                ("YELLOW", "general_ward", "Fracture suspected. X-ray and orthopaedic review."),
    "dislocated":              ("YELLOW", "general_ward", "Dislocation. Orthopaedic reduction and assessment."),
    "twisted ankle":           ("YELLOW", "general_ward", "Ankle sprain or fracture. X-ray and orthopaedic review."),
    "fell down":               ("YELLOW", "general_ward", "Fall — assess for fracture and head injury."),
    "hip pain":                ("YELLOW", "general_ward", "Hip pain — assess for fracture, especially in elderly."),
    "knee pain":               ("YELLOW", "general_ward", "Knee pain — assess for fracture or soft tissue injury."),
    "shoulder pain":           ("YELLOW", "general_ward", "Shoulder pain — assess for dislocation or fracture."),

    # ---- GREEN: NON-URGENT → general_ward ----
    "mild fever":              ("GREEN", "general_ward", "Low-grade fever. Rest, fluids, and over-the-counter medication."),
    "low fever":               ("GREEN", "general_ward", "Mild temperature elevation. Monitor and treat symptomatically."),
    "fever":                   ("GREEN", "general_ward", "Fever. Antipyretics and assessment if persisting."),
    "temperature":             ("GREEN", "general_ward", "Elevated temperature. Antipyretics and monitoring."),
    "headache":                ("GREEN", "general_ward", "Headache. Analgesics and monitoring. Seek care if worsening."),
    "migraine":                ("GREEN", "general_ward", "Migraine. Analgesics, dark rest, anti-emetics if needed."),
    "cold":                    ("GREEN", "general_ward", "Common cold. Rest and symptomatic treatment."),
    "runny nose":              ("GREEN", "general_ward", "Upper respiratory symptoms. Symptomatic treatment."),
    "blocked nose":            ("GREEN", "general_ward", "Nasal congestion. Decongestants and steam inhalation."),
    "sneezing":                ("GREEN", "general_ward", "Sneezing — likely allergic rhinitis or cold."),
    "cough":                   ("GREEN", "general_ward", "Cough. Monitor for worsening. Antitussives may help."),
    "dry cough":               ("GREEN", "general_ward", "Dry cough. Honey, lozenges; see GP if persisting >3 weeks."),
    "sore throat":             ("GREEN", "general_ward", "Sore throat. Gargle, lozenges, see GP if persistent."),
    "throat pain":             ("GREEN", "general_ward", "Pharyngitis. Salt water gargle and analgesics."),
    "minor cut":               ("GREEN", "general_ward", "Minor laceration. Clean, apply antiseptic, bandage."),
    "scratch":                 ("GREEN", "general_ward", "Superficial scratch. Clean and apply antiseptic."),
    "sprain":                  ("GREEN", "general_ward", "Mild sprain. Rest, ice, compression, elevation (RICE)."),
    "muscle pain":             ("GREEN", "general_ward", "Muscular pain. Rest and anti-inflammatory medication."),
    "muscle cramp":            ("GREEN", "general_ward", "Muscle cramp. Stretch, hydrate, magnesium if recurring."),
    "back pain":               ("GREEN", "general_ward", "Back pain. Rest, analgesics, physiotherapy if needed."),
    "nausea":                  ("GREEN", "general_ward", "Nausea. Monitor, rest, antiemetics if needed."),
    "feeling sick":            ("GREEN", "general_ward", "Nausea. Rest, hydration, antiemetics if needed."),
    "toothache":               ("GREEN", "general_ward", "Dental pain. Analgesics and dental referral."),
    "tooth pain":              ("GREEN", "general_ward", "Toothache. Analgesics and emergency dental review."),
    "ear pain":                ("GREEN", "general_ward", "Otalgia. ENT assessment if persistent."),
    "earache":                 ("GREEN", "general_ward", "Ear pain — possible otitis. ENT review."),
    "rash":                    ("GREEN", "general_ward", "Skin rash. Dermatological assessment if spreading."),
    "skin rash":               ("GREEN", "general_ward", "Rash. Dermatological assessment and antihistamines."),
    "itching":                 ("GREEN", "general_ward", "Pruritus. Antihistamines and dermatological review."),
    "insect bite":             ("GREEN", "general_ward", "Insect bite. Clean, antihistamine, monitor for reaction."),
    "eye irritation":          ("GREEN", "general_ward", "Eye irritation. Rinse with clean water, see ophthalmologist."),
    "red eye":                 ("GREEN", "general_ward", "Conjunctivitis. Eye drops and review if not improving."),
    "neck pain":               ("GREEN", "general_ward", "Neck pain. Analgesics, physiotherapy if chronic."),
    "constipation":            ("GREEN", "general_ward", "Constipation. Laxatives, hydration, diet modification."),
    "bloating":                ("GREEN", "general_ward", "Abdominal bloating. Diet assessment and symptomatic treatment."),
    "gas pain":                ("GREEN", "general_ward", "Flatulence and gas pain. Antiflatulents and dietary advice."),
    "indigestion":             ("GREEN", "general_ward", "Indigestion. Antacids and dietary modification."),
    "acidity":                 ("GREEN", "general_ward", "Acid reflux. Antacids, avoid trigger foods, see GP if persistent."),
    "heartburn":               ("GREEN", "general_ward", "Heartburn. Antacids and dietary advice."),
    "period pain":             ("GREEN", "general_ward", "Dysmenorrhoea. Analgesics and gynaecological review if severe."),
    "urine pain":              ("GREEN", "general_ward", "Dysuria — possible UTI. Urine culture and antibiotics."),
    "burning urination":       ("GREEN", "general_ward", "UTI symptoms. Urine analysis and antibiotic therapy."),
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
    best_explanation = "Symptoms noted. Recommend general ward assessment."
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
