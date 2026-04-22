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

  let status: "healthy" | "warning" | "critical" = "healthy";
  if (v.ai_risk_level === "MEDIUM") status = "warning";
  if (v.ai_risk_level === "HIGH") status = "critical";

  return {
    id: v.id,
    name: v.name,
    registration: v.registration_number,
    mileage: v.mileage,
    fuel: v.fuel_level,

    // 🔥 AI-derived fields
    health,
    status,
    riskLevel: v.ai_risk_level,
    failureProbability: v.ai_failure_probability,
    affectedComponent: v.ai_component,
    confidence: v.ai_confidence,
    lastAnalyzed: v.ai_last_analyzed,

    nextService: v.next_service_date ?? null
  };
}
