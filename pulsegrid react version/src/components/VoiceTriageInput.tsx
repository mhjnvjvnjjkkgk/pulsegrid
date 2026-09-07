import React, { useRef, useState } from 'react';
import { Mic, MicOff, Search, X, MapPin, Droplet, Building2, ArrowRight } from 'lucide-react';

interface VoiceTriageInputProps {
  currentQuery: string;
  onQueryChange: (query: string) => void;
  onSearchSubmit: (query: string) => void;
  isListening: boolean;
  onToggleListening: () => void;
  isSearchActive: boolean;
  onClearSearch?: () => void;
  isVisible?: boolean;
}

const COMMON_BLOOD_GROUPS = ['O+', 'B+', 'A+', 'AB+', 'O-', 'A-'];

export const VoiceTriageInput: React.FC<VoiceTriageInputProps> = ({
  currentQuery,
  onQueryChange,
  onSearchSubmit,
  isListening,
  onToggleListening,
  isSearchActive,
  onClearSearch,
  isVisible = true,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [showBloodPicker, setShowBloodPicker] = useState(false);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (currentQuery.trim()) {
      onSearchSubmit(currentQuery.trim());
      inputRef.current?.blur();
    }
  };

  const handleBloodGroupSelect = (bg: string) => {
    const query = `${bg} Blood`;
    onQueryChange(query);
    onSearchSubmit(query);
    setShowBloodPicker(false);
  };

  const handleFocusBloodInput = () => {
    setShowBloodPicker((prev) => !prev);
    inputRef.current?.focus();
  };

  const handleNearestHospital = () => {
    onQueryChange('Nearest Hospital');
    onSearchSubmit('Nearest Hospital');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    // Allow typing entire sentence freely without auto-routing on 1 letter!
    onQueryChange(val);
  };

  if (!isVisible) return null;

  return (
    <div
      className={`fixed left-0 right-0 z-40 px-3.5 max-w-md mx-auto pointer-events-auto transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${
        isSearchActive ? 'top-14' : 'bottom-6'
      }`}
    >
      {/* 70/30 Ratio buttons: 1) TYPE REQUIRED BLOOD GROUP (70%) 2) NEAREST HOSPITAL (30%) */}
      {!isSearchActive && (
        <div className="mb-2 flex items-stretch gap-2 w-full select-none">
          {/* 1) 70% Ratio: TYPE REQUIRED BLOOD GROUP */}
          <button
            type="button"
            onClick={handleFocusBloodInput}
            className="w-[70%] flex items-center gap-2.5 px-3 py-2 rounded-2xl bg-[#121212]/95 backdrop-blur-xl border border-[#2a2a2a] hover:border-[#E2FF4D] text-white shadow-[0_8px_24px_rgba(0,0,0,0.8)] transition-all cursor-pointer group active:scale-[0.98]"
          >
            <span className="w-6 h-6 rounded-lg bg-[#ff334b]/20 border border-[#ff334b]/40 flex items-center justify-center flex-shrink-0 text-[#ff334b] group-hover:scale-110 transition-transform">
              <Droplet className="w-3.5 h-3.5 fill-current" />
            </span>
            <div className="text-left min-w-0 flex-1">
              <span className="block text-[10px] font-black text-white group-hover:text-[#E2FF4D] tracking-wider uppercase truncate">
                TYPE REQUIRED BLOOD GROUP
              </span>
              <span className="block text-[8px] text-[#888888] font-medium truncate">
                Tap to select O+, B+, A+, AB-...
              </span>
            </div>
          </button>

          {/* 2) 30% Ratio: NEAREST HOSPITAL */}
          <button
            type="button"
            onClick={handleNearestHospital}
            className="w-[30%] flex flex-col items-center justify-center px-2 py-2 rounded-2xl bg-[#121212]/95 backdrop-blur-xl border border-[#2a2a2a] hover:border-[#E2FF4D] text-white shadow-[0_8px_24px_rgba(0,0,0,0.8)] transition-all cursor-pointer group active:scale-[0.98]"
          >
            <div className="flex items-center gap-1 text-[#E2FF4D] group-hover:scale-110 transition-transform mb-0.5">
              <Building2 className="w-4 h-4" />
            </div>
            <span className="text-[9px] font-black text-white group-hover:text-[#E2FF4D] tracking-tight uppercase text-center leading-tight">
              nearest hospital
            </span>
          </button>
        </div>
      )}

      {/* Optional Blood Quick Picker bar if user tapped TYPE REQUIRED BLOOD GROUP */}
      {!isSearchActive && showBloodPicker && (
        <div className="mb-2 flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1.5 px-2.5 rounded-xl bg-[#161616]/95 border border-[#333333] shadow-2xl animate-in fade-in slide-in-from-bottom-2 duration-200">
          <span className="text-[9px] font-bold text-[#E2FF4D] uppercase px-1 flex-shrink-0">SELECT:</span>
          {COMMON_BLOOD_GROUPS.map((bg) => (
            <button
              key={bg}
              type="button"
              onClick={() => handleBloodGroupSelect(bg)}
              className="px-2.5 py-1 rounded-lg bg-[#222222] hover:bg-[#E2FF4D] hover:text-black text-white text-[10px] font-black tracking-wide border border-[#333333] transition-colors cursor-pointer flex-shrink-0"
            >
              {bg}
            </button>
          ))}
        </div>
      )}

      {/* Main Green Themed Floating Search Bar */}
      <form
        onSubmit={handleSubmit}
        className={`flex items-center backdrop-blur-xl rounded-full px-3.5 shadow-[0_12px_36px_rgba(0,0,0,0.85)] border transition-all duration-300 gap-2.5 ${
          isSearchActive
            ? 'h-11 bg-[#141414]/95 border-[#E2FF4D]/60 ring-1 ring-[#E2FF4D]/20'
            : 'h-12 bg-[#111111]/95 border-[#2a2a2a] ring-1 ring-[#E2FF4D]/30'
        }`}
      >
        {/* Neon Green Search / Pin Icon */}
        <button
          type="submit"
          className="text-[#E2FF4D] hover:scale-110 transition-transform flex-shrink-0 flex items-center justify-center cursor-pointer"
          title="Search Emergency Hospital"
        >
          {isSearchActive ? (
            <Search className="w-4 h-4 text-[#E2FF4D]" />
          ) : (
            <MapPin className="w-4 h-4 text-[#E2FF4D]" />
          )}
        </button>

        {/* Symptoms / Emergency Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={currentQuery}
          onChange={handleInputChange}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSubmit();
            }
          }}
          placeholder={
            isSearchActive
              ? 'Type symptoms and press Enter...'
              : 'Type symptoms (e.g. chest pain) & press Enter...'
          }
          className="flex-1 min-w-0 bg-transparent text-xs sm:text-sm text-white font-sans font-medium placeholder-[#777777] focus:outline-none"
        />

        {/* Submit Arrow Button (appears when user has typed something to clearly trigger triage) */}
        {currentQuery.trim().length > 0 && (
          <button
            type="submit"
            title="Detect issue & route to hospital"
            className="w-7 h-7 rounded-full bg-[#E2FF4D] text-black hover:bg-white flex items-center justify-center transition-colors flex-shrink-0 cursor-pointer active:scale-95 shadow-md"
          >
            <ArrowRight className="w-3.5 h-3.5 stroke-[3]" />
          </button>
        )}

        {/* Clear search button (when active) */}
        {isSearchActive && onClearSearch && (
          <button
            type="button"
            onClick={onClearSearch}
            title="Clear and reset search"
            className="text-[#888888] hover:text-white p-1 rounded-full transition-colors flex-shrink-0 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        {/* Green Glowing Voice Mic Button */}
        <button
          type="button"
          onClick={onToggleListening}
          title={isListening ? 'Stop Voice Listening' : 'Speak Symptoms'}
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all cursor-pointer ${
            isListening
              ? 'bg-[#ff334b] text-white animate-pulse scale-105 shadow-[0_0_15px_rgba(255,51,75,0.8)]'
              : 'bg-[#1e1e1e] text-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black border border-[#2a2a2a]'
          }`}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>
      </form>
    </div>
  );
};
