export type Vehicle = {
  id: string;
  userId: string;
  name: string;
  model: string;
  year: number;
  registrationNumber: string;
  createdAt: string;
};
export type DashboardVehicle = Vehicle & {
  mileage: number;
  fuelLevel: number;
  health: number;
  status: "optimal" | "warning" | "critical";
  lastService?: string;
  nextService?: string;
};