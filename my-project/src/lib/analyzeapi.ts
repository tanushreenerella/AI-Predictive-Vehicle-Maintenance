import { fetchWithAuth } from "@/lib/fetchWithAuth";

const API_BASE = "https://ai-predictive-vehicle-maintenance-production.up.railway.app";

export async function analyzeapi(sensorData: any, vehicleId?: string) {
  const payload = { ...sensorData };
  if (vehicleId) payload.vehicle_id = vehicleId;

  const res = await fetchWithAuth(`${API_BASE}/predict`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Vehicle analysis failed");
  }

  return res.json();
}
