type RawVehicle = {
  id: string;
  user_id?: string;
  name: string;
  model: string;
  year?: number;
  registration_number?: string;
  created_at?: string;
  mileage?: number;
  fuel_level?: number;
  health?: number | null;
  ai_risk_level?: string | null;
  risk_level?: string | null;
  ai_failure_probability?: number | null;
  failure_probability?: number | null;
  ai_component?: string | null;
  ai_confidence?: number | null;
  ai_last_analyzed?: string | null;
  last_service_date?: string | null;
  next_service_date?: string | null;
};

export function normalizeVehicle(v: RawVehicle) {
  return {
    id: v.id,
    userId: v.user_id,
    name: v.name,
    model: v.model,
    year: v.year,
    registrationNumber: v.registration_number,
    createdAt: v.created_at,
  };
}
export function normalizeDashboardVehicle(v: RawVehicle) {
  const probability = v.ai_failure_probability ?? v.failure_probability;
  const health = typeof v.health === "number"
    ? v.health
    : typeof probability === "number"
      ? Math.max(0, Math.round(100 - probability * 100))
      : 0;

  let status: "optimal" | "warning" | "critical" = "optimal";
  if (v.ai_risk_level === "MEDIUM") status = "warning";
  if (v.ai_risk_level === "HIGH") status = "critical";

  return {
    id: v.id,
    name: v.name,
    registration: v.registration_number,
    mileage: v.mileage ?? 0,
    fuelLevel: v.fuel_level ?? 0,

    health,
    status,
    riskLevel: v.ai_risk_level ?? null,
    failureProbability: probability ?? null,
    affectedComponent: v.ai_component ?? null,
    confidence: v.ai_confidence ?? null,
    lastAnalyzed: v.ai_last_analyzed ?? null,
    lastService: v.last_service_date ?? null,
    nextService: v.next_service_date ?? null,
  };
}
