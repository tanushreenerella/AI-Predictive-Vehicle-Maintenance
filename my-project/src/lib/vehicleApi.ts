import { Vehicle } from "./types";
import { normalizeVehicle } from "@/lib/normalizers/vehicle";
import { fetchWithAuth } from "@/lib/fetchWithAuth";
const BASE_URL = "https://ai-predictive-vehicle-maintenance-production.up.railway.app";

// Backend request payload (snake_case)
export interface CreateVehiclePayload {
  name: string;
  model: string;
  year: number;
  registration_number: string;
}

export async function addVehicle(payload: CreateVehiclePayload) {
  const res = await fetchWithAuth(`${BASE_URL}/vehicles`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Failed to add vehicle");
  return res.json();
}

export async function getVehicles(): Promise<Vehicle[]> {
  const res = await fetchWithAuth(`${BASE_URL}/vehicles/me`);
  if (!res.ok) throw new Error("Failed to fetch vehicles");
  const data = await res.json();

  return data.map(normalizeVehicle);
}
