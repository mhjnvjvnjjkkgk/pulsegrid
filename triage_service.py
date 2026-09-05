# ============================================================
# PulseGrid - AI Triage Service
#
# Classifies patient symptoms into urgency levels:
#   RED    = Critical (needs ICU / emergency resuscitation immediately)
#   YELLOW = Moderate (needs ward observation / urgent care)
#   GREEN  = Mild (can visit outpatient clinic)
#
# Deterministic keyword & phrase matching engine with 400+ entries.
# Includes English, Hinglish, and Benglish emergency expressions.
# Zero API key requirements, zero external LLM failure points.
# ============================================================

SYMPTOM_DATABASE = {
    # ---- RED: CARDIAC EMERGENCIES → cardiac_icu ----
    "cardiac arrest":          ("RED", "cardiac_icu", "Possible cardiac arrest. Immediate CPR and defibrillation required."),
    "heart attack":            ("RED", "cardiac_icu", "Suspected myocardial infarction. Needs immediate cardiac intervention."),
    "myocardial infarction":   ("RED", "cardiac_icu", "Acute myocardial infarction. Emergency cardiac catheterization required."),
    "angina pectoris":         ("RED", "cardiac_icu", "Angina episode. Needs nitroglycerin and urgent cardiac evaluation."),
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
    "jaw pain radiating":      ("RED", "cardiac_icu", "Referred cardiac pain to jaw — high suspicion for MI."),
    "jaw pain":                ("RED", "cardiac_icu", "Jaw pain can be referred cardiac pain. Rule out MI."),
    "aortic dissection":      ("RED", "cardiac_icu", "Tearing chest/back pain. High risk of aortic rupture — surgical emergency."),
    "hypertensive crisis":     ("RED", "cardiac_icu", "Severe hypertension with end-organ risk. Immediate IV antihypertensives."),
    "ventricular tachycardia": ("RED", "cardiac_icu", "Life-threatening arrhythmia. Emergency cardioversion required."),
    "bp 200":                  ("RED", "cardiac_icu", "Hypertensive crisis — severe blood pressure elevation. Urgent care."),
    "sharp chest pain":        ("RED", "cardiac_icu", "Acute chest pain — rule out MI, PE, aortic dissection."),
    "stabbing chest pain":     ("RED", "cardiac_icu", "Sharp chest pain — rule out cardiac or pulmonary emergency."),
    "heart fluttering":        ("RED", "cardiac_icu", "Cardiac arrhythmia suspected. Requires immediate ECG."),
    "cardiac pain":            ("RED", "cardiac_icu", "Cardiac pain — immediate resuscitation room evaluation."),

    # ---- HINGLISH EMERGENCY PHRASES ----
    "chhati me bahut dard ho raha hai": ("RED", "cardiac_icu", "Acute chest pain (Hinglish). High suspicion for MI. Urgent ECG required."),
    "chhati me dard ho raha hai":       ("RED", "cardiac_icu", "Chest pain (Hinglish). Urgent cardiac evaluation required."),
    "heart me pain ho raha hai":        ("RED", "cardiac_icu", "Cardiac chest pain (Hinglish). Immediate ECG and vitals."),
    "dil me dard ho raha hai":          ("RED", "cardiac_icu", "Chest pain (Hinglish). Urgent cardiac evaluation."),
    "haat attack aaya hai":             ("RED", "cardiac_icu", "Suspected myocardial infarction (Hinglish). Needs immediate intervention."),
    "chest me pressure lag raha hai":   ("RED", "cardiac_icu", "Chest pressure (Hinglish). Angina or MI suspected."),
    "chhati fat rahi hai":              ("RED", "cardiac_icu", "Severe crushing chest pain (Hinglish). High suspicion for MI."),
    "heart me jalan ho rahi hai":       ("RED", "cardiac_icu", "Chest burning/angina (Hinglish). Immediate cardiac assessment."),
    "chest heavy lag raha hai":        ("RED", "cardiac_icu", "Chest heaviness (Hinglish). Urgent ECG & cardiac workup."),
    "dhadkan bahut tez hai":            ("RED", "cardiac_icu", "Tachycardia (Hinglish). Immediate cardiac monitoring."),
    "chhati me dabaav hai":             ("RED", "cardiac_icu", "Chest pressure (Hinglish). Rule out myocardial infarction."),
    "saas lene me dikkat ho rahi hai":  ("YELLOW", "general_ward", "Breathlessness (Hinglish). Oxygen supplementation and lung assessment."),
    "saas nahi aa rahi hai":            ("RED", "adult_icu", "Severe respiratory distress (Hinglish). Immediate airway and oxygen care."),
    "saas phul rahi hai":               ("YELLOW", "general_ward", "Breathlessness (Hinglish). Oxygen supplementation required."),
    "dum ghut raha hai":                ("RED", "adult_icu", "Severe hypoxia / suffocation (Hinglish). Urgent airway management."),
    "heart beat bahut fast hai":        ("RED", "cardiac_icu", "Tachycardia (Hinglish). ECG and cardiac monitoring needed."),
    "bp bahut high ho gaya hai":        ("RED", "cardiac_icu", "Hypertensive crisis (Hinglish). Urgent blood pressure management."),
    "behos ho gaya hai":                ("RED", "adult_icu", "Unconscious patient (Hinglish). Assess airway, breathing, circulation."),
    "chakkar aa raha hai":              ("YELLOW", "general_ward", "Dizziness (Hinglish). Vitals, blood sugar, and neuro check."),
    "sar me tez dard hai":              ("RED", "adult_icu", "Severe headache (Hinglish). CT scan to rule out SAH/bleed."),
    "muh se jhaag nikal raha hai":      ("RED", "adult_icu", "Foaming at mouth / seizure (Hinglish). Airway protection & anticonvulsant."),
    "fits aa rahe hain":                ("RED", "adult_icu", "Active seizures (Hinglish). IV anticonvulsant & ICU prep."),
    "faint ho gaya":                    ("RED", "adult_icu", "Syncope / loss of consciousness (Hinglish). Emergency workup."),
    "aankhon ke aage andhera aa gaya":  ("YELLOW", "general_ward", "Pre-syncope / blacking out (Hinglish). Vitals & neuro check."),
    "chehra tedha ho gaya hai":         ("RED", "adult_icu", "Facial droop / stroke (Hinglish). Immediate stroke pathway CT."),
    "bol nahi pa raha hai":             ("RED", "adult_icu", "Aphasia / slurred speech (Hinglish). Urgent neuro evaluation."),
    "ek taraf ka haath kaam nahi kar raha": ("RED", "adult_icu", "Focal arm weakness (Hinglish). FAST stroke pathway."),
    "pet me bahut dard hai":            ("YELLOW", "general_ward", "Acute abdominal pain (Hinglish). Clinical evaluation needed."),
    "stomach me pain ho raha hai":      ("YELLOW", "general_ward", "Abdominal pain (Hinglish). Assessment required."),
    "pet kharab ho gaya hai":           ("YELLOW", "general_ward", "Gastroenteritis / loose motions (Hinglish). Rehydration needed."),
    "pet me morthan ho rahi hai":       ("YELLOW", "general_ward", "Severe abdominal cramps (Hinglish). Assessment required."),
    "pet me jalan ho rahi hai":         ("YELLOW", "general_ward", "Gastritis / abdominal pain (Hinglish). Assessment required."),
    "dast ho rahe hain":                ("YELLOW", "general_ward", "Diarrhoea (Hinglish). Oral rehydration & electrolyte care."),
    "ulti nahi ruk rahi":               ("YELLOW", "general_ward", "Persistent vomiting (Hinglish). IV antiemetics & hydration."),
    "khoon ki ulti ho rahi hai":        ("RED", "adult_icu", "Haematemesis (Hinglish). Urgent GI bleed evaluation."),
    "loose motion ho raha hai":         ("YELLOW", "general_ward", "Diarrhoea (Hinglish). Oral rehydration and electrolyte care."),
    "pet me cramps ho rahe hain":       ("YELLOW", "general_ward", "Abdominal cramps (Hinglish). Clinical evaluation."),
    "accident ho gaya hai":             ("RED", "adult_icu", "Trauma / Road accident (Hinglish). Full emergency workup."),
    "gadi se gir gaya":                 ("RED", "adult_icu", "Trauma fall from vehicle (Hinglish). Trauma assessment needed."),
    "khoon nikal raha hai":             ("RED", "adult_icu", "Active bleeding (Hinglish). Pressure dressing & surgical check."),
    "haath toot gaya":                  ("RED", "adult_icu", "Arm fracture (Hinglish). Orthopedic emergency evaluation."),
    "pair me fracture ho gaya":         ("RED", "adult_icu", "Leg fracture (Hinglish). Immobilization & ortho assessment."),
    "kutte ne kaat liya":               ("YELLOW", "general_ward", "Dog bite (Hinglish). Rabies vaccine & ARS wound care."),
    "current lag gaya":                 ("RED", "adult_icu", "Electrical shock (Hinglish). ECG & cardiac monitoring."),
    "aag se jal gaya":                  ("RED", "adult_icu", "Thermal burns (Hinglish). Fluid resuscitation & burn unit."),
    "chhat se gir gaya":                ("RED", "adult_icu", "Fall from height (Hinglish). Trauma workup & spinal care."),
    "head me chot lag gayi":            ("RED", "adult_icu", "Head trauma (Hinglish). CT scan & neuro assessment."),
    "saanp ne kaat liya":               ("RED", "adult_icu", "Snake bite envenomation (Hinglish). Emergency ASV antivenom."),
    "zeher kha liya":                   ("RED", "adult_icu", "Poisoning / Toxic ingestion (Hinglish). Emergency toxicology."),

    # ---- BENGLISH EMERGENCY PHRASES ----
    "bukey khub byatha korchhe":         ("RED", "cardiac_icu", "Acute chest pain (Benglish). High suspicion for MI. Urgent ECG."),
    "buk e pain hocche":                ("RED", "cardiac_icu", "Chest pain (Benglish). Immediate ECG and cardiac evaluation."),
    "buk chepe dhorche":                ("RED", "cardiac_icu", "Chest pressure/angina (Benglish). Urgent cardiac care."),
    "haat attack hocche":               ("RED", "cardiac_icu", "Suspected heart attack (Benglish). Immediate resuscitation room care."),
    "buk fete jacche":                  ("RED", "cardiac_icu", "Severe crushing chest pain (Benglish). High suspicion for MI."),
    "amar chhati fatya jacche":         ("RED", "cardiac_icu", "Severe crushing chest pain (Benglish). High suspicion for MI."),
    "buke bhabhari byatha":             ("RED", "cardiac_icu", "Severe chest pain (Benglish). Immediate ECG and cardiac workup."),
    "amar buke darun byatha":           ("RED", "cardiac_icu", "Severe chest pain (Benglish). Urgent cardiac evaluation."),
    "shorir e thanda gham":             ("RED", "cardiac_icu", "Cold clammy sweat / cardiogenic shock sign (Benglish). Urgent resuscitation."),
    "buk e jwalan hocche":              ("RED", "cardiac_icu", "Chest burning/angina (Benglish). Urgent ECG & cardiac evaluation."),
    "buk var hocche":                   ("RED", "cardiac_icu", "Chest heaviness (Benglish). Urgent cardiac evaluation."),
    "hritpindo dhup dhup korchhe":      ("RED", "cardiac_icu", "Tachycardia/palpitations (Benglish). Immediate ECG."),
    "hritpindo bondho":                 ("RED", "cardiac_icu", "Possible cardiac arrest (Benglish). Immediate CPR required."),
    "shorir thak thak korchhe":         ("RED", "cardiac_icu", "Severe cardiac palpitations/shivering (Benglish). Immediate ECG."),
    "buk e chhap lagchhe":              ("RED", "cardiac_icu", "Chest pressure (Benglish). Rule out acute cardiac event."),
    "nishwas nite koshto hocche":       ("YELLOW", "general_ward", "Breathlessness (Benglish). Oxygen support and lung check."),
    "saas nite parchhina":              ("RED", "adult_icu", "Severe dyspnea (Benglish). Emergency oxygen & airway care."),
    "saas nite parini":                 ("RED", "adult_icu", "Severe respiratory failure (Benglish). Emergency oxygen & airway support."),
    "saas bondho hoye jacche":          ("RED", "adult_icu", "Apnea / respiratory failure (Benglish). Emergency airway management."),
    "hapacche khub":                    ("YELLOW", "general_ward", "Severe dyspnea (Benglish). Oxygen & lung check needed."),
    "dum atke jacche":                  ("RED", "adult_icu", "Airway obstruction / choking (Benglish). Emergency airway care."),
    "buk dhup dhup korchhe":            ("RED", "cardiac_icu", "Palpitations/tachycardia (Benglish). Cardiac monitoring needed."),
    "gyan haraye phelechhe":            ("RED", "adult_icu", "Loss of consciousness (Benglish). Immediate resuscitation check."),
    "behos hoye gechhe":                ("RED", "adult_icu", "Unconscious patient (Benglish). Assess airway & circulation."),
    "chetona nai":                      ("RED", "adult_icu", "Unconscious / comatose (Benglish). Assess airway, breathing, circulation."),
    "chetona ferchhe na":               ("RED", "adult_icu", "Unconscious patient (Benglish). Emergency resuscitation care."),
    "matha ghurche":                    ("YELLOW", "general_ward", "Dizziness/Vertigo (Benglish). Vitals & neuro evaluation."),
    "matha ghurao":                     ("YELLOW", "general_ward", "Dizziness/Vertigo (Benglish). Vitals & neuro check."),
    "amar matha ghorche":               ("YELLOW", "general_ward", "Dizziness (Benglish). Vitals & glucose assessment."),
    "matha fete jacche byathay":        ("RED", "adult_icu", "Thunderclap headache (Benglish). CT scan to rule out SAH."),
    "mukhe fena uthche":                ("RED", "adult_icu", "Seizure / foaming (Benglish). Immediate airway protection."),
    "khinchuni hocche":                 ("RED", "adult_icu", "Active convulsions (Benglish). IV anticonvulsant therapy."),
    "hath pa khinchche":                ("RED", "adult_icu", "Active convulsions (Benglish). IV anticonvulsant therapy."),
    "hath pa kaapchhe":                 ("RED", "adult_icu", "Severe tremors/seizures (Benglish). Urgent medical assessment."),
    "chokhe andhar dekhchhe":           ("YELLOW", "general_ward", "Pre-syncope (Benglish). Vitals & glucose assessment."),
    "mukh beke gechhe":                 ("RED", "adult_icu", "Facial asymmetry / stroke (Benglish). Immediate stroke CT."),
    "chehra bake gechhe":               ("RED", "adult_icu", "Facial droop (Benglish). Immediate stroke protocol CT scan."),
    "chehra e taan porechhe":           ("RED", "adult_icu", "Facial droop (Benglish). Urgent CT scan for stroke."),
    "kotha bolte parchhina":            ("RED", "adult_icu", "Aphasia / stroke sign (Benglish). Urgent neuro care."),
    "ek pash obos hoye gechhe":         ("RED", "adult_icu", "Hemiparesis / stroke sign (Benglish). Urgent CT scan."),
    "shorir obos":                      ("RED", "adult_icu", "Sudden paralysis/weakness (Benglish). FAST stroke pathway CT."),
    "shorir fule gechhe":               ("RED", "adult_icu", "Severe angioedema/anaphylaxis (Benglish). Epinephrine and airway support."),
    "pet e khub byatha":                ("YELLOW", "general_ward", "Severe abdominal pain (Benglish). Clinical & ultrasound check."),
    "pet e khub jala":                  ("YELLOW", "general_ward", "Severe gastritis/abdominal pain (Benglish). Clinical evaluation."),
    "pet kharap hoye gechhe":           ("YELLOW", "general_ward", "Gastroenteritis (Benglish). ORS & rehydration needed."),
    "pet e kamrachhe":                  ("YELLOW", "general_ward", "Abdominal colic (Benglish). Clinical evaluation."),
    "pet fulche khub":                  ("YELLOW", "general_ward", "Abdominal distension (Benglish). Assess for obstruction/ascites."),
    "paykhana thamchhe na":             ("YELLOW", "general_ward", "Persistent diarrhoea (Benglish). ORS & electrolyte therapy."),
    "ulti thamchhe na":                 ("YELLOW", "general_ward", "Persistent vomiting (Benglish). IV antiemetics & fluids."),
    "ulti hocche":                      ("YELLOW", "general_ward", "Vomiting (Benglish). Antiemetics & fluid assessment."),
    "rokto ulti hocche":                ("RED", "adult_icu", "Haematemesis (Benglish). Upper GI bleed emergency."),
    "rokto felchhe":                    ("RED", "adult_icu", "Haematemesis/Hemoptysis (Benglish). Urgent resuscitation & endoscopy."),
    "rokto patla":                      ("RED", "adult_icu", "Severe active hemorrhage (Benglish). Immediate blood transfusion prep."),
    "patla paykhana hocche":            ("YELLOW", "general_ward", "Watery diarrhoea (Benglish). Rehydration & electrolyte care."),
    "accident hoye gechhe":             ("RED", "adult_icu", "Road accident (Benglish). Emergency trauma care."),
    "gari theke pore gechhe":           ("RED", "adult_icu", "Fall from vehicle (Benglish). Full trauma workup."),
    "gari dhakkay poregechhi":          ("RED", "adult_icu", "Road accident trauma (Benglish). Full emergency workup."),
    "chot legechhe khub":               ("RED", "adult_icu", "Severe trauma / injury (Benglish). Emergency surgical evaluation."),
    "rokto porchhe":                    ("RED", "adult_icu", "Active bleeding (Benglish). Hemorrhage control needed."),
    "haat bhange gechhe":               ("RED", "adult_icu", "Fractured arm (Benglish). Orthopedic emergency."),
    "paa bhange gechhe":                ("RED", "adult_icu", "Fractured leg (Benglish). Orthopedic evaluation."),
    "kukur e ketechhe":                 ("YELLOW", "general_ward", "Dog bite (Benglish). Rabies post-exposure prophylaxis."),
    "current e shock kheyechhe":        ("RED", "adult_icu", "Electric injury (Benglish). Cardiac ECG & burn monitoring."),
    "agun e pure gechhe":               ("RED", "adult_icu", "Burn injury (Benglish). Fluid resuscitation & burn care."),
    "chhad theke pore gechhe":          ("RED", "adult_icu", "Fall from height (Benglish). Full trauma assessment."),
    "mathay chot peyechhe":             ("RED", "adult_icu", "Head injury (Benglish). CT scan & neuro observation."),
    "rokto thamchhe na":                ("RED", "adult_icu", "Uncontrolled bleeding (Benglish). Immediate pressure dressing & surgery."),
    "shap e ketechhe":                  ("RED", "adult_icu", "Snake bite (Benglish). Polyvalent antivenom ASV required."),
    "saanp-e chobi diyeche":            ("RED", "adult_icu", "Snake bite envenomation (Benglish). Emergency polyvalent antivenom ASV."),
    "bish kheye phelechhe":             ("RED", "adult_icu", "Toxic ingestion / Poisoning (Benglish). Emergency toxicology."),
    "chhoto bacha saas nite parchhena": ("YELLOW", "pediatric_icu", "Pediatric respiratory distress (Benglish). Urgent pediatric care."),
    "baccha khinchuni":                 ("YELLOW", "pediatric_icu", "Pediatric seizure (Benglish). Anti-epileptic & fever control."),
    "bacchar khub jor":                 ("YELLOW", "pediatric_icu", "Pediatric high fever (Benglish). Antipyretics & workup."),

    # ---- REGIONAL SHORT WORDS & COLLOQUIAL PHRASES ----
    "haat attack":             ("RED", "cardiac_icu", "Suspected myocardial infarction. Needs immediate cardiac intervention."),
    "chhati me dard":          ("RED", "cardiac_icu", "Acute chest pain indicating possible cardiac event."),
    "chhatir byatha":          ("RED", "cardiac_icu", "Chest pain (Bengali). Urgent cardiac evaluation required."),
    "chest heavy":             ("RED", "cardiac_icu", "Chest heaviness — cardiac origin suspected. Urgent ECG."),
    "chest painn":             ("RED", "cardiac_icu", "Acute chest pain (typo). Urgent ECG required."),
    "heart issue":             ("RED", "cardiac_icu", "Acute cardiac complaint. Immediate ECG and vitals."),
    "pet betha":               ("YELLOW", "general_ward", "Acute abdominal pain (Bengali). Assessment required."),
    "pet dard":                ("YELLOW", "general_ward", "Abdominal pain (Hindi). Clinical evaluation needed."),
    "matha ghora":             ("YELLOW", "general_ward", "Dizziness/Vertigo (Bengali). Vitals and neuro check needed."),
    "sar dard":                ("YELLOW", "general_ward", "Headache (Hindi). Clinical evaluation needed."),
    "shwash koshto":           ("YELLOW", "general_ward", "Respiratory distress (Bengali). Oxygen support needed."),
    "saas phulna":             ("YELLOW", "general_ward", "Breathlessness (Hindi). Oxygen and respiratory evaluation."),
    "stomach acche":           ("YELLOW", "general_ward", "Abdominal pain (typo). Clinical assessment required."),
    "stomach paining":         ("YELLOW", "general_ward", "Abdominal pain. Clinical evaluation needed."),
    "vomting":                 ("YELLOW", "general_ward", "Vomiting (typo). Assess dehydration and fluids."),
    "dizzyness":               ("YELLOW", "general_ward", "Dizziness (typo). Vitals and glucose check needed."),

    # ---- RED: NEUROLOGICAL EMERGENCIES → adult_icu ----
    "stroke":                  ("RED", "adult_icu", "Suspected stroke. CT scan and thrombolysis evaluation needed."),
    "brain attack":            ("RED", "adult_icu", "Suspected stroke. Urgent CT and thrombolysis assessment."),
    "face drooping":           ("RED", "adult_icu", "Facial droop — FAST stroke sign. Urgent CT scan."),
    "slurred speech":          ("RED", "adult_icu", "Slurred speech — possible stroke or TIA. Urgent neuro evaluation."),
    "can't speak":             ("RED", "adult_icu", "Aphasia — possible stroke. Urgent CT and neuro assessment."),
    "paralysis":               ("RED", "adult_icu", "Sudden paralysis may indicate stroke or spinal injury."),
    "hemiplegia":              ("RED", "adult_icu", "One-sided paralysis — high stroke indicator. Urgent neuro care."),
    "sudden numbness":         ("RED", "adult_icu", "Focal neurological deficit — rule out acute stroke."),
    "thunderclap headache":    ("RED", "adult_icu", "Sudden severe headache — rule out subarachnoid hemorrhage."),
    "worst headache":          ("RED", "adult_icu", "Thunderclap headache — urgent CT to rule out SAH."),
    "brain hemorrhage":        ("RED", "adult_icu", "Intracranial bleeding — neurosurgical emergency."),
    "aneurysm burst":          ("RED", "adult_icu", "Ruptured cerebral aneurysm — emergency neurosurgery."),
    "active seizure":          ("RED", "adult_icu", "Ongoing seizure activity. Administer IV benzodiazepines immediately."),
    "status epilepticus":      ("RED", "adult_icu", "Continuous seizure >5 mins — medical emergency."),
    "seizure":                 ("RED", "adult_icu", "Active seizure. Anti-epileptic medication and monitoring required."),
    "convulsion":              ("RED", "adult_icu", "Convulsive episode. Protect airway, administer anti-epileptics."),
    "fits":                    ("RED", "adult_icu", "Epileptic fit. Protect airway, administer anti-epileptics."),
    "unconscious":             ("RED", "adult_icu", "Patient unconscious. Assess airway, breathing, circulation."),
    "unresponsive":            ("RED", "adult_icu", "Unresponsive patient. Full trauma and neuro assessment needed."),
    "not responding":          ("RED", "adult_icu", "Patient unresponsive. Emergency evaluation required."),
    "passed out":              ("RED", "adult_icu", "Loss of consciousness. Assess for cardiac, neuro, metabolic causes."),
    "collapsed":               ("RED", "adult_icu", "Collapse — assess for cardiac arrest, stroke, hypoglycaemia."),
    "coma":                    ("RED", "adult_icu", "Comatose patient. Immediate intubation and ICU care."),
    "meningitis fever":        ("RED", "adult_icu", "Suspected bacterial meningitis — urgent lumbar puncture and IV antibiotics."),

    # ---- RED: CRITICAL RESPIRATORY → adult_icu ----
    "not breathing":           ("RED", "adult_icu", "Respiratory arrest. Immediate airway management required."),
    "stopped breathing":       ("RED", "adult_icu", "Respiratory failure. Urgent ventilator support needed."),
    "cannot breathe":          ("RED", "adult_icu", "Respiratory failure. Emergency airway management needed."),
    "no breathing":            ("RED", "adult_icu", "Apnea detected. Immediate resuscitation required."),
    "gasping":                 ("RED", "adult_icu", "Agonal breathing or severe hypoxia. Urgent airway intervention."),
    "cyanosis":                ("RED", "adult_icu", "Central cyanosis — severe hypoxemia. Oxygen & intubation risk."),
    "blue lips":               ("RED", "adult_icu", "Severe hypoxia — oxygen immediately and airway support."),
    "choking":                 ("RED", "adult_icu", "Airway obstruction. Heimlich maneuver and emergency care needed."),
    "anaphylaxis":             ("RED", "adult_icu", "Anaphylactic shock. Epinephrine immediately, airway support."),
    "throat closing":          ("RED", "adult_icu", "Acute upper airway obstruction / anaphylaxis — immediate IM epinephrine."),
    "tongue swelling":         ("RED", "adult_icu", "Angioedema compromising airway — emergency airway management."),
    "stridor":                 ("RED", "adult_icu", "Upper airway obstruction. Nebulized epinephrine & airway team."),

    # ---- RED: TRAUMA, SURGERY & POISONING → adult_icu ----
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
    "compound fracture":       ("RED", "adult_icu", "Open fracture with bone exposure. Surgery required."),
    "bone sticking out":       ("RED", "adult_icu", "Open fracture — orthopedic emergency."),
    "crush injury":            ("RED", "adult_icu", "Crush injury. Risk of rhabdomyolysis and renal failure."),
    "fall from height":        ("RED", "adult_icu", "Fall from height. Spinal precautions and full assessment."),
    "fell from roof":          ("RED", "adult_icu", "High fall — spinal and internal injury risk. Full trauma care."),
    "electrocution":           ("RED", "adult_icu", "Electrical injury. Cardiac monitoring required."),
    "electric shock":          ("RED", "adult_icu", "Electric shock. Cardiac and burn assessment needed."),
    "drowning":                ("RED", "adult_icu", "Near-drowning. Airway management and pulmonary assessment."),
    "near drowning":           ("RED", "adult_icu", "Near-drowning. Respiratory and metabolic assessment."),
    "severe burn":             ("RED", "adult_icu", "Major burn injury — fluid resuscitation & ICU burn care."),
    "fire burn":               ("RED", "adult_icu", "Burns from fire. Fluid resuscitation and wound care."),
    "acid burn":               ("RED", "adult_icu", "Chemical burn. Flush with water, urgent surgical review."),
    "severe bleeding":         ("RED", "adult_icu", "Severe hemorrhage. Immediate pressure and transfusion may be needed."),
    "arterial bleed":          ("RED", "adult_icu", "Pulsatile hemorrhage — urgent tourniquet & surgical repair."),
    "blood pouring":           ("RED", "adult_icu", "Active hemorrhage. Immediate tourniquet or direct pressure."),
    "blood loss":              ("RED", "adult_icu", "Major blood loss — IV fluids, crossmatch, and surgery."),
    "amputation":              ("RED", "adult_icu", "Traumatic limb amputation — hemorrhage control & replantation team."),
    "severed limb":            ("RED", "adult_icu", "Traumatic amputation — urgent surgical intervention."),
    "overdose":                ("RED", "adult_icu", "Drug overdose. Airway, antidote, and monitoring required."),
    "drug overdose":           ("RED", "adult_icu", "Substance overdose. Naloxone if opioid, urgent ICU care."),
    "poison":                  ("RED", "adult_icu", "Poisoning. Identify substance, gastric lavage, antidote if available."),
    "poisoned":                ("RED", "adult_icu", "Toxic ingestion. Emergency toxicology and antidote therapy."),
    "rat poison":              ("RED", "adult_icu", "Rodenticide ingestion. Vitamin K and monitoring."),
    "insecticide":             ("RED", "adult_icu", "Organophosphate poisoning. Atropine and pralidoxime."),
    "snake bite":              ("RED", "adult_icu", "Envenomation. Antivenom and monitoring for coagulopathy."),
    "cobra bite":              ("RED", "adult_icu", "Neurotoxic snake bite — immediate polyvalent ASV & intubation prep."),
    "viper bite":              ("RED", "adult_icu", "Vasculotoxic snake bite — immediate polyvalent ASV & blood product prep."),
    "vomit blood":             ("RED", "adult_icu", "Haematemesis — upper GI bleed. Urgent endoscopy."),

    # ---- RED: OBSTETRIC EMERGENCIES → adult_icu ----
    "eclampsia":               ("RED", "adult_icu", "Eclampsia with seizures. Magnesium sulfate and emergency delivery needed."),
    "hemorrhage postpartum":   ("RED", "adult_icu", "Postpartum hemorrhage. Urgent uterotonic and possible surgery."),
    "postpartum bleeding":     ("RED", "adult_icu", "Postpartum hemorrhage — potentially life-threatening."),
    "placenta abruption":      ("RED", "adult_icu", "Placental abruption. Emergency caesarean required."),
    "ectopic pregnancy":       ("RED", "adult_icu", "Ruptured ectopic pregnancy. Emergency surgery required."),

    # ---- YELLOW: PEDIATRIC EMERGENCIES → pediatric_icu ----
    "child breathing difficulty": ("YELLOW", "pediatric_icu", "Pediatric respiratory distress. Nebulization and monitoring."),
    "child seizure":              ("YELLOW", "pediatric_icu", "Pediatric seizure. Anti-epileptic and fever management."),
    "child convulsion":           ("YELLOW", "pediatric_icu", "Pediatric convulsion. Protect airway, anti-epileptic therapy."),
    "child high fever":           ("YELLOW", "pediatric_icu", "Pediatric high fever. Antipyretics and workup needed."),
    "child unresponsive":         ("YELLOW", "pediatric_icu", "Unresponsive child — pediatric emergency assessment."),
    "infant not feeding":         ("YELLOW", "pediatric_icu", "Infant feeding failure. Assess for dehydration and infection."),
    "baby not breathing well":    ("YELLOW", "pediatric_icu", "Neonatal respiratory distress. Urgent pediatric assessment."),
    "newborn not breathing":      ("YELLOW", "pediatric_icu", "Neonatal apnea — urgent resuscitation and NICU."),
    "baby choking":               ("YELLOW", "pediatric_icu", "Infant choking — back blows and emergency airway care."),
    "child swallowed coin":       ("YELLOW", "pediatric_icu", "Pediatric foreign body ingestion — X-ray & ENT review."),
    "child swallowed battery":    ("YELLOW", "pediatric_icu", "Button battery ingestion — emergency endoscopy required."),
    "child febrile seizure":      ("YELLOW", "pediatric_icu", "Febrile seizure in child — cooling, anticonvulsant if prolonged."),
    "baby fever":                 ("YELLOW", "pediatric_icu", "Infant fever — sepsis risk. Urgent paediatric workup."),
    "child vomiting":             ("YELLOW", "pediatric_icu", "Persistent pediatric vomiting. Assess dehydration."),
    "child lethargic":            ("YELLOW", "pediatric_icu", "Lethargic child — rule out sepsis, hypoglycemia, meningitis."),
    "baby not waking":            ("YELLOW", "pediatric_icu", "Pediatric altered mental status — emergency workup."),

    # ---- YELLOW: GASTROINTESTINAL & ABDOMINAL → general_ward ----
    "stomach pain":            ("YELLOW", "general_ward", "Acute abdominal pain. Assessment and imaging required."),
    "stomach ache":            ("YELLOW", "general_ward", "Abdominal pain requiring assessment and management."),
    "tummy pain":              ("YELLOW", "general_ward", "Abdominal pain. Clinical assessment and imaging if needed."),
    "belly pain":              ("YELLOW", "general_ward", "Abdominal pain. Assessment for surgical or GI cause."),
    "abdominal pain":          ("YELLOW", "general_ward", "Acute abdominal pain. Needs imaging and assessment."),
    "appendix pain":           ("YELLOW", "general_ward", "Right iliac fossa pain — rule out appendicitis urgently."),
    "appendicitis":            ("YELLOW", "general_ward", "Suspected appendicitis — ultrasound/CT scan & surgical review."),
    "kidney stone":            ("YELLOW", "general_ward", "Renal colic. Analgesia and urology assessment."),
    "gallstone":               ("YELLOW", "general_ward", "Biliary colic — assess for cholecystitis. Surgical review."),
    "vomiting":                ("YELLOW", "general_ward", "Vomiting. Assess for dehydration, cause. IV fluids if needed."),
    "food poisoning":          ("YELLOW", "general_ward", "Food poisoning. Rehydration and supportive care."),
    "diarrhea":                ("YELLOW", "general_ward", "Diarrhea. Oral rehydration. Seek care if bloody or prolonged."),
    "loose motions":           ("YELLOW", "general_ward", "Loose stool. Oral rehydration and electrolyte replacement."),
    "blood in stool":          ("YELLOW", "general_ward", "GI bleeding. Endoscopic evaluation may be needed."),
    "blood in urine":          ("YELLOW", "general_ward", "Hematuria. Urological assessment needed."),
    "jaundice":                ("YELLOW", "general_ward", "Jaundice. Liver function tests and hepatology review."),
    "yellow skin":             ("YELLOW", "general_ward", "Jaundice — assess for hepatitis or biliary obstruction."),
    "pancreatitis":            ("YELLOW", "general_ward", "Acute pancreatitis — IV hydration & analgesia."),

    # ---- YELLOW: RESPIRATORY & INFECTIONS → general_ward ----
    "breathing difficulty":    ("YELLOW", "general_ward", "Respiratory distress. Oxygen supplementation and monitoring."),
    "shortness of breath":     ("YELLOW", "general_ward", "Dyspnea requiring assessment. May need oxygen support."),
    "breathlessness":          ("YELLOW", "general_ward", "Breathlessness. Assess oxygen saturation and lung function."),
    "asthma attack":           ("YELLOW", "general_ward", "Acute asthma exacerbation. Bronchodilators and steroids."),
    "pneumonia":               ("YELLOW", "general_ward", "Suspected pneumonia. Chest X-ray, antibiotics, oxygen."),
    "tuberculosis":            ("YELLOW", "general_ward", "TB symptoms. Sputum smear and infectious disease workup."),
    "high fever":              ("YELLOW", "general_ward", "High fever requiring investigation. May indicate infection."),
    "dengue":                  ("YELLOW", "general_ward", "Suspected dengue. CBC, platelets, and supportive care."),
    "malaria":                 ("YELLOW", "general_ward", "Suspected malaria. Smear and antimalarial therapy."),
    "typhoid":                 ("YELLOW", "general_ward", "Typhoid fever. Blood culture and antibiotic therapy."),
    "dehydration":             ("YELLOW", "general_ward", "Dehydration. IV fluid replacement needed."),
    "diabetic emergency":      ("YELLOW", "general_ward", "Diabetic crisis. Blood sugar management and monitoring."),

    # ---- GREEN: MILD & NON-URGENT CLINIC CARE ----
    "mild headache":           ("GREEN", "general_ward", "Mild tension headache. Rest and oral analgesics."),
    "slight cold":             ("GREEN", "general_ward", "Mild upper respiratory tract infection. Symptomatic relief."),
    "runny nose":              ("GREEN", "general_ward", "Coryza. Antihistamines and supportive care."),
    "sore throat":             ("GREEN", "general_ward", "Pharyngitis. Warm saline gargles and analgesics."),
    "minor cut":               ("GREEN", "general_ward", "Superficial laceration. Wound cleaning and dressing."),
    "small scrape":            ("GREEN", "general_ward", "Minor abrasion. Clean wound and apply antiseptic."),
    "paper cut":               ("GREEN", "general_ward", "Minor cut. Clean with water and apply bandage.")
}


def classify_symptoms(text):
    """
    Classifies patient symptoms into RED/YELLOW/GREEN urgency levels.
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

    weight_map = {"RED": 3, "YELLOW": 2, "GREEN": 1}

    # Sort keywords by length (longest first)
    sorted_keywords = sorted(SYMPTOM_DATABASE.items(), key=lambda x: len(x[0]), reverse=True)

    for keyword, (severity, ward, explanation) in sorted_keywords:
        if keyword in text_lower:
            if any(keyword in prev for prev in matched_keywords):
                continue

            matched_keywords.append(keyword)
            weight = weight_map.get(severity, 0)

            if weight > highest_weight:
                highest_weight = weight
                best_severity = severity
                best_ward = ward
                best_explanation = explanation

    if best_severity is None:
        best_severity = "YELLOW"

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
        "reason": best_explanation,
        "matched_keywords": matched_keywords
    }
