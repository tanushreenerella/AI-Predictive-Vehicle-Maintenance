import { apiErrorMessage } from "@/lib/apiError";
import { fetchWithAuth } from "@/lib/fetchWithAuth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ai-predictive-vehicle-maintenance-qdst.onrender.com";

export async function analyzeapi(sensorData: any, vehicleId?: string) {
  const payload = { ...sensorData };
  if (vehicleId) payload.vehicle_id = vehicleId;

  const res = await fetchWithAuth(`${API_BASE}/predict`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(await apiErrorMessage(res, "Vehicle analysis failed"));
  }

  return res.json();
}
