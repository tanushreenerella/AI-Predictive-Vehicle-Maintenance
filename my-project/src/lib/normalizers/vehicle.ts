export function normalizeVehicle(v: any) {
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
export function normalizeDashboardVehicle(v: any) {
  const health = Math.max(
    0,
    Math.round(100 - (v.ai_failure_probability ?? 0) * 100)
  );

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
    failureProbability: v.ai_failure_probability ?? null,
    affectedComponent: v.ai_component ?? null,
    confidence: v.ai_confidence ?? null,
    lastAnalyzed: v.ai_last_analyzed ?? null,
    lastService: v.last_service_date ?? null,
    nextService: v.next_service_date ?? null,
  };
}
