import { fetchWithAuth } from "@/lib/fetchWithAuth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ai-predictive-vehicle-maintenance-qdst.onrender.com";

export async function getCurrentUser() {
  const res = await fetchWithAuth(`${API_BASE}/auth/me`);

  if (!res.ok) {
    throw new Error("Not authenticated");
  }

  return res.json();
}
