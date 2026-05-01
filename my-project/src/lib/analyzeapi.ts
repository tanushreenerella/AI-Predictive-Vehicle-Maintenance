// lib/api.ts
export async function analyzeapi(sensorData: any) {
  const res = await fetch("https://ai-predictive-vehicle-maintenance-production.up.railway.app/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sensor_data: sensorData,
    }),
  });

  if (!res.ok) {
    throw new Error("Vehicle analysis failed");
  }

  return res.json();
}
