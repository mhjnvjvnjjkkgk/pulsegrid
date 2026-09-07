import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Hospital, LiveHold, WardCode } from './types';
import { DEFAULT_USER_LOCATION, INITIAL_HOSPITALS } from './data/hospitals';
import { CLINICAL_PROTOCOLS } from './data/protocols';
import { classifyEmergency } from './utils/triageClassifier';
import { calculateDistanceKm, calculateEtaMinutes } from './utils/distance';
import { VoiceTriageInput } from './components/VoiceTriageInput';
import { TacticalMap } from './components/TacticalMap';
import { HospitalPeekDrawer } from './components/HospitalPeekDrawer';
import { ClinicalProtocolSheet } from './components/ClinicalProtocolSheet';
import { Crosshair, MapPin, Search, X, Check, Undo2 } from 'lucide-react';

export interface AddressSuggestion {
  place_id: string;
  display_name: string;
  lat: number;
  lng: number;
  title: string;
  subtitle: string;
}

const SAVED_LOCATION_KEY = 'statmed_user_location';

function getInitialUserLocation(): { lat: number; lng: number; address: string } {
  try {
    const saved = localStorage.getItem(SAVED_LOCATION_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (
        typeof parsed.lat === 'number' &&
        typeof parsed.lng === 'number' &&
        typeof parsed.address === 'string'
      ) {
        return parsed;
      }
    }
  } catch {
    // ignore
  }
  return DEFAULT_USER_LOCATION;
}

// Snap to nearest drivable road via OSRM nearest API (with instant offline fallback)
async function snapToNearestRoad(
  lat: number,
  lng: number
): Promise<{ lat: number; lng: number; name?: string }> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);
    const res = await fetch(
      `https://router.project-osrm.org/nearest/v1/driving/${lng},${lat}?number=1`,
      { signal: controller.signal }
    );
    clearTimeout(timeout);
    if (res.ok) {
      const data = await res.json();
      if (data.waypoints && data.waypoints.length > 0) {
        const [wLng, wLat] = data.waypoints[0].location;
        return { lat: wLat, lng: wLng, name: data.waypoints[0].name };
      }
    }
  } catch (err) {
    console.warn('Road snap request failed, using offset approximation:', err);
  }
  // Safe slight offset onto nearby street corridor if offline/timeout
  return {
    lat: Number((lat + 0.00025).toFixed(6)),
    lng: Number((lng + 0.00015).toFixed(6)),
  };
}

