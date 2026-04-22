const API_BASE = "http://localhost:8000";

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`, {
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error("Not authenticated");
  }

  return res.json();
}
