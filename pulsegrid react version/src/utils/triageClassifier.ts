import { SeverityLevel, WardCode } from '../types';

export interface TriageClassification {
  severity: SeverityLevel;
  recommended_ward: WardCode;
  protocol_key: string;
  matched_keywords: string[];
  score: number;
  explanation: string;
  blood_needed?: {
    group?: string;
    component?: string;
  };
  offer_hold: boolean;
}

export function classifyEmergency(query: string, patientAge?: number): TriageClassification {
  const normalized = query.toLowerCase().trim();

  // Blood group detection
  const bloodMatch = normalized.match(/\b(o-|o\+|a-|a\+|b-|b\+|ab-|ab\+)\b/i);
  const bloodKeyword =
    normalized.includes('blood') ||
    normalized.includes('prbc') ||
    normalized.includes('platelet') ||
    normalized.includes('plasma') ||
    normalized.includes('rokto') ||
    normalized.includes('khoon');

  let bloodNeeded: { group?: string; component?: string } | undefined = undefined;
  if (bloodMatch || bloodKeyword) {
    bloodNeeded = {
      group: bloodMatch ? bloodMatch[1].toUpperCase() : 'O-',
      component: normalized.includes('platelet')
        ? 'PLATELETS'
        : normalized.includes('plasma')
        ? 'PLASMA'
        : 'PRBC',
    };
  }

  // Check Negations
  const isNegated =
    normalized.includes('no chest pain') ||
    normalized.includes('not breathless') ||
    normalized.includes('no bleeding') ||
    normalized.includes('fine now') ||
    normalized.includes('just acidity') ||
    normalized.includes('normal');

  if (isNegated && !normalized.includes('severe') && !normalized.includes('unresponsive')) {
    return {
      severity: 'GREEN',
      recommended_ward: 'general_oxygen',
      protocol_key: 'respiratory',
      matched_keywords: ['ruled out critical symptoms'],
      score: 15,
      explanation: 'No critical acute telemetry flags detected. Safe for outpatient clinic or oral antacid evaluation.',
      offer_hold: false,
    };
  }

  // 1. CARDIAC ARREST / UNRESPONSIVE
  if (
    normalized.includes('cardiac arrest') ||
    normalized.includes('no pulse') ||
    normalized.includes('stopped breathing') ||
    normalized.includes('unresponsive') ||
    normalized.includes('cpr') ||
    normalized.includes('collapsed') ||
    normalized.includes('behosh') ||
    normalized.includes('agyan') ||
    normalized.includes('behoshi')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'adult_icu',
      protocol_key: 'arrest',
      matched_keywords: ['unresponsive', 'cardiac arrest / no pulse'],
      score: 100,
      explanation: 'Loss of responsiveness and respiratory collapse requires immediate CPR & Level-1 Resuscitation Bay.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 2. SEVERE CHEST PAIN / HEART ATTACK
  if (
    normalized.includes('chest pain') ||
    normalized.includes('heart attack') ||
    normalized.includes('seene mein') ||
    normalized.includes('chhati te') ||
    normalized.includes('angina') ||
    normalized.includes('chhatir') ||
    normalized.includes('cardiac') ||
    normalized.includes('left arm pain') ||
    normalized.includes('jaw pain')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'cardiac_icu',
      protocol_key: 'cardiac',
      matched_keywords: ['chest pain', 'cardiac symptoms', 'radiation to arm'],
      score: 95,
      explanation: 'Acute coronary syndrome presentation. Requires urgent Cath Lab & Cardiac ICU monitored bed.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 3. STROKE / PARALYSIS / FAST
  if (
    normalized.includes('stroke') ||
    normalized.includes('paralysis') ||
    normalized.includes('face droop') ||
    normalized.includes('slurred speech') ||
    normalized.includes('arm weakness') ||
    normalized.includes('brain attack') ||
    normalized.includes('mouth crooked') ||
    normalized.includes('mukhe baka')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'adult_icu',
      protocol_key: 'stroke',
      matched_keywords: ['stroke symptoms', 'FAST protocol positive'],
      score: 95,
      explanation: 'Acute neurological deficit within active thrombolysis window. Emergency CT Brain priority.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 4. ARTERIAL BLEEDING / MASSIVE TRAUMA
  if (
    normalized.includes('bleeding') ||
    normalized.includes('blood loss') ||
    normalized.includes('accident') ||
    normalized.includes('spurting') ||
    normalized.includes('stab') ||
    normalized.includes('khoon') ||
    normalized.includes('rokto') ||
    normalized.includes('trauma')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'adult_icu',
      protocol_key: 'trauma',
      matched_keywords: ['arterial bleeding', 'massive blood loss', 'trauma shock'],
      score: 90,
      explanation: 'Critical vascular compromise. Trauma surgery & Massive Transfusion Protocol (MTP) alerted.',
      offer_hold: true,
      blood_needed: bloodNeeded || { group: 'O-', component: 'PRBC' },
    };
  }

  // 5. PEDIATRIC CONVULSION / FEVER
  if (
    (patientAge !== undefined && patientAge <= 12) ||
    normalized.includes('child') ||
    normalized.includes('baby') ||
    normalized.includes('baccha') ||
    normalized.includes('bacha') ||
    normalized.includes('shishu') ||
    normalized.includes('pediatric') ||
    normalized.includes('pedia')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'pediatric_icu',
      protocol_key: 'pediatric',
      matched_keywords: ['pediatric emergency', 'child high fever/fit'],
      score: 88,
      explanation: 'Pediatric urgent distress. Auto-routed to dedicated Pediatric ICU & Neonatal Care Unit.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 6. RESPIRATORY DISTRESS / ASTHMA / CHOKING
  if (
    normalized.includes('asthma') ||
    normalized.includes('breathless') ||
    normalized.includes('breathing') ||
    normalized.includes('shortness of breath') ||
    normalized.includes('saans') ||
    normalized.includes('sash') ||
    normalized.includes('wheezing') ||
    normalized.includes('oxygen') ||
    normalized.includes('choking') ||
    normalized.includes('stridor') ||
    normalized.includes('suffocation')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'general_oxygen',
      protocol_key: 'respiratory',
      matched_keywords: ['respiratory distress', 'hypoxic wheezing', 'dyspnea'],
      score: 85,
      explanation: 'Acute airway constriction and hypoxic stress. High-flow oxygen support with continuous SpO2 nebulization required.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 7. BURNS / FIRE / SCALDS
  if (
    normalized.includes('burn') ||
    normalized.includes('fire') ||
    normalized.includes('scald') ||
    normalized.includes('acid') ||
    normalized.includes('electric shock') ||
    normalized.includes('electrocution')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'adult_icu',
      protocol_key: 'burn',
      matched_keywords: ['thermal injury', 'burns / fluid loss risk'],
      score: 85,
      explanation: 'Thermal shock and airway edema risk. Fluid resuscitation using Parkland formula and sterile burn bay required.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 8. FRACTURES / BONE INJURY / FALL
  if (
    normalized.includes('fracture') ||
    normalized.includes('broken bone') ||
    normalized.includes('broken arm') ||
    normalized.includes('broken leg') ||
    normalized.includes('dislocation') ||
    normalized.includes('fall from height')
  ) {
    return {
      severity: 'YELLOW',
      recommended_ward: 'adult_icu',
      protocol_key: 'trauma',
      matched_keywords: ['orthopedic trauma', 'skeletal injury'],
      score: 75,
      explanation: 'Acute skeletal trauma requiring digital X-ray, neurovascular integrity check, and limb splinting.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 9. MATERNITY / PREGNANCY / LABOR
  if (
    normalized.includes('pregnancy') ||
    normalized.includes('pregnant') ||
    normalized.includes('labor') ||
    normalized.includes('delivery') ||
    normalized.includes('contractions') ||
    normalized.includes('water broke')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'general_oxygen',
      protocol_key: 'maternity',
      matched_keywords: ['active labor', 'obstetric emergency'],
      score: 88,
      explanation: 'Active labor or obstetric complication. Emergency delivery suite with neonatal resuscitation prep required.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 10. POISON / SNAKE BITE / OVERDOSE
  if (
    normalized.includes('snake') ||
    normalized.includes('poison') ||
    normalized.includes('overdose') ||
    normalized.includes('insecticide') ||
    normalized.includes('toxin')
  ) {
    return {
      severity: 'RED',
      recommended_ward: 'adult_icu',
      protocol_key: 'arrest',
      matched_keywords: ['toxic ingestion', 'envenomation risk'],
      score: 92,
      explanation: 'Acute toxidrome / venomous bite. Immediate antivenom titration or gastric lavage and ICU monitoring required.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 11. BLOOD REQUEST ONLY
  if (bloodNeeded) {
    return {
      severity: 'YELLOW',
      recommended_ward: 'adult_icu',
      protocol_key: 'trauma',
      matched_keywords: [`Blood group ${bloodNeeded.group}`, 'transfusion protocol'],
      score: 80,
      explanation: `Immediate transfusion requirement for group ${bloodNeeded.group}. Filtering hospitals with crossmatched reserve units.`,
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // 12. NEAREST HOSPITAL / GENERAL EMERGENCY
  if (
    normalized.includes('nearest') ||
    normalized.includes('closest') ||
    normalized.includes('hospital') ||
    normalized.includes('emergency') ||
    normalized.includes('doctor')
  ) {
    return {
      severity: 'YELLOW',
      recommended_ward: 'adult_icu',
      protocol_key: 'cardiac',
      matched_keywords: ['closest emergency triage'],
      score: 70,
      explanation: 'Proximity-optimized routing to the nearest hospital with 24/7 emergency response and staffed triage capacity.',
      offer_hold: true,
      blood_needed: bloodNeeded,
    };
  }

  // Default: General Emergency Clinical Assessment
  return {
    severity: 'YELLOW',
    recommended_ward: 'adult_icu',
    protocol_key: 'cardiac',
    matched_keywords: ['acute symptoms requiring evaluation'],
    score: 70,
    explanation: 'Clinical symptoms require urgent bedside assessment, continuous vital monitoring, and diagnostic imaging.',
    offer_hold: true,
    blood_needed: bloodNeeded,
  };
}
