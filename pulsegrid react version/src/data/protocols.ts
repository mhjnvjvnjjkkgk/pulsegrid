import { ClinicalProtocol } from '../types';

export const CLINICAL_PROTOCOLS: Record<string, ClinicalProtocol> = {
  cardiac: {
    category: 'cardiac',
    esi_acuity: '🚨 ESI-1 CRITICAL PRIORITY (IMMEDIATE CARDIAC ICU TRIAGE)',
    priority_code: 'ACS-STEMI-STAT',
    title: 'Severe Chest Pain / Heart Attack',
    target_ward: 'cardiac_icu',
    rapid_scan_symptoms: [
      { id: 'cs1', label: 'Crushing jaw/arm pain', checked: true, iconType: 'radiation' },
      { id: 'cs2', label: 'Severe breathlessness', checked: true, iconType: 'lungs' },
      { id: 'cs3', label: 'Cold diaphoresis (sweat)', checked: true, iconType: 'droplet' },
      { id: 'cs4', label: 'Sudden dizziness', checked: false, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'STAT',
      angle_badge: '45° ANGLE',
      title: 'Elevate Torso with Bent Knees',
      instruction:
        'Seat patient upright leaning back at 45° (Semi-Fowler position) with bent knees. This minimizes cardiac workload and eases thoracic congestion instantly.',
    },
    protocol_steps: [
      'Call 108 immediately and inform regarding acute STEMI presentation.',
      'Have conscious patient chew one 300mg Soluble Aspirin (Disprin) immediately if no allergy.',
      'Assist patient to take sublingual Nitroglycerin spray/tablet if prescribed.',
      'Strictly prohibit any walking, standing or stair climbing.',
      'Loosen tight collar, belt, and chest clothing; keep room well-ventilated.',
      'Monitor radial pulse and prepare automated external defibrillator (AED) if available.',
    ],
    do_nots: [
      '❌ Do NOT allow patient to lie flat (causes acute pulmonary edema).',
      '❌ Do NOT allow patient to walk to car or ambulance.',
      '❌ Do NOT give water, food, or heavy oral liquids.',
    ],
    calming_script:
      '"Breathe slowly with me. In through the nose, out through the mouth. The cardiac ICU slot is locked and ready."',
  },

  arrest: {
    category: 'arrest',
    esi_acuity: '🚨 ESI-1 CRITICAL (Immediate Resuscitation Required)',
    priority_code: 'CPR-CODE-BLUE',
    title: 'Cardiac Arrest / Unresponsive Patient',
    target_ward: 'adult_icu',
    rapid_scan_symptoms: [
      { id: 'ar1', label: 'No carotid pulse detected', checked: true, iconType: 'alert' },
      { id: 'ar2', label: 'No chest rise (agonal gasping)', checked: true, iconType: 'lungs' },
      { id: 'ar3', label: 'Completely unresponsive', checked: true, iconType: 'alert' },
      { id: 'ar4', label: 'Cyanotic (blue) lips/digits', checked: true, iconType: 'droplet' },
    ],
    immediate_action: {
      badge: 'IMMEDIATE',
      angle_badge: 'FLAT ON FLOOR',
      title: 'Begin High-Quality Chest Compressions',
      instruction:
        'Place patient flat on a firm floor. Interlock hands in center of chest. Push hard and fast at 100-120 beats/min to 2 inches depth.',
    },
    protocol_steps: [
      'Shout for help and instruct bystander to call 108 & fetch nearest AED.',
      'Deliver 100-120 compressions per minute (tempo of "Stayin Alive").',
      'Allow complete chest recoil after every single push.',
      'If trained: 30 compressions followed by 2 quick rescue breaths.',
      'Power on AED as soon as it arrives and follow voice prompts.',
      'Rotate compressor every 2 minutes to prevent rescuer fatigue.',
    ],
    do_nots: [
      '❌ Do NOT place pillows under the head.',
      '❌ Do NOT attempt to give liquids or oral medications.',
      '❌ Do NOT delay compressions searching for pulse beyond 10 seconds.',
    ],
    calming_script:
      '"Stay back, give us room! Ambulance is on the way. I am giving CPR to keep oxygen moving to the heart."',
  },

  stroke: {
    category: 'stroke',
    esi_acuity: '🚨 ESI-1 CRITICAL (Brain Attack - Thrombolysis Window)',
    priority_code: 'STROKE-CODE-TPA',
    title: 'Acute Ischemic Stroke / FAST Protocol',
    target_ward: 'adult_icu',
    rapid_scan_symptoms: [
      { id: 'st1', label: 'Facial asymmetry / droop', checked: true, iconType: 'alert' },
      { id: 'st2', label: 'One-sided arm / leg weakness', checked: true, iconType: 'alert' },
      { id: 'st3', label: 'Slurred or incomprehensible speech', checked: true, iconType: 'radiation' },
      { id: 'st4', label: 'Sudden loss of balance/vision', checked: false, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'TIME CRITICAL',
      angle_badge: '15° - 30° ELEVATION',
      title: 'Lateral Recovery Position / Slight Elevation',
      instruction:
        'Lay patient on side in Recovery Position with head elevated 15-30°. Protect airway from saliva/emesis aspiration.',
    },
    protocol_steps: [
      'Record EXACT time symptoms were first noticed (vital for 4.5h tPA thrombolysis).',
      'Do not allow patient to stand or walk.',
      'Check blood sugar if glucometer available (rule out hypoglycemia mimic).',
      'Keep patient calm, quiet, and in dark/dimly lit environment.',
      'Do not administer any oral medication, food, or water.',
      'Transport directly to Comprehensive Stroke Center with CT & Neuro-cath lab.',
    ],
    do_nots: [
      '❌ Do NOT give Aspirin or blood thinners (lethal if hemorrhagic stroke).',
      '❌ Do NOT give water or food (paralyzed swallowing muscles cause fatal choking).',
    ],
    calming_script:
      '"Stay calm. Keep your head on the side. We have recorded the exact stroke onset time for the neuro-specialist."',
  },

  trauma: {
    category: 'trauma',
    esi_acuity: '🚨 ESI-1 CRITICAL (Massive Transfusion Protocol)',
    priority_code: 'TRAUMA-MTP-STAT',
    title: 'Arterial Bleeding / Massive Trauma Shock',
    target_ward: 'adult_icu',
    rapid_scan_symptoms: [
      { id: 'tr1', label: 'Pulsatile bright red blood spurting', checked: true, iconType: 'droplet' },
      { id: 'tr2', label: 'Rapid weak pulse (>120 bpm)', checked: true, iconType: 'alert' },
      { id: 'tr3', label: 'Cold, pale, clammy skin', checked: true, iconType: 'droplet' },
      { id: 'tr4', label: 'Altered mental status / confusion', checked: false, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'HEMO-STOP',
      angle_badge: 'ELEVATE & PRESS',
      title: 'Firm Direct Compression & Tourniquet',
      instruction:
        'Apply heavy direct pressure over wound with clean cloth. For limb arterial spurt, apply tourniquet 2-3 inches above wound immediately.',
    },
    protocol_steps: [
      'Apply uninterrupted direct manual pressure over bleeding site.',
      'Tighten tourniquet until bright bleeding halts completely; write time on patient forehead.',
      'Pack deep junctional wounds (groin, axilla) with sterile gauze.',
      'Keep patient warm with blankets to prevent hypothermic coagulopathy.',
      'Elevate lower extremities 12 inches if no pelvic/spinal fracture suspected.',
      'Prepare for Universal O-Negative blood uncrossmatched resuscitation.',
    ],
    do_nots: [
      '❌ Do NOT remove blood-soaked dressings; apply fresh ones directly on top.',
      '❌ Do NOT loosen tourniquet once applied.',
      '❌ Do NOT give food or water before surgical intervention.',
    ],
    calming_script:
      '"Hold continuous pressure with me! The trauma resuscitation team and O-negative blood are prepped."',
  },

  pediatric: {
    category: 'pediatric',
    esi_acuity: '🚨 ESI-2 URGENT (Pediatric Resuscitation Bay)',
    priority_code: 'PEDI-FEBRILE-STAT',
    title: 'High Fever & Febrile Convulsions in Child',
    target_ward: 'pediatric_icu',
    rapid_scan_symptoms: [
      { id: 'pe1', label: 'Temperature > 102°F (38.9°C)', checked: true, iconType: 'alert' },
      { id: 'pe2', label: 'Rhythmic limb twitching / jerking', checked: true, iconType: 'radiation' },
      { id: 'pe3', label: 'Eyes rolled upward', checked: true, iconType: 'alert' },
      { id: 'pe4', label: 'Inability to respond during convulsion', checked: true, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'COOL & PROTECT',
      angle_badge: 'TEPID WIPE',
      title: 'Tepid Sponging & Recovery Position',
      instruction:
        'Lay child on side on soft mattress. Sponge body with lukewarm (not ice) water to safely dissipate heat without triggering shivering.',
    },
    protocol_steps: [
      'Clear sharp objects around the child to prevent physical injury.',
      'Time the seizure duration carefully on phone timer.',
      'Loosen tight clothing around neck and torso.',
      'Ensure mouth is clear of secretions or regurgitation.',
      'Do not place anything inside the child’s mouth.',
      'Transport to specialized Pediatric ICU immediately.',
    ],
    do_nots: [
      '❌ Do NOT immerse child in ice-cold bath (triggers shivering and rebound hyperthermia).',
      '❌ Do NOT force fingers, spoons or objects between teeth.',
    ],
    calming_script:
      '"Febrile seizures are terrifying but usually subside within 2-3 mins. We are actively cooling the child safely."',
  },

  respiratory: {
    category: 'respiratory',
    esi_acuity: '🚨 ESI-1 CRITICAL (High-Flow O2 & Airway Management)',
    priority_code: 'RESP-ASTHMA-STAT',
    title: 'Severe Respiratory Distress / Status Asthmaticus',
    target_ward: 'general_oxygen',
    rapid_scan_symptoms: [
      { id: 're1', label: 'Intercostal retractions (ribs pulling in)', checked: true, iconType: 'lungs' },
      { id: 're2', label: 'Audible expiratory wheeze', checked: true, iconType: 'alert' },
      { id: 're3', label: 'SpO2 < 90% or central cyanosis', checked: true, iconType: 'droplet' },
      { id: 're4', label: 'Inability to speak in full sentences', checked: true, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'AIRWAY STAT',
      angle_badge: 'TRIPOD STANCE',
      title: 'Tripod Position & Inhaler Spacer',
      instruction:
        'Sit patient upright leaning slightly forward with hands on knees (Tripod position). Administer 2-4 puffs of Salbutamol inhaler via spacer.',
    },
    protocol_steps: [
      'Administer 4 puffs of bronchodilator inhaler; repeat in 5 minutes if no relief.',
      'Open windows or ensure high-ventilation airflow.',
      'Guide patient through pursed-lip breathing (inhale 2s, exhale 4s).',
      'Loosen neckwear, collars, and tight chest bands.',
      'Keep patient calm; anxiety increases oxygen consumption.',
      'Transport to hospital with High-Flow Nasal Cannula (HFNC) & Oxygen Ward.',
    ],
    do_nots: [
      '❌ Do NOT force patient to lie down flat.',
      '❌ Do NOT crowd around the patient.',
    ],
    calming_script:
      '"Breathe slowly with me: In... two... Out... two... three... four. High-flow oxygen bed is locked."',
  },

  burn: {
    category: 'burn',
    esi_acuity: '🚨 ESI-2 URGENT (Burn & Fluid Resuscitation Bay)',
    priority_code: 'BURN-PARKLAND-STAT',
    title: 'Severe Burns / Thermal Inhalation Injury',
    target_ward: 'adult_icu',
    rapid_scan_symptoms: [
      { id: 'bu1', label: 'Blistering / deep dermal charring', checked: true, iconType: 'alert' },
      { id: 'bu2', label: 'Facial burns / soot around nostrils', checked: true, iconType: 'lungs' },
      { id: 'bu3', label: 'Severe unrelenting pain or numbness', checked: true, iconType: 'radiation' },
      { id: 'bu4', label: 'Hypovolemic shivering / tachycardia', checked: false, iconType: 'droplet' },
    ],
    immediate_action: {
      badge: 'COOL & COVER',
      angle_badge: 'STERILE COVER',
      title: 'Cool Running Water & Clean Cling Film',
      instruction:
        'Irrigate burned area immediately with clean, cool running water for 10-20 minutes. Cover loosely with sterile dressing or clean cling film.',
    },
    protocol_steps: [
      'Remove burning source; extinguish flames and remove hot garments (unless stuck).',
      'Do not apply ice directly or submerge in ice water (causes tissue ischemia).',
      'Remove jewelry, rings, and watches before edema develops rapidly.',
      'Check airway patency if smoke inhalation or facial burns suspected.',
      'Keep patient warm with a clean blanket to prevent shock hypothermia.',
      'Transport immediately to Burn Resuscitation Unit.',
    ],
    do_nots: [
      '❌ Do NOT apply toothpaste, butter, oil, or turmeric.',
      '❌ Do NOT burst or puncture blisters.',
      '❌ Do NOT peel clothing that is melted or adhered to skin.',
    ],
    calming_script:
      '"Keep the sterile wrap in place. Do not scratch. The burn trauma team is prepping IV fluids."',
  },

  maternity: {
    category: 'maternity',
    esi_acuity: '🚨 ESI-1 CRITICAL (Emergency Obstetric Bay)',
    priority_code: 'OBGYN-LABOR-STAT',
    title: 'Precipitous Labor / Obstetric Emergency',
    target_ward: 'general_oxygen',
    rapid_scan_symptoms: [
      { id: 'ma1', label: 'Contractions < 3 minutes apart', checked: true, iconType: 'alert' },
      { id: 'ma2', label: 'Rupture of membranes (water broke)', checked: true, iconType: 'droplet' },
      { id: 'ma3', label: 'Urge to push / crowning visible', checked: false, iconType: 'alert' },
      { id: 'ma4', label: 'Vaginal bleeding or severe pain', checked: false, iconType: 'alert' },
    ],
    immediate_action: {
      badge: 'LATERAL TILT',
      angle_badge: 'LEFT LATERAL',
      title: 'Left Lateral Recumbent Positioning',
      instruction:
        'Place mother on her left side with a pillow behind her back. This relieves inferior vena cava compression and maximizes fetal placental blood flow.',
    },
    protocol_steps: [
      'Call 108 and alert labor triage desk for impending delivery.',
      'Time contractions from start of one to start of next.',
      'Keep mother warm, calm, and breathing through contractions (panting breath).',
      'Prepare sterile towels, clean blankets, and bulb suction for newborn.',
      'If delivery is imminent, support newborn head gently; do not pull.',
      'Transport directly to Labor Suite & Neonatal ICU facility.',
    ],
    do_nots: [
      '❌ Do NOT have mother lie flat on her back (supine hypotension syndrome).',
      '❌ Do NOT attempt to hold legs together to delay delivery.',
      '❌ Do NOT pull on umbilical cord.',
    ],
    calming_script:
      '"Breathe in through your nose and blow out gently. We have alerted the labor suite and neonatal team."',
  },
};
