import React, { useState } from 'react';
import { Hospital, ClinicalProtocol, LiveHold } from '../types';
import {
  X,
  ShieldAlert,
  Heart,
  AlertOctagon,
  CheckSquare,
  Square,
  Lock,
  Truck,
  Phone,
  ArrowLeft,
  Activity,
  Flame,
  Wind,
  Droplets,
  AlertTriangle,
} from 'lucide-react';

interface ClinicalProtocolSheetProps {
  hospital: Hospital;
  protocol: ClinicalProtocol;
  onClose: () => void;
  onBookSlot: () => void;
  isHolding: boolean;
  activeHold?: LiveHold | null;
}

export const ClinicalProtocolSheet: React.FC<ClinicalProtocolSheetProps> = ({
  hospital,
  protocol,
  onClose,
  onBookSlot,
  isHolding,
  activeHold,
}) => {
  const [symptoms, setSymptoms] = useState(protocol.rapid_scan_symptoms);

  const toggleSymptom = (id: string) => {
    setSymptoms((prev) =>
      prev.map((s) => (s.id === id ? { ...s, checked: !s.checked } : s))
    );
  };

  return (
    <div
      style={{
        WebkitOverflowScrolling: 'touch',
        touchAction: 'pan-y',
        overscrollBehaviorY: 'contain',
      }}
      className="fixed inset-0 z-50 overflow-y-auto bg-[#0A0A0A] text-white animate-fadeIn max-w-md mx-auto font-sans select-text"
    >
      {/* Top Phone Chrome bar */}
      <div className="sticky top-0 z-30 bg-[#0A0A0A]/95 border-b border-[#222222] px-4 pt-3 pb-2 backdrop-blur-xl">
        <div className="flex items-center justify-between text-xs text-[#888888] mb-1.5">
          <span className="font-black text-white text-sm">9:41</span>
          <div className="flex items-center gap-1.5 bg-[#111111] border border-[#ff334b]/40 px-3 py-1 rounded-full text-[#ff334b] font-black text-[9px] uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#ff334b] animate-ping"></span>
            <span>TACTICAL SOS</span>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-[#111111] border border-[#222222] flex items-center justify-center text-white/70 hover:text-white hover:bg-[#222222] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Spatial Radar Tag */}
        <div className="flex items-center justify-between text-[10px] font-bold tracking-tight">
          <div className="flex items-center gap-1 text-[#888888]">
            <Activity className="w-3.5 h-3.5 text-[#E2FF4D]" />
            <span>RADAR: {hospital.short_name} ({hospital.distance_km} KM)</span>
          </div>
          <span className="text-[#E2FF4D] font-black">ETA ~{hospital.eta_minutes} MIN</span>
        </div>
      </div>

      <div className="p-4 space-y-3.5 pb-40">
        {/* Hospital Locked Badge Card */}
        <div className="bg-[#111111] rounded-3xl p-3.5 border border-[#222222] shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-2xl bg-[#E2FF4D] text-black flex items-center justify-center shadow-md">
                <Heart className="w-5 h-5 fill-black stroke-black" />
              </div>
              <div>
                <h3 className="font-black text-sm text-white uppercase italic tracking-tight">{hospital.name}</h3>
                <span className="text-[10px] font-bold text-[#E2FF4D] flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#E2FF4D]"></span>
                  Cardiac Care Bay Ready
                </span>
              </div>
            </div>

            <div className="bg-[#1A1A1A] border border-[#222222] text-[#E2FF4D] text-[9px] font-black px-2.5 py-1 rounded-full uppercase tracking-wider">
              ICU LOCKED
            </div>
          </div>
        </div>

        {/* Priority Banner */}
        <div className="bg-[#111111] border border-[#ff334b]/40 rounded-2xl p-3">
          <div className="flex items-center gap-2 text-xs font-black text-[#ff334b] uppercase tracking-wide">
            <AlertOctagon className="w-4 h-4 flex-shrink-0" />
            <span>{protocol.esi_acuity}</span>
          </div>
        </div>

        {/* Title and Code Header */}
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">❤️</span>
            <h1 className="font-black text-xl sm:text-2xl text-white tracking-tighter uppercase italic leading-none">
              {protocol.title}
            </h1>
          </div>
          <div className="text-[10px] font-black text-[#E2FF4D] tracking-wider mt-1.5 uppercase">
            CLINICAL PRIORITY CODE: {protocol.priority_code}
          </div>
        </div>

        {/* Section: CHECK PATIENT STATUS (RAPID SCAN) */}
        <div className="bg-[#111111] rounded-3xl p-3.5 border border-[#222222]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-1.5">
              <span>CHECK PATIENT STATUS</span>
            </span>
            <span className="text-[9px] font-black bg-[#1A1A1A] text-[#E2FF4D] px-2.5 py-0.5 rounded-full border border-[#222222] uppercase tracking-wider">
              RAPID SCAN
            </span>
          </div>

          {/* 4 Interactive Chips Grid */}
          <div className="grid grid-cols-2 gap-2">
            {symptoms.map((item) => (
              <button
                key={item.id}
                onClick={() => toggleSymptom(item.id)}
                className={`p-2.5 rounded-2xl text-left text-xs transition-all border flex items-start gap-2 ${
                  item.checked
                    ? 'bg-white border-white text-black font-black shadow-md'
                    : 'bg-[#1A1A1A] border-[#222222] text-[#888888] font-bold hover:text-white'
                }`}
              >
                <div className="mt-0.5">
                  {item.checked ? (
                    <CheckSquare className="w-3.5 h-3.5 text-black" />
                  ) : (
                    <Square className="w-3.5 h-3.5 text-[#555555]" />
                  )}
                </div>
                <span className="text-[11px] leading-tight">{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Section: IMMEDIATE ACTION (SEMI-FOWLER 45° POSITION) */}
        <div className="bg-[#111111] rounded-3xl p-4 border-2 border-[#E2FF4D] shadow-2xl">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-black text-[#E2FF4D] uppercase tracking-wider flex items-center gap-1.5">
              <span>⚡ IMMEDIATE ACTION</span>
            </span>
            <span className="text-[9px] font-black bg-[#E2FF4D] text-black px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              {protocol.immediate_action.badge}
            </span>
          </div>

          <div className="flex items-start gap-3 bg-black border border-[#222222] rounded-2xl p-3">
            {protocol.immediate_action.angle_badge && (
              <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-[#E2FF4D] text-black flex flex-col items-center justify-center font-black text-xs text-center leading-none shadow-sm">
                <span>45°</span>
                <span className="text-[8px] font-bold mt-0.5">ANGLE</span>
              </div>
            )}

            <div>
              <h4 className="font-black text-xs text-white uppercase">
                {protocol.immediate_action.title}
              </h4>
              <p className="text-[11px] text-[#aaaaaa] leading-relaxed mt-1 font-medium">
                {protocol.immediate_action.instruction}
              </p>
            </div>
          </div>
        </div>

        {/* Section: EMERGENCY PROTOCOL STEPS */}
        <div className="bg-[#111111] rounded-3xl p-3.5 border border-[#222222]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-black text-white uppercase tracking-wider">
              EMERGENCY PROTOCOL STEPS
            </span>
            <span className="text-[10px] font-bold text-[#888888] uppercase">
              {protocol.protocol_steps.length} CLINICAL POINTS
            </span>
          </div>

          <div className="space-y-2">
            {protocol.protocol_steps.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2.5 text-xs text-white bg-black border border-[#222222] p-2.5 rounded-2xl"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#E2FF4D] text-black font-black text-[10px] flex items-center justify-center">
                  {idx + 1}
                </span>
                <span className="leading-snug pt-0.5 text-[11px] font-medium">{step}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Section: CRITICAL DO NOT DOs */}
        <div className="bg-[#111111] border border-[#ff334b]/40 rounded-3xl p-3.5">
          <span className="text-xs font-black text-[#ff334b] uppercase block mb-2 tracking-wider">
            CRITICAL DO NOT DOs
          </span>
          <div className="space-y-1.5 text-xs text-white">
            {protocol.do_nots.map((d, i) => (
              <div key={i} className="text-[11px] leading-tight font-medium flex items-center gap-1.5">
                <span className="text-[#ff334b] font-black">✕</span>
                <span>{d}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Calming Script for Bystanders */}
        <div className="bg-[#111111] border border-[#222222] rounded-3xl p-3.5 text-xs">
          <span className="text-[10px] text-[#E2FF4D] uppercase block font-black mb-1.5 tracking-wider">
            BYSTANDER CALMING SCRIPT (READ ALOUD)
          </span>
          <p className="italic text-[#cccccc] text-[11px] font-medium leading-relaxed">
            "{protocol.calming_script}"
          </p>
        </div>
      </div>

      {/* Sticky Bottom Action Buttons */}
      <div className="fixed bottom-0 left-0 right-0 z-40 max-w-md mx-auto p-4 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A]/95 to-transparent backdrop-blur-xl border-t border-[#222222]">
        <button
          onClick={onBookSlot}
          className="relative w-full py-4 px-4 rounded-full bg-white text-black font-black text-sm sm:text-base tracking-tight hover:bg-[#E2FF4D] transition-colors flex items-center justify-center gap-2 uppercase shadow-xl active:scale-[0.98] cursor-pointer"
        >
          <Lock className="w-4 h-4 text-black" />
          <span>{isHolding ? 'VIEW CURRENT ACTIVE HOLD ➔' : 'BOOK MY SLOT AND START ➔'}</span>
        </button>

        <div className="grid grid-cols-2 gap-2.5 mt-2.5">
          <a
            href="tel:108"
            className="py-3 px-3 rounded-2xl bg-[#111111] border border-[#ff334b]/40 hover:bg-[#ff334b] hover:text-white text-[#ff334b] font-black text-xs uppercase tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer"
          >
            <Truck className="w-3.5 h-3.5" />
            <span>Ambulance (108)</span>
          </a>

          <a
            href={`tel:${hospital.phone.replace(/[^0-9+]/g, '')}`}
            className="py-3 px-3 rounded-2xl bg-[#111111] border border-[#222222] hover:bg-white hover:text-black text-white font-black text-xs uppercase tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer"
          >
            <Phone className="w-3.5 h-3.5 text-[#E2FF4D]" />
            <span>Call Hospital</span>
          </a>
        </div>
      </div>
    </div>
  );
};
