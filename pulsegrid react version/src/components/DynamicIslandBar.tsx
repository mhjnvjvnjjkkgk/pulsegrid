import React from 'react';
import { Wifi, Battery, AlertTriangle, Zap, Shield, Stethoscope, User, Truck } from 'lucide-react';

interface DynamicIslandBarProps {
  activeRole: 'CITIZEN' | 'PARAMEDIC' | 'NURSE';
  onRoleChange: (role: 'CITIZEN' | 'PARAMEDIC' | 'NURSE') => void;
  onOpenDesk: () => void;
  isHolding: boolean;
  holdTimeLeft?: string;
  emergencyCategory?: string;
}

export const DynamicIslandBar: React.FC<DynamicIslandBarProps> = ({
  activeRole,
  onRoleChange,
  onOpenDesk,
  isHolding,
  holdTimeLeft,
  emergencyCategory = 'CARDIAC',
}) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 pointer-events-auto select-none">
      {/* Top Phone Chrome / Dynamic Island Container */}
      <div className="mx-auto max-w-md px-4 pt-2 pb-1">
        <div className="flex items-center justify-between text-xs text-[#888888] font-sans mb-1.5 px-2">
          <span className="font-black text-white text-sm tracking-tight">9:41</span>

          {/* Dynamic Island Capsule */}
          <div className="flex items-center gap-2 bg-[#111111] border border-[#222222] px-3 py-1 rounded-full shadow-lg transition-all duration-300">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isHolding ? 'bg-[#ff334b]' : 'bg-[#E2FF4D]'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isHolding ? 'bg-[#ff334b]' : 'bg-[#E2FF4D]'}`}></span>
            </span>
            <span className="text-[10px] font-black tracking-wider uppercase text-white">
              {isHolding ? `HOLD ACTIVE ${holdTimeLeft || '14:59'}` : 'LIVE SOS'}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-white/80">
            <Wifi className="w-3.5 h-3.5" />
            <Battery className="w-4 h-4" />
          </div>
        </div>

        {/* Role Controls */}
        <div className="flex items-center justify-end gap-2 mt-1">
          {/* Role Switcher Pill / Nurse Desk Shortcut */}
          <div className="flex items-center gap-1 bg-[#111111] border border-[#222222] p-0.5 rounded-full">
            <button
              onClick={() => onRoleChange('CITIZEN')}
              title="Citizen Mode"
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-black transition-all ${
                activeRole === 'CITIZEN'
                  ? 'bg-[#E2FF4D] text-black'
                  : 'text-[#888888] hover:text-white'
              }`}
            >
              <span className="hidden xs:inline">Citizen</span>
              <User className="w-3 h-3 xs:hidden" />
            </button>

            <button
              onClick={() => onRoleChange('PARAMEDIC')}
              title="108 Dispatch Mode"
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-black transition-all ${
                activeRole === 'PARAMEDIC'
                  ? 'bg-white text-black'
                  : 'text-[#888888] hover:text-white'
              }`}
            >
              <span className="hidden xs:inline">108 Unit</span>
              <Truck className="w-3 h-3 xs:hidden" />
            </button>

            <button
              onClick={onOpenDesk}
              title="Open Hospital Nurse Desk"
              className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black bg-[#1A1A1A] text-[#E2FF4D] border border-[#222222] hover:border-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black transition-all"
            >
              <Stethoscope className="w-3 h-3" />
              <span className="hidden xs:inline">Desk</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
