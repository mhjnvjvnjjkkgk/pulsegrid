/**
 * PulseGrid Haversine Geodetic Calculator & Traffic Model
 */

export function calculateDistanceKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  return Math.round(distance * 10) / 10; // 1 decimal place
}

/**
 * Calculates estimated driving transit time in minutes with Indian urban traffic factor
 */
export function calculateEtaMinutes(distanceKm: number): number {
  if (distanceKm <= 0.3) return 2;
  if (distanceKm <= 1.0) return Math.max(3, Math.round(distanceKm * 3.2));
  if (distanceKm <= 3.0) return Math.max(4, Math.round(distanceKm * 2.8 + 1));
  if (distanceKm <= 6.0) return Math.max(8, Math.round(distanceKm * 2.6 + 2));
  return Math.max(12, Math.round(distanceKm * 2.4 + 3));
}
