export type VehicleAnalysis = {
  vehicleId: string;
  data: any;
  createdAt: string;
};

const KEY = "vehicle_analyses";

export const saveAnalysis = (analysis: VehicleAnalysis) => {
  const existing = JSON.parse(localStorage.getItem(KEY) || "[]");
  localStorage.setItem(KEY, JSON.stringify([...existing, analysis]));
};

export const getAnalysisByVehicle = (vehicleId: string) => {
  const all = JSON.parse(localStorage.getItem(KEY) || "[]");
  return all.filter((a: VehicleAnalysis) => a.vehicleId === vehicleId);
};
