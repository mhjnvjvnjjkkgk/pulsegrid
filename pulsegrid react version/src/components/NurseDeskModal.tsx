import React, { useState } from 'react';
import { Hospital, LiveHold, WardCode } from '../types';
import { X, Check, AlertTriangle, ShieldCheck, Stethoscope, Clock, UserCheck, RefreshCw } from 'lucide-react';

interface NurseDeskModalProps {
  hospital: Hospital;
  onClose: () => void;
  onUpdateWardCounter: (wardCode: WardCode, delta: number) => void;
  onUpdateStaffedBeds: (wardCode: WardCode, newStaffed: number) => void;
  inboundQueue: LiveHold[];
  onRedeemHold: (otpCode: string) => boolean;
}

export const NurseDeskModal: React.FC<NurseDeskModalProps> = ({
  hospital,
  onClose,
  onUpdateWardCounter,
  onUpdateStaffedBeds,
  inboundQueue,
  onRedeemHold,
}) => {
  const [otpInput, setOtpInput] = useState(['', '', '', '']);
  const [verificationFeedback, setVerificationFeedback] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const handleOtpChange = (index: number, val: string) => {
    const cleanVal = val.replace(/[^0-9]/g, '').slice(-1);
    const newOtp = [...otpInput];
    newOtp[index] = cleanVal;
    setOtpInput(newOtp);

    // Auto advance focus
    if (cleanVal && index < 3) {
      const nextInput = document.getElementById(`otp-nurse-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleVerify = () => {
    const fullOtp = otpInput.join('');
    if (fullOtp.length !== 4) {
      setVerificationFeedback({
        success: false,
        message: 'Please enter a complete 4-digit OTP.',
      });
      return;
    }

    const success = onRedeemHold(fullOtp);
    if (success) {
      setVerificationFeedback({
        success: true,
        message: `OTP ${fullOtp} VERIFIED. Patient Admitted to Bed.`,
      });
      setOtpInput(['', '', '', '']);
    } else {
      setVerificationFeedback({
        success: false,
        message: `No active reservation found for OTP: ${fullOtp}.`,
      });
    }

    setTimeout(() => {
      setVerificationFeedback(null);
    }, 4000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-[#0A0A0A]/95 text-white select-none backdrop-blur-2xl p-3 sm:p-5 max-w-2xl mx-auto font-sans">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-[#222222] pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-[#E2FF4D] text-black flex items-center justify-center shadow-md">
            <Stethoscope className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-black text-base sm:text-lg text-white uppercase italic tracking-tight">{hospital.name}</h2>
              <span className="bg-[#1A1A1A] border border-[#222222] text-[#E2FF4D] text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                NURSE DESK
              </span>
            </div>
            <p className="text-xs text-[#888888] font-bold">
              Emergency Ward Resuscitation & Rapid Bed Inventory System
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-8 h-8 rounded-full bg-[#111111] border border-[#222222] flex items-center justify-center text-white/70 hover:text-white hover:bg-[#222222] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* RAPID CHECK-IN 4-DIGIT OTP BOX */}
      <div className="bg-[#111111] rounded-3xl p-4 mb-4 border border-[#222222] shadow-xl">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-1.5">
            <UserCheck className="w-4 h-4 text-[#E2FF4D]" />
            <span>RAPID GATE CHECK-IN (ADMIT PATIENT)</span>
          </span>
          <span className="text-[10px] font-bold text-[#888888]">Glove-Friendly Touch Scanner</span>
        </div>

        <div className="flex items-center justify-between gap-2.5 flex-wrap">
          <div className="flex gap-2">
            {[0, 1, 2, 3].map((idx) => (
              <input
                key={idx}
                id={`otp-nurse-${idx}`}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={otpInput[idx]}
                onChange={(e) => handleOtpChange(idx, e.target.value)}
                placeholder="•"
                className="w-12 h-14 rounded-2xl bg-black border-2 border-[#333333] text-white font-mono font-black text-2xl text-center focus:outline-none focus:border-[#E2FF4D] shadow-inner"
              />
            ))}
          </div>

          <button
            onClick={handleVerify}
            className="flex-1 min-w-[140px] h-14 rounded-2xl bg-white text-black font-black text-sm tracking-tight uppercase flex items-center justify-center gap-2 hover:bg-[#E2FF4D] active:scale-95 shadow-lg transition-all cursor-pointer"
          >
            <Check className="w-5 h-5 stroke-[3]" />
            <span>VERIFY & ADMIT</span>
          </button>
        </div>

        {verificationFeedback && (
          <div
            className={`mt-3 p-3 rounded-2xl text-xs font-bold border flex items-center gap-2 ${
              verificationFeedback.success
                ? 'bg-[#1A1A1A] border-[#E2FF4D] text-[#E2FF4D]'
                : 'bg-[#1A1A1A] border-[#ff334b] text-[#ff334b]'
            }`}
          >
            <span>{verificationFeedback.success ? '✓' : '⚠️'}</span>
            <span>{verificationFeedback.message}</span>
          </div>
        )}
      </div>

      {/* 4 WARD COUNTERS (72px GLOVE-FRIENDLY TOUCH TARGETS) */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-xs font-black text-white uppercase tracking-wider">
            WARD CAPACITY — 1-TAP [ + ] / [ − ] UPDATE
          </span>
          <span className="text-[10px] font-bold text-[#E2FF4D] uppercase">
            Ghost Gap = Unstaffed Physical Beds
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {hospital.wards.map((ward) => (
            <div
              key={ward.ward_code}
              className="bg-[#111111] rounded-3xl p-3.5 border border-[#222222] relative overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between border-b border-[#222222] pb-2 mb-2.5">
                <span className="font-black text-sm text-white uppercase tracking-tight">
                  {ward.label}
                </span>
                {ward.ghost_gap > 0 && (
                  <span className="text-[10px] font-bold text-[#E2FF4D] bg-[#1A1A1A] px-2.5 py-0.5 rounded-full border border-[#222222]">
                    ⌀ {ward.ghost_gap} Ghost Beds
                  </span>
                )}
              </div>

              {/* Counts & Buttons */}
              <div className="flex items-center justify-between gap-3">
                {/* Large buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onUpdateWardCounter(ward.ward_code, -1)}
                    disabled={ward.occupied <= 0}
                    title="Discharge / Patient Transferred (-1)"
                    className="w-14 h-14 rounded-2xl bg-[#1A1A1A] border border-[#222222] text-white font-mono font-black text-2xl flex items-center justify-center hover:bg-[#ff334b] hover:text-white active:scale-90 transition-all disabled:opacity-25 disabled:cursor-not-allowed cursor-pointer"
                  >
                    −
                  </button>

                  <button
                    onClick={() => onUpdateWardCounter(ward.ward_code, 1)}
                    disabled={ward.occupied >= ward.total_staffed}
                    title="Admit Patient (+1 Occupied)"
                    className="w-14 h-14 rounded-2xl bg-[#1A1A1A] border border-[#222222] text-[#E2FF4D] font-mono font-black text-2xl flex items-center justify-center hover:bg-[#E2FF4D] hover:text-black active:scale-90 transition-all disabled:opacity-25 disabled:cursor-not-allowed cursor-pointer"
                  >
                    +
                  </button>
                </div>

                {/* Capacity breakdown */}
                <div className="text-right flex-1">
                  <div className="text-xl font-black text-white tracking-tight">
                    {ward.occupied} <span className="text-xs text-[#888888] font-bold">/ {ward.total_staffed}</span>
                  </div>
                  <div className="text-[10px] text-[#666666] uppercase font-bold tracking-wider">OCCUPIED / STAFFED</div>

                  <div className="flex items-center justify-end gap-2 mt-1">
                    <span className="text-xs font-black text-[#E2FF4D]">
                      {ward.available_now} Free
                    </span>
                    <span className="text-xs text-[#888888] font-bold">
                      {ward.held_now} Held
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* LIVE INBOUND PATIENTS QUEUE */}
      <div className="bg-[#111111] rounded-3xl p-4 border border-[#222222]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-[#E2FF4D]" />
            <span>LIVE INBOUND QUEUE ({inboundQueue.length} EN ROUTE)</span>
          </span>
          <span className="text-[10px] font-bold text-[#888888]">15-Min Dynamic GPS Monitored</span>
        </div>

        {inboundQueue.length === 0 ? (
          <div className="p-6 rounded-2xl bg-black border border-[#222222] text-center text-xs text-[#888888] font-bold">
            No active inbound ambulance holds. All quiet at ER reception.
          </div>
        ) : (
          <div className="space-y-2">
            {inboundQueue.map((hold) => (
              <div
                key={hold.hold_id}
                className="flex items-center justify-between bg-black border border-[#222222] p-3.5 rounded-2xl text-xs"
              >
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-0.5 rounded-full bg-[#1A1A1A] border border-[#ff334b]/40 text-[#ff334b] font-black text-[9px] uppercase">
                    {hold.severity}
                  </span>
                  <div>
                    <div className="text-white font-black flex items-center gap-1.5 uppercase">
                      <span>OTP: <strong className="text-[#E2FF4D]">{hold.otp_code}</strong></span>
                      <span className="text-[#444444]">•</span>
                      <span>{hold.ward_label}</span>
                    </div>
                    <div className="text-[10px] text-[#888888] font-bold">
                      {hold.requester_name} ({hold.requester_phone}) • {hold.hold_type}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-black text-[#E2FF4D]">
                    ⏱ {Math.floor(hold.seconds_left / 60)}:
                    {(hold.seconds_left % 60).toString().padStart(2, '0')}
                  </span>
                  <button
                    onClick={() => {
                      onRedeemHold(hold.otp_code);
                      setVerificationFeedback({
                        success: true,
                        message: `Admitted ${hold.requester_name} with OTP ${hold.otp_code}`,
                      });
                    }}
                    className="px-3 py-1.5 rounded-xl bg-[#E2FF4D] text-black hover:bg-white text-[10px] font-black uppercase transition-all cursor-pointer"
                  >
                    ADMIT
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
