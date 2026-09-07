import React, { useState, useRef, useEffect } from 'react';
import { Hospital, LiveHold, ClinicalProtocol } from '../types';
import {
  AlertTriangle,
  CheckCircle2,
  Star,
  Lock,
  Phone,
  Truck,
  Navigation,
  ChevronUp,
  ChevronDown,
  Heart,
  Droplet,
  ShieldAlert,
  Activity,
  AlertOctagon,
  Copy,
  Check,
  X,
} from 'lucide-react';

interface HospitalPeekDrawerProps {
  hospital?: Hospital | null;
  onBookSlot: () => void;
  isHolding: boolean;
  activeHold?: LiveHold | null;
  onCancelHold?: () => void;
  onSimulateRedeem?: () => void;
  onOpenProtocolView: () => void;
  protocol: ClinicalProtocol;
  drawerExpanded: boolean;
  onDrawerExpandedChange: (expanded: boolean) => void;
  isVisible?: boolean;
  triageExplanation?: string;
  onClose?: () => void;
}

export const HospitalPeekDrawer: React.FC<HospitalPeekDrawerProps> = ({
  hospital,
  onBookSlot,
  isHolding,
  activeHold,
  onCancelHold,
  onOpenProtocolView,
  protocol,
  drawerExpanded,
  onDrawerExpandedChange,
  isVisible = true,
  triageExplanation,
  onClose,
}) => {
  const [copiedOtp, setCopiedOtp] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const touchStartYRef = useRef<number>(0);
  const lastScrollTopRef = useRef<number>(0);

  if (!hospital || !isVisible) {
    return null;
  }

  const availableBeds = hospital.wards.reduce((acc, w) => acc + w.available_now, 0);
  const primaryWard = hospital.wards.find((w) => w.ward_code === protocol.target_ward) || hospital.wards[0];

  const handleCopyOtp = (otp: string) => {
    navigator.clipboard?.writeText(otp);
    setCopiedOtp(true);
    setTimeout(() => setCopiedOtp(false), 2000);
  };

  // Touch tracking for drawer gestures
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartYRef.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentY = e.touches[0].clientY;
    const deltaY = currentY - touchStartYRef.current;

    // Swiping upward (scrolling down content) -> expand to 70%
    if (!drawerExpanded && deltaY < -15) {
      onDrawerExpandedChange(true);
    }
    // Swiping downward (scrolling back up) when at the top -> collapse back to peek
    else if (drawerExpanded && deltaY > 25) {
      if (!scrollContainerRef.current || scrollContainerRef.current.scrollTop <= 5) {
        onDrawerExpandedChange(false);
      }
    }
  };

  // Wheel tracking (mouse / trackpad) for expand and collapse
  const handleWheel = (e: React.WheelEvent) => {
    if (e.deltaY > 8 && !drawerExpanded) {
      onDrawerExpandedChange(true);
    } else if (e.deltaY < -8 && drawerExpanded) {
      if (!scrollContainerRef.current || scrollContainerRef.current.scrollTop <= 5) {
        onDrawerExpandedChange(false);
      }
    }
  };

  // Scroll listener inside container
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const currentTop = e.currentTarget.scrollTop;
    if (!drawerExpanded && currentTop > 8) {
      onDrawerExpandedChange(true);
    }
    lastScrollTopRef.current = currentTop;
  };

  return (
    <div
      className={`fixed left-0 right-0 bottom-0 z-40 max-w-md mx-auto pointer-events-auto transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${
        isVisible
          ? 'translate-y-0 opacity-100'
          : 'translate-y-full opacity-0 pointer-events-none'
      }`}
    >
      <div
        onWheel={handleWheel}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        style={{
          height: drawerExpanded ? '72vh' : '30vh',
          maxHeight: '74vh',
          transition: 'height 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
        className="bg-[#0e1726] rounded-t-[32px] border-t border-x border-[#1e3a5f] shadow-[0_-20px_60px_rgba(0,0,0,0.95)] flex flex-col overflow-hidden"
      >
        {/* Sleek Minimal Drag Handle Pill (Tap or scroll/swipe to expand/minimize) */}
        <div
          onClick={() => onDrawerExpandedChange(!drawerExpanded)}
          className="w-full pt-3 pb-2 flex-shrink-0 cursor-pointer flex items-center justify-center group touch-none select-none"
        >
          <div className="w-12 h-1.5 rounded-full bg-[#334155] group-hover:bg-[#E2FF4D] transition-colors" />
        </div>

        {/* Scrollable Content Container */}
        <div
          ref={scrollContainerRef}
          onScroll={handleScroll}
          style={{
            WebkitOverflowScrolling: 'touch',
            touchAction: 'pan-y',
            overscrollBehaviorY: 'contain',
          }}
          className="flex-1 px-4 pt-0 pb-3 overflow-y-auto no-scrollbar select-text space-y-3"
        >
          {/* Header Row: Hospital Name, ETA & Distance */}
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5 truncate">
                <h2 className="font-black text-base sm:text-lg text-white tracking-tight uppercase italic leading-tight truncate">
                  {hospital.short_name || hospital.name}
                </h2>
                <CheckCircle2 className="w-4 h-4 text-[#E2FF4D] fill-[#E2FF4D]/20 flex-shrink-0" />
              </div>
              <p className="text-[11px] text-[#8ab4f8] font-medium truncate mt-0.5">
                {hospital.corridor_name || hospital.address}
              </p>
            </div>

            {/* Live Metrics Pill & Close Button */}
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <span className="px-2 py-1 rounded-lg bg-[#14233c] border border-[#22395d] text-[10px] font-black text-[#E2FF4D] flex items-center gap-1">
                <Navigation className="w-3 h-3" />
                {hospital.eta_minutes} MIN
              </span>
              <span className="px-2 py-1 rounded-lg bg-[#14233c] border border-[#22395d] text-[10px] font-black text-white">
                {hospital.distance_km} KM
              </span>
              {onClose && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onClose();
                  }}
                  title="Deselect Hospital"
                  className="p-1 rounded-lg bg-[#14233c] hover:bg-[#ff334b]/20 hover:text-[#ff334b] text-gray-400 border border-[#22395d] transition-colors cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Condition / Recommended Ward Tag */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="px-2 py-0.5 rounded-md bg-[#ff334b]/15 border border-[#ff334b]/30 text-[#ff334b] text-[10px] font-black tracking-wide uppercase">
              {protocol.priority_code}
            </span>
            <span className="px-2 py-0.5 rounded-md bg-[#E2FF4D]/10 border border-[#E2FF4D]/20 text-[#E2FF4D] text-[10px] font-bold">
              {primaryWard.label}: {primaryWard.available_now} Beds Available
            </span>
          </div>

          {/* If HOLD IS ACTIVE & Drawer is Expanded: Detailed GPS Soft-Lock Card */}
          {isHolding && activeHold && drawerExpanded && (
            <div className="bg-[#111c2e] border-2 border-[#E2FF4D] rounded-2xl p-3 shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#22395d] pb-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E2FF4D] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#E2FF4D]"></span>
                  </span>
                  <div>
                    <span className="text-[11px] font-black text-[#E2FF4D] tracking-wider uppercase block">
                      15-MIN GPS SOFT LOCK ACTIVE
                    </span>
                    <span className="text-[9px] text-[#8ab4f8] font-bold">
                      Ward: {activeHold.ward_label} • Bed Reserved
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="font-mono text-base font-black text-white">
                    {Math.floor(activeHold.seconds_left / 60)}:
                    {(activeHold.seconds_left % 60).toString().padStart(2, '0')}
                  </span>
                  <span className="text-[8px] font-bold text-[#E2FF4D] block uppercase">
                    GPS TRACKED
                  </span>
                </div>
              </div>

              {/* 4-Digit Gate OTP Display */}
              <div className="flex items-center justify-between bg-black/50 border border-[#22395d] rounded-xl p-2.5">
                <div>
                  <span className="text-[9px] font-bold text-[#8ab4f8] block uppercase tracking-wider">
                    GATE CHECK-IN CODE (OTP)
                  </span>
                  <span className="text-[9px] text-[#E2FF4D] font-bold">
                    Show to ER Nurse upon arrival
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <div className="flex gap-1">
                    {activeHold.otp_code.split('').map((char, i) => (
                      <span
                        key={i}
                        className="w-6 h-8 rounded-lg bg-[#14233c] border border-[#334e77] text-white font-mono font-black text-sm flex items-center justify-center"
                      >
                        {char}
                      </span>
                    ))}
                  </div>

                  <button
                    onClick={() => handleCopyOtp(activeHold.otp_code)}
                    className="p-1.5 rounded-lg bg-[#1e3455] text-xs font-bold text-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black transition-colors cursor-pointer"
                    title="Copy OTP"
                  >
                    {copiedOtp ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* EXPANDED SECTION: Emergency Clinical Issue Assessment & Protocols */}
          {drawerExpanded && (
            <div className="pt-2 border-t border-[#1e3a5f] space-y-3 select-text">
              {/* Clinical Issue Assessment Card */}
              <div className="bg-[#111f38] border border-[#1e3a5f] rounded-2xl p-3.5 space-y-2">
                <div className="flex items-center justify-between border-b border-[#1e3a5f] pb-2">
                  <div className="flex items-center gap-1.5">
                    <AlertOctagon className="w-4 h-4 text-[#ff334b]" />
                    <span className="text-xs font-black text-white uppercase tracking-wide">
                      CLINICAL ASSESSMENT & DIAGNOSIS
                    </span>
                  </div>
                  <span className="text-[9px] font-bold text-[#E2FF4D] bg-[#E2FF4D]/10 px-2 py-0.5 rounded border border-[#E2FF4D]/30">
                    LIVE TRIAGE
                  </span>
                </div>

                <div>
                  <div className="text-xs font-black text-[#E2FF4D] mb-1">
                    {protocol.title} • {protocol.esi_acuity}
                  </div>
                  <p className="text-[11px] text-[#cbd5e1] leading-relaxed">
                    {triageExplanation ||
                      'Symptoms indicate an acute clinical emergency requiring monitored resuscitation and continuous hemodynamic telemetry.'}
                  </p>
                </div>

                {/* Why this hospital was chosen */}
                <div className="bg-[#0a1424] border border-[#1e3a5f] rounded-xl p-2.5 text-[11px] text-[#8ab4f8]">
                  <span className="text-white font-bold block mb-0.5">
                    Why {hospital.short_name || hospital.name}?
                  </span>
                  Confirmed {primaryWard.available_now} staffed bed(s) in {primaryWard.label}. 
                  {hospital.has_cath_lab ? ' Active 24/7 Cath Lab.' : ''} 
                  {hospital.is_trauma_center ? ' Level-1 Trauma bay ready.' : ''} ETA is only {hospital.eta_minutes} mins ({hospital.distance_km} km).
                </div>

                {/* Immediate First-Aid Posture & Action */}
                {protocol.immediate_action && (
                  <div className="bg-[#0d1b2a] border border-[#234570] rounded-xl p-2.5">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-black text-[#E2FF4D] uppercase">
                        {protocol.immediate_action.title}
                      </span>
                      {protocol.immediate_action.angle_badge && (
                        <span className="text-[9px] font-black text-black bg-[#E2FF4D] px-2 py-0.5 rounded">
                          {protocol.immediate_action.angle_badge}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-[#e2e8f0] leading-relaxed">
                      {protocol.immediate_action.instruction}
                    </p>
                  </div>
                )}

                {/* Critical DO NOTs */}
                {protocol.do_nots && protocol.do_nots.length > 0 && (
                  <div className="pt-1.5 border-t border-[#1e3a5f]">
                    <span className="text-[10px] font-black text-[#ff334b] uppercase block mb-1">
                      CRITICAL DO NOT DOs
                    </span>
                    <div className="space-y-1 text-[10px] text-[#e2e8f0]">
                      {protocol.do_nots.map((dn, i) => (
                        <div key={i} className="flex items-center gap-1.5">
                          <span className="text-[#ff334b] font-black">✕</span>
                          <span>{dn}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Availability Highlights 3-Grid */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-[#111f38] border border-[#1e3a5f] rounded-xl p-2">
                  <span className="text-[8px] text-[#8ab4f8] font-bold uppercase block">RECOMMENDED</span>
                  <span className="text-xs sm:text-sm font-black text-white block my-0.5">
                    {primaryWard.available_now} Beds
                  </span>
                  <span className="text-[8px] text-[#888888] font-bold uppercase truncate block">
                    {primaryWard.label}
                  </span>
                </div>

                <div className="bg-[#111f38] border border-[#1e3a5f] rounded-xl p-2">
                  <span className="text-[8px] text-[#888888] font-bold uppercase block">TOTAL BEDS</span>
                  <span className="text-xs sm:text-sm font-black text-[#E2FF4D] block my-0.5">
                    {availableBeds} Free
                  </span>
                  <span className="text-[8px] text-[#888888] font-bold uppercase block">All Wards</span>
                </div>

                <div className="bg-[#111f38] border border-[#1e3a5f] rounded-xl p-2">
                  <span className="text-[8px] text-[#8ab4f8] font-bold uppercase block">TRAUMA LEVEL</span>
                  <span className="text-[10px] font-black text-white block my-0.5 truncate">
                    {hospital.is_trauma_center ? 'Level-1 Ready' : 'Civic Unit'}
                  </span>
                  <span className="text-[8px] text-[#E2FF4D] font-bold uppercase block">Verified</span>
                </div>
              </div>

              {/* Ward Capacity Breakdown */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-black text-white uppercase tracking-wider">
                    WARD CAPACITY BREAKDOWN
                  </span>
                  <span className="text-[9px] text-[#8ab4f8] font-mono">LIVE TELEMETRY</span>
                </div>

                <div className="space-y-1.5">
                  {hospital.wards.map((ward) => (
                    <div
                      key={ward.ward_code}
                      className="flex items-center justify-between bg-[#111f38] border border-[#1e3a5f] rounded-xl px-3 py-2 text-xs"
                    >
                      <div>
                        <div className="text-white font-bold text-xs uppercase">{ward.label}</div>
                        <div className="text-[9px] text-[#8ab4f8]">
                          Staffed: {ward.total_staffed} | Physical: {ward.total_physical}
                        </div>
                      </div>

                      <div className="text-right">
                        <span
                          className={`text-xs font-black ${
                            ward.available_now > 0 ? 'text-[#E2FF4D]' : 'text-[#ff334b]'
                          }`}
                        >
                          {ward.available_now} Free
                        </span>
                        <span className="text-[9px] text-[#888888] block font-bold">
                          {ward.held_now} Held
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Blood Bank stock */}
              {hospital.blood_summary.length > 0 && (
                <div>
                  <span className="text-[10px] font-black text-white uppercase tracking-wider block mb-1.5">
                    BLOOD BANK STOCK
                  </span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {hospital.blood_summary.map((blood, idx) => (
                      <div
                        key={idx}
                        className="bg-[#111f38] border border-[#1e3a5f] rounded-xl p-2 text-xs flex items-center justify-between"
                      >
                        <div className="flex items-center gap-1.5 text-white">
                          <Droplet className="w-3 h-3 fill-[#ff334b] text-[#ff334b]" />
                          <span className="font-bold text-[11px]">
                            {blood.blood_group} {blood.component}
                          </span>
                        </div>
                        <span className="text-[#E2FF4D] font-black text-xs">
                          {blood.units_free_now} Units
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* STICKY FOOTER ACTION BAR - Always pinned at bottom in same position */}
        <div className="flex-shrink-0 px-4 pt-2.5 pb-4 bg-[#0a121f] border-t border-[#1e3a5f] shadow-[0_-8px_20px_rgba(0,0,0,0.6)]">
          {isHolding && activeHold ? (
            /* When Soft Lock is Active: */
            !drawerExpanded ? (
              /* When in 30% view: User asked: "when its active, when i scroll back and move from 70% to 30%, only the name, condition, and timer and otp should be visible and should take the place of the book button" */
              <div className="flex items-center justify-between bg-[#111f38] border-2 border-[#E2FF4D] rounded-2xl p-2.5">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E2FF4D] opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-[#E2FF4D]"></span>
                    </span>
                    <span className="text-[11px] font-black text-[#E2FF4D] uppercase tracking-wider">
                      {protocol.priority_code} • {Math.floor(activeHold.seconds_left / 60)}:
                      {(activeHold.seconds_left % 60).toString().padStart(2, '0')}
                    </span>
                  </div>
                  <span className="text-[9px] text-[#8ab4f8] font-bold block mt-0.5">
                    {hospital.short_name || hospital.name} • OTP: <strong className="text-white tracking-widest">{activeHold.otp_code}</strong>
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopyOtp(activeHold.otp_code)}
                    className="p-1.5 rounded-lg bg-[#1e3455] text-xs font-bold text-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black transition-colors cursor-pointer"
                    title="Copy OTP"
                  >
                    {copiedOtp ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    onClick={onCancelHold}
                    className="py-1.5 px-3 rounded-xl bg-[#ff334b]/20 border border-[#ff334b]/40 text-[#ff334b] text-[10px] font-black hover:bg-[#ff334b] hover:text-white transition-colors uppercase cursor-pointer"
                  >
                    RELEASE
                  </button>
                </div>
              </div>
            ) : (
              /* When in 70% view: Sticky bottom has Release and Call buttons (No nurse desk admit button!) */
              <div className="flex gap-2">
                <button
                  onClick={onCancelHold}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-[#1e293b] border border-[#ff334b]/40 text-[#ff334b] text-xs font-black tracking-wider hover:bg-[#ff334b] hover:text-white transition-colors uppercase cursor-pointer text-center"
                >
                  RELEASE 15-MIN HOLD
                </button>
                <a
                  href={`tel:${hospital.phone.replace(/[^0-9+]/g, '')}`}
                  className="py-2.5 px-5 rounded-xl bg-[#E2FF4D] text-black text-xs font-black tracking-tight hover:bg-white transition-colors uppercase flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Phone className="w-3.5 h-3.5 fill-current" />
                  <span>CALL ER</span>
                </a>
              </div>
            )
          ) : (
            /* When Hold is NOT Active: Sticky Book My Slot & Action Buttons */
            <div className="space-y-2">
              <button
                onClick={onBookSlot}
                className="w-full py-2.5 px-4 rounded-full bg-[#E2FF4D] text-black font-black text-xs sm:text-sm tracking-tight hover:bg-white transition-colors flex items-center justify-center gap-2 uppercase shadow-xl cursor-pointer active:scale-[0.98]"
              >
                <Lock className="w-3.5 h-3.5 text-black" />
                <span>BOOK MY SLOT AND START ➔</span>
              </button>

              <div className="grid grid-cols-2 gap-2">
                {/* Ambulance 108 */}
                <a
                  href="tel:108"
                  className="py-2 px-3 rounded-xl bg-[#141f33] border border-[#ff334b]/40 hover:bg-[#ff334b] hover:text-white text-[#ff334b] font-black text-[11px] uppercase tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                >
                  <Truck className="w-3.5 h-3.5" />
                  <span>Ambulance (108)</span>
                </a>

                {/* Call Hospital */}
                <a
                  href={`tel:${hospital.phone.replace(/[^0-9+]/g, '')}`}
                  className="py-2 px-3 rounded-xl bg-[#141f33] border border-[#1e3a5f] hover:bg-white hover:text-black text-white font-black text-[11px] uppercase tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                >
                  <Phone className="w-3.5 h-3.5 text-[#E2FF4D]" />
                  <span>Call Hospital</span>
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