export function App() {
  // Global User Location State with localStorage persistence
  const [userLocation, setUserLocation] = useState<{
    lat: number;
    lng: number;
    address: string;
  }>(getInitialUserLocation);

  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [showLocationModal, setShowLocationModal] = useState<boolean>(false);
  const [manualAddressInput, setManualAddressInput] = useState<string>('');
  const [isGeocoding, setIsGeocoding] = useState<boolean>(false);
  const [addressSuggestions, setAddressSuggestions] = useState<AddressSuggestion[]>([]);
  const [isSearchingAddress, setIsSearchingAddress] = useState<boolean>(false);

  // Rapido-Style Draggable Road Pickup Pin State
  const [isAdjustingPickup, setIsAdjustingPickup] = useState<boolean>(false);
  const [pickupPoint, setPickupPoint] = useState<{ lat: number; lng: number } | null>(null);

  // Triage & Input state
  const [currentQuery, setCurrentQuery] = useState('');
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Drawer & Modal views
  const [drawerExpanded, setDrawerExpanded] = useState(false);
  const [showProtocolSheet, setShowProtocolSheet] = useState(false);

  // Active Live Hold (15-Min Dynamic GPS Soft Lock)
  const [activeHold, setActiveHold] = useState<LiveHold | null>(null);
  const [, setInboundQueue] = useState<LiveHold[]>([]);

  // Search bar is visible only when no active hold, not adjusting pickup, and drawer is in peek mode
  const isSearchBarVisible = !activeHold && !drawerExpanded && !isAdjustingPickup;

  // Current clinical protocol based on query
  const classification = classifyEmergency(currentQuery);
  const currentProtocol = CLINICAL_PROTOCOLS[classification.protocol_key] || CLINICAL_PROTOCOLS.cardiac;

  // Speech Recognition setup (Web Speech API with graceful fallback)
  const recognitionRef = useRef<any>(null);

  // Real-time Address Autocomplete (Nominatim debounced search)
  useEffect(() => {
    const trimmed = manualAddressInput.trim();
    if (trimmed.length < 2) {
      setAddressSuggestions([]);
      setIsSearchingAddress(false);
      return;
    }

    setIsSearchingAddress(true);
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
            trimmed
          )}&addressdetails=1&limit=5`,
          {
            headers: { 'Accept-Language': 'en' },
            signal: controller.signal,
          }
        );
        if (res.ok) {
          const data = await res.json();
          const mapped: AddressSuggestion[] = data.map((item: any) => {
            const parts = (item.display_name || '').split(',').map((s: string) => s.trim());
            const title = parts.slice(0, 2).join(', ');
            const subtitle = parts.slice(2).join(', ');
            return {
              place_id: String(item.place_id || Math.random()),
              display_name: item.display_name,
              lat: parseFloat(item.lat),
              lng: parseFloat(item.lon),
              title: title || item.name || 'Location',
              subtitle: subtitle || '',
            };
          });
          setAddressSuggestions(mapped);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.warn('Address autocomplete error:', err);
        }
      } finally {
        setIsSearchingAddress(false);
      }
    }, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [manualAddressInput]);

  // Re-sort hospitals based on emergency severity and live proximity
  const sortHospitals = useCallback(
    (hospitalList: Hospital[], query: string, targetWardCode: WardCode): Hospital[] => {
      const result = classifyEmergency(query);

      return [...hospitalList].sort((a, b) => {
        if (result.severity === 'RED') {
          const aWard = a.wards.find((w) => w.ward_code === targetWardCode);
          const bWard = b.wards.find((w) => w.ward_code === targetWardCode);

          const aHasBed = (aWard?.available_now ?? 0) > 0;
          const bHasBed = (bWard?.available_now ?? 0) > 0;

          if (aHasBed && !bHasBed) return -1;
          if (!aHasBed && bHasBed) return 1;

          return a.eta_minutes - b.eta_minutes;
        }

        const aWard = a.wards.find((w) => w.ward_code === targetWardCode);
        const bWard = b.wards.find((w) => w.ward_code === targetWardCode);

        const aBeds = aWard?.available_now ?? 0;
        const bBeds = bWard?.available_now ?? 0;

        if (aBeds > 0 && bBeds === 0) return -1;
        if (aBeds === 0 && bBeds > 0) return 1;

        return a.eta_minutes - b.eta_minutes;
      });
    },
    []
  );

  // Re-calculate all hospital ETAs and distances relative to any chosen origin
  const recomputeHospitalsForOrigin = useCallback(
    (lat: number, lng: number, prevList: Hospital[], query: string): Hospital[] => {
      const targetWardCode = classifyEmergency(query).recommended_ward;

      const updated = prevList.map((hosp) => {
        const distKm = calculateDistanceKm(lat, lng, hosp.lat, hosp.lng);
        const etaMin = calculateEtaMinutes(distKm);

        return {
          ...hosp,
          distance_km: distKm,
          eta_minutes: etaMin,
        };
      });

      return sortHospitals(updated, query, targetWardCode);
    },
    [sortHospitals]
  );

  // Hospital state
  const [hospitals, setHospitals] = useState<Hospital[]>(() => {
    return recomputeHospitalsForOrigin(
      userLocation.lat,
      userLocation.lng,
      INITIAL_HOSPITALS,
      ''
    );
  });

  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);

  // Reverse geocoding helper via OpenStreetMap Nominatim
  const reverseGeocode = async (lat: number, lng: number): Promise<string | null> => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
        {
          headers: { 'Accept-Language': 'en' },
          signal: controller.signal,
        }
      );
      clearTimeout(timeout);
      if (res.ok) {
        const data = await res.json();
        if (data.display_name) {
          const parts = data.display_name.split(',').map((p: string) => p.trim());
          const shortAddress = parts.slice(0, 3).join(', ');
          return shortAddress;
        }
      }
    } catch {
      // ignore
    }
    return null;
  };

  // Apply coordinates cleanly across all hospital ETAs, state, and localStorage
  const applyCoordinates = useCallback(
    (lat: number, lng: number, addressLabel?: string) => {
      const cleanLat = Number(lat.toFixed(6));
      const cleanLng = Number(lng.toFixed(6));
      const cleanAddr =
        addressLabel || `Near Lat ${cleanLat.toFixed(4)}, Lng ${cleanLng.toFixed(4)}`;

      const newLocation = {
        lat: cleanLat,
        lng: cleanLng,
        address: cleanAddr,
      };

      setUserLocation(newLocation);

      try {
        localStorage.setItem(SAVED_LOCATION_KEY, JSON.stringify(newLocation));
      } catch {
        // ignore
      }

      setHospitals((prev) => {
        const recalculated = recomputeHospitalsForOrigin(cleanLat, cleanLng, prev, currentQuery);
        if (recalculated.length > 0) {
          setSelectedHospital((currentSelected) => {
            if (!currentSelected) return null;
            const match = recalculated.find((h) => h.id === currentSelected.id);
            return match || recalculated[0];
          });
        }
        return recalculated;
      });
    },
    [currentQuery, recomputeHospitalsForOrigin]
  );

  // Request browser GPS location cleanly
  const requestLiveGps = useCallback(() => {
    setIsLocating(true);

    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      const handleSuccess = (position: GeolocationPosition) => {
        const { latitude, longitude } = position.coords;
        const distToDefault = calculateDistanceKm(
          latitude,
          longitude,
          DEFAULT_USER_LOCATION.lat,
          DEFAULT_USER_LOCATION.lng
        );

        const initialLabel =
          distToDefault < 1.5
            ? DEFAULT_USER_LOCATION.address
            : `Current Location (${latitude.toFixed(4)}, ${longitude.toFixed(4)})`;

        applyCoordinates(latitude, longitude, initialLabel);
        setIsLocating(false);

        reverseGeocode(latitude, longitude).then((placeName) => {
          if (placeName) {
            setUserLocation((prev) => {
              const updated = { ...prev, address: placeName };
              try {
                localStorage.setItem(SAVED_LOCATION_KEY, JSON.stringify(updated));
              } catch {
                // ignore
              }
              return updated;
            });
          }
        });
      };

      const handleError = (err: GeolocationPositionError) => {
        console.warn('High accuracy geolocation timed out/failed, trying standard accuracy:', err?.message);
        navigator.geolocation.getCurrentPosition(
          handleSuccess,
          (fallbackErr) => {
            console.warn('Geolocation fallback failed, keeping current location:', fallbackErr?.message);
            setIsLocating(false);
          },
          {
            enableHighAccuracy: false,
            timeout: 5000,
            maximumAge: 300000,
          }
        );
      };

      navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 60000,
      });
    } else {
      setIsLocating(false);
    }
  }, [applyCoordinates]);

  // "Use Live GPS" with Rapido-style Pin Placement & Dragging on the nearest road
  const handleUseLiveGpsWithPin = useCallback(async () => {
    setIsLocating(true);
    setShowLocationModal(false);

    const onCoordsResolved = async (lat: number, lng: number) => {
      setIsLocating(false);
      // Automatically snap to the nearest road
      const road = await snapToNearestRoad(lat, lng);
      setPickupPoint({ lat: road.lat, lng: road.lng });
      setIsAdjustingPickup(true);

      reverseGeocode(lat, lng).then((addr) => {
        if (addr) {
          setUserLocation((prev) => ({ ...prev, address: addr }));
        }
      });
    };

    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => onCoordsResolved(pos.coords.latitude, pos.coords.longitude),
        (err) => {
          console.warn('GPS error, using current location:', err);
          onCoordsResolved(userLocation.lat, userLocation.lng);
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 60000 }
      );
    } else {
      onCoordsResolved(userLocation.lat, userLocation.lng);
    }
  }, [userLocation.lat, userLocation.lng]);

  // Finalize Rapido Road Pickup Location
  const handleFinalizePickup = useCallback(async () => {
    if (!pickupPoint) {
      setIsAdjustingPickup(false);
      return;
    }
    const distMeters = Math.max(
      5,
      Math.round(
        calculateDistanceKm(userLocation.lat, userLocation.lng, pickupPoint.lat, pickupPoint.lng) * 1000
      )
    );
    setIsAdjustingPickup(false);
    const roadAddr = await reverseGeocode(pickupPoint.lat, pickupPoint.lng);
    const finalLabel = roadAddr || `Roadside Pickup Spot (~${distMeters}m walk)`;
    applyCoordinates(pickupPoint.lat, pickupPoint.lng, finalLabel);
  }, [applyCoordinates, pickupPoint, userLocation.lat, userLocation.lng]);

  // Snap Draggable Pin to nearest road
  const handleSnapPickupToRoad = useCallback(async () => {
    if (!pickupPoint) return;
    const road = await snapToNearestRoad(pickupPoint.lat, pickupPoint.lng);
    setPickupPoint({ lat: road.lat, lng: road.lng });
  }, [pickupPoint]);

  // Run live GPS detection on initial mount and initialize facilities if saved location exists
  const hasDetectedGpsOnMount = useRef(false);
  useEffect(() => {
    if (!hasDetectedGpsOnMount.current) {
      hasDetectedGpsOnMount.current = true;
      if (
        userLocation.lat !== DEFAULT_USER_LOCATION.lat ||
        userLocation.lng !== DEFAULT_USER_LOCATION.lng
      ) {
        applyCoordinates(userLocation.lat, userLocation.lng, userLocation.address);
      }
      requestLiveGps();
    }
  }, [applyCoordinates, requestLiveGps, userLocation.address, userLocation.lat, userLocation.lng]);

  // Speech recognition hook
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          handleSymptomInput(transcript);
        }
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
    }
  }, []);

  const handleToggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch {
          setIsListening(false);
        }
      } else {
        alert('Voice dictation is supported in modern Chrome, Edge, and Safari.');
      }
    }
  };

  // Handle clinical emergency symptom input / search submit
  const handleSymptomInput = (query: string) => {
    setCurrentQuery(query);
    setIsSearchActive(true);

    const result = classifyEmergency(query);
    const sorted = sortHospitals(hospitals, query, result.recommended_ward);
    setHospitals(sorted);

    if (sorted.length > 0) {
      setSelectedHospital(sorted[0]);
    }
  };

  const handleClearSearch = () => {
    setCurrentQuery('');
    setIsSearchActive(false);
    setDrawerExpanded(false);
    setSelectedHospital(null);

    const targetWardCode = classifyEmergency('').recommended_ward;
    const sorted = sortHospitals(hospitals, '', targetWardCode);
    setHospitals(sorted);
  };

  // Live Hold Countdown (Decrements every 1 sec; warns at 2 min; releases bed at 0)
  useEffect(() => {
    if (!activeHold) return;

    const timer = setInterval(() => {
      setActiveHold((prev) => {
        if (!prev) return null;
        if (prev.seconds_left <= 1) {
          clearInterval(timer);
          // Release bed back to inventory on expiry
          setHospitals((hospList) =>
            hospList.map((h) => {
              if (h.id === prev.hospital_id) {
                return {
                  ...h,
                  wards: h.wards.map((w) =>
                    w.ward_code === prev.ward_code
                      ? { ...w, available_now: w.available_now + 1 }
                      : w
                  ),
                };
              }
              return h;
            })
          );
          return null;
        }
        return {
          ...prev,
          seconds_left: prev.seconds_left - 1,
        };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [activeHold]);

  // Book a 15-minute emergency soft hold
  const handleBookSlot = (overrideWardCode?: WardCode) => {
    if (!selectedHospital) return;
    const wardCode = overrideWardCode || currentProtocol.target_ward || 'adult_icu';
    const ward = selectedHospital.wards.find((w) => w.ward_code === wardCode);
    if (!ward || ward.available_now <= 0) return;

    // Optimistically decrement bed count immediately
    setHospitals((prev) =>
      prev.map((h) => {
        if (h.id === selectedHospital.id) {
          return {
            ...h,
            wards: h.wards.map((w) =>
              w.ward_code === wardCode ? { ...w, available_now: Math.max(0, w.available_now - 1) } : w
            ),
          };
        }
        return h;
      })
    );

    // Generate 6-digit OTP code for nurse desk redemption
    const randomOtp = Math.floor(100000 + Math.random() * 900000).toString();

    const newHold: LiveHold = {
      hold_id: `hold_${Date.now()}`,
      hospital_id: selectedHospital.id,
      hospital_name: selectedHospital.name,
      ward_code: wardCode,
      ward_label: ward.label,
      otp_code: randomOtp,
      seconds_left: 900, // 15:00 minutes
      total_seconds: 900,
      hold_type: 'CITIZEN',
      severity: classification.severity,
      requester_phone: '+91 98300 12345',
      requester_name: 'Citizen Patient',
      created_at: new Date().toISOString(),
      status: 'ACTIVE',
      vector_status: 'TOWARD',
      current_lat: userLocation.lat,
      current_lng: userLocation.lng,
      eta_display: `${selectedHospital.eta_minutes} mins`,
    };

    setActiveHold(newHold);
    setInboundQueue((prev) => [newHold, ...prev]);
    setShowProtocolSheet(false);
  };

  const handleCancelHold = () => {
    if (!activeHold) return;

    // Release bed back to inventory
    setHospitals((prev) =>
      prev.map((h) => {
        if (h.id === activeHold.hospital_id) {
          return {
            ...h,
            wards: h.wards.map((w) =>
              w.ward_code === activeHold.ward_code
                ? { ...w, available_now: w.available_now + 1 }
                : w
            ),
          };
        }
        return h;
      })
    );

    setActiveHold(null);
  };

  const handleRedeemHold = (otp: string) => {
    if (activeHold && activeHold.otp_code === otp) {
      setActiveHold(null);
      setInboundQueue((prev) =>
        prev.map((h) => (h.otp_code === otp ? { ...h, status: 'REDEEMED' } : h))
      );
    }
  };

  const handleSelectSuggestion = (s: AddressSuggestion) => {
    applyCoordinates(s.lat, s.lng, s.title || s.display_name);
    setShowLocationModal(false);
    setManualAddressInput('');
    setAddressSuggestions([]);
  };

  // Manual Geocode Search
  const handleManualAddressSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (addressSuggestions.length > 0) {
      handleSelectSuggestion(addressSuggestions[0]);
      return;
    }
    if (!manualAddressInput.trim()) return;

    setIsGeocoding(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          manualAddressInput.trim()
        )}&addressdetails=1&limit=1`,
        { headers: { 'Accept-Language': 'en' } }
      );
      if (res.ok) {
        const data = await res.json();
        if (data.length > 0) {
          const lat = parseFloat(data[0].lat);
          const lon = parseFloat(data[0].lon);
          const parts = (data[0].display_name || '').split(',').map((p: string) => p.trim());
          const shortName = parts.slice(0, 2).join(', ');
          applyCoordinates(lat, lon, shortName || data[0].name || manualAddressInput.trim());
          setShowLocationModal(false);
          setManualAddressInput('');
          setAddressSuggestions([]);
        } else {
          alert('Could not locate this address. Please type a specific locality or place name.');
        }
      }
    } catch {
      alert('Geocoding service unavailable. Please try again.');
    } finally {
      setIsGeocoding(false);
    }
  };

  const handleSelectHospital = useCallback((hosp: Hospital) => {
    setSelectedHospital(hosp);
    setIsSearchActive(true);
  }, []);

  const handleRouteCalculated = useCallback((distKm: number, durationMin: number) => {
    setSelectedHospital((prev) => {
      if (!prev) return null;
      if (prev.distance_km === distKm && prev.eta_minutes === durationMin) {
        return prev;
      }
      return {
        ...prev,
        distance_km: distKm,
        eta_minutes: durationMin,
      };
    });
  }, []);

  return (
    <main className="relative w-full h-screen overflow-hidden bg-[#0A0A0A] text-white font-sans">
      {/* 1. Rapido-Style Draggable Road Pickup Pin Adjustment Card */}
      {isAdjustingPickup && pickupPoint && (
        <div className="fixed top-3.5 left-0 right-0 z-50 px-3 max-w-md mx-auto pointer-events-auto animate-in slide-in-from-top-4 duration-300">
          <div className="bg-[#121212]/98 backdrop-blur-2xl border-2 border-[#E2FF4D] rounded-2xl p-3.5 shadow-[0_12px_40px_rgba(0,0,0,0.95)] text-white">
            <div className="flex items-center justify-between mb-2 pb-2 border-b border-[#262626]">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#E2FF4D] animate-ping"></span>
                <h4 className="text-xs font-black uppercase tracking-wider text-[#E2FF4D]">
                  ROAD PICKUP PIN
                </h4>
              </div>
              <span className="text-[10px] text-black font-black bg-[#E2FF4D] px-2 py-0.5 rounded-full uppercase">
                DRAG OR TAP MAP
              </span>
            </div>

            <p className="text-xs text-[#d1d5db] mb-2.5 leading-relaxed">
              Pin auto-placed on nearest road. Drag the pin to any road spot or tap on the map.
            </p>

            {/* Walking Distance Indicator with Dotted Icon */}
            <div className="flex items-center justify-between bg-[#1a1a1a] rounded-xl px-3 py-2 border border-[#333333] mb-3">
              <div className="flex items-center gap-2">
                <span className="text-base">🚶</span>
                <div>
                  <span className="block text-[11px] font-bold text-white">
                    Walk to road: ~{Math.max(5, Math.round(calculateDistanceKm(userLocation.lat, userLocation.lng, pickupPoint.lat, pickupPoint.lng) * 1000))} meters
                  </span>
                  <span className="block text-[9px] text-[#E2FF4D] font-medium">
                    •••• Dotted line shows walking path
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={handleSnapPickupToRoad}
                className="px-2.5 py-1 rounded-lg bg-[#262626] hover:bg-[#333333] text-[10px] font-bold text-[#E2FF4D] border border-[#E2FF4D]/40 cursor-pointer transition-colors"
              >
                Snap to Road
              </button>
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsAdjustingPickup(false)}
                className="flex-1 py-2 rounded-xl bg-[#222222] hover:bg-[#2a2a2a] text-xs font-bold text-gray-300 transition-colors cursor-pointer flex items-center justify-center gap-1.5"
              >
                <Undo2 className="w-3.5 h-3.5" />
                Cancel
              </button>
              <button
                type="button"
                onClick={handleFinalizePickup}
                className="flex-[2] py-2 rounded-xl bg-[#E2FF4D] hover:bg-[#f5ff80] text-black text-xs font-black tracking-wide shadow-lg transition-all cursor-pointer flex items-center justify-center gap-1.5 active:scale-95"
              >
                <Check className="w-4 h-4 stroke-[3]" />
                Finalize Location
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Green Themed MY LOCATION Bar (Moved to top in cleared space) */}
      {!isAdjustingPickup && (
        <div className="fixed top-3.5 left-0 right-0 z-30 px-3.5 max-w-md mx-auto pointer-events-auto transition-all duration-300">
          <div
            onClick={() => setShowLocationModal(true)}
            className="flex items-center justify-between bg-[#111111]/95 backdrop-blur-xl border border-[#2a2a2a] hover:border-[#E2FF4D] ring-1 ring-[#E2FF4D]/30 rounded-full px-3.5 py-1.5 shadow-[0_8px_32px_rgba(0,0,0,0.85)] cursor-pointer group transition-all"
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <span className="p-1 rounded-full bg-[#E2FF4D]/15 text-[#E2FF4D] group-hover:scale-110 flex-shrink-0 transition-transform">
                <MapPin className="w-3.5 h-3.5" />
              </span>
              <span className="text-[10px] font-black uppercase text-[#E2FF4D] tracking-wider flex-shrink-0">
                MY LOCATION:
              </span>
              <span className="text-[11px] font-medium text-white truncate group-hover:text-[#E2FF4D] transition-colors">
                {isLocating ? 'Detecting your GPS location...' : userLocation.address}
              </span>
            </div>

            <div className="flex items-center gap-1.5 ml-2 flex-shrink-0">
              <span className="text-[9px] text-[#E2FF4D] bg-[#222222] border border-[#333333] px-2 py-0.5 rounded-full font-bold group-hover:bg-[#E2FF4D] group-hover:text-black transition-colors">
                Change
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleUseLiveGpsWithPin();
                }}
                title="Place & Drag Road Pin with Live GPS"
                className="text-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black p-1 rounded-full transition-all cursor-pointer"
              >
                <Crosshair className={`w-3.5 h-3.5 ${isLocating ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Voice Triage Search Bar directly beneath MY LOCATION */}
      <VoiceTriageInput
        currentQuery={currentQuery}
        onQueryChange={(query) => {
          setCurrentQuery(query);
        }}
        onSearchSubmit={(query) => handleSymptomInput(query)}
        isListening={isListening}
        onToggleListening={handleToggleListening}
        isSearchActive={isSearchActive}
        onClearSearch={handleClearSearch}
        isVisible={isSearchBarVisible}
      />

      {/* 4. Full-Screen Interactive Google Maps Canvas with Automatic Route & Rapido Pin */}
      <TacticalMap
        userLocation={userLocation}
        hospitals={hospitals}
        selectedHospital={selectedHospital}
        onSelectHospital={handleSelectHospital}
        isHolding={!!activeHold}
        onUserLocate={requestLiveGps}
        isLocating={isLocating}
        isSearchActive={isSearchActive}
        onRouteCalculated={handleRouteCalculated}
        drawerExpanded={drawerExpanded}
        isAdjustingPickup={isAdjustingPickup}
        pickupPoint={pickupPoint}
        onPickupPointChange={(point) => setPickupPoint(point)}
      />

      {/* 5. Hospital Peek Drawer - visible when a hospital is selected */}
      {selectedHospital && (
        <HospitalPeekDrawer
          hospital={selectedHospital}
          onBookSlot={handleBookSlot}
          isHolding={!!activeHold}
          activeHold={activeHold}
          onCancelHold={handleCancelHold}
          onSimulateRedeem={() => {
            if (activeHold) {
              handleRedeemHold(activeHold.otp_code);
            }
          }}
          onOpenProtocolView={() => setShowProtocolSheet(true)}
          protocol={currentProtocol}
          drawerExpanded={drawerExpanded}
          onDrawerExpandedChange={(expanded) => setDrawerExpanded(expanded)}
          isVisible={!isAdjustingPickup}
          triageExplanation={classification.explanation}
          onClose={handleClearSearch}
        />
      )}

      {/* 6. Expanded Clinical Protocol Sheet */}
      {showProtocolSheet && selectedHospital && (
        <ClinicalProtocolSheet
          hospital={selectedHospital}
          protocol={currentProtocol}
          onClose={() => setShowProtocolSheet(false)}
          onBookSlot={handleBookSlot}
          isHolding={!!activeHold}
          activeHold={activeHold}
        />
      )}

      {/* 7. Location Adjustment Modal with Real-time Address Autocomplete */}
      {showLocationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-md bg-[#121212] border border-[#2a2a2a] ring-1 ring-[#E2FF4D]/30 rounded-2xl shadow-2xl p-4 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-[#222222]">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#E2FF4D]" />
                <h3 className="font-bold text-sm text-white">Adjust My Location</h3>
              </div>
              <button
                onClick={() => {
                  setShowLocationModal(false);
                  setAddressSuggestions([]);
                }}
                className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleManualAddressSubmit} className="mt-3">
              <label className="block text-xs font-bold text-[#E2FF4D] uppercase tracking-wider mb-1.5">
                Search Your Address / Locality:
              </label>
              <div className="relative flex items-center gap-2 bg-[#181818] border border-[#2e2e2e] focus-within:border-[#E2FF4D] focus-within:ring-1 focus-within:ring-[#E2FF4D]/30 rounded-xl px-3 py-2.5 transition-all">
                <Search className="w-4 h-4 text-[#E2FF4D] flex-shrink-0" />
                <input
                  type="text"
                  value={manualAddressInput}
                  onChange={(e) => setManualAddressInput(e.target.value)}
                  placeholder="Type street, building, area (e.g. Park Street, Salt Lake...)"
                  className="w-full bg-transparent text-sm text-white focus:outline-none placeholder:text-gray-500"
                  autoFocus
                />
                {isSearchingAddress && (
                  <div className="w-3.5 h-3.5 border-2 border-[#E2FF4D] border-t-transparent rounded-full animate-spin flex-shrink-0" />
                )}
                {manualAddressInput && (
                  <button
                    type="button"
                    onClick={() => {
                      setManualAddressInput('');
                      setAddressSuggestions([]);
                    }}
                    className="text-gray-400 hover:text-white p-0.5 cursor-pointer flex-shrink-0"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Real-time Address Autocomplete Results Dropdown */}
              {addressSuggestions.length > 0 && (
                <div className="mt-2 max-h-56 overflow-y-auto rounded-xl border border-[#2a2a2a] bg-[#161616] shadow-2xl divide-y divide-[#222222]">
                  {addressSuggestions.map((s) => (
                    <button
                      key={s.place_id}
                      type="button"
                      onClick={() => handleSelectSuggestion(s)}
                      className="w-full text-left px-3.5 py-2.5 flex items-start gap-2.5 hover:bg-[#202020] hover:border-l-2 hover:border-l-[#E2FF4D] transition-colors cursor-pointer group"
                    >
                      <MapPin className="w-4 h-4 text-[#E2FF4D] flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                      <div className="min-w-0 flex-1">
                        <span className="block text-xs font-bold text-white group-hover:text-[#E2FF4D] truncate">
                          {s.title}
                        </span>
                        {s.subtitle && (
                          <span className="block text-[10px] text-gray-400 truncate mt-0.5">
                            {s.subtitle}
                          </span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* No match indicator */}
              {!isSearchingAddress && manualAddressInput.trim().length >= 2 && addressSuggestions.length === 0 && (
                <div className="mt-2 px-3 py-2 rounded-xl bg-[#161616] border border-[#262626] text-[11px] text-gray-400">
                  No address matches found. Press Enter to search or try a different locality name.
                </div>
              )}

              <div className="mt-3 flex items-center justify-between gap-2">
                <button
                  type="button"
                  onClick={handleUseLiveGpsWithPin}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#E2FF4D]/15 border border-[#E2FF4D]/40 text-xs font-bold text-[#E2FF4D] hover:bg-[#E2FF4D] hover:text-black transition-all cursor-pointer shadow-sm active:scale-95"
                >
                  <Crosshair className="w-3.5 h-3.5" />
                  Use Live GPS & Place Pin
                </button>
                <button
                  type="submit"
                  disabled={!manualAddressInput.trim() || isGeocoding}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#E2FF4D] text-black text-xs font-black hover:bg-[#f5ff80] disabled:opacity-40 transition-all cursor-pointer shadow-md active:scale-95"
                >
                  {isGeocoding ? 'Locating...' : 'Set Location'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Honesty strip */}
      <div className="fixed bottom-0 left-0 right-0 z-10 pointer-events-none text-center pb-0.5">
        <span className="text-[8px] font-mono text-white/30 tracking-widest uppercase bg-black/80 px-2 py-0.5 rounded-t">
          SIMULATED CAPACITY DATA • DEMONSTRATION ONLY • SMART INDIA HACKATHON 2026
        </span>
      </div>
    </main>
  );
}

export default App;
