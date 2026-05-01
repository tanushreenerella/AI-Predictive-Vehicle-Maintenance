import { fetchWithAuth } from "@/lib/fetchWithAuth";

const API_BASE = "https://ai-predictive-vehicle-maintenance-production.up.railway.app";

export async function getCurrentUser() {
  const res = await fetchWithAuth(`${API_BASE}/auth/me`);

  if (!res.ok) {
    throw new Error("Not authenticated");
  }

  return res.json();
}
