import { Vehicle } from "./types";
import { normalizeVehicle } from "@/lib/normalizers/vehicle";
const BASE_URL = "http://localhost:8000";

// Backend request payload (snake_case)
export interface CreateVehiclePayload {
  name: string;
  model: string;
  year: number;
  registration_number: string;
}

export async function addVehicle(payload: CreateVehiclePayload) {
  const res = await fetch(`${BASE_URL}/vehicles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Failed to add vehicle");
  return res.json();
}

export async function getVehicles(): Promise<Vehicle[]> {
  const res = await fetch(`${BASE_URL}/vehicles/me`,{credentials:"include"});
  if (!res.ok) throw new Error("Failed to fetch vehicles");
  const data = await res.json();

  // map snake_case from backend to camelCase for frontend
  return data.map(normalizeVehicle);
}
