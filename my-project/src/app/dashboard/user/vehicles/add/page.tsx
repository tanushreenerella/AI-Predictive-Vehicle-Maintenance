"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { addVehicle } from "@/lib/vehicleApi";
import { Car, Hash, Layers, CalendarDays, ArrowLeft } from "lucide-react";

export default function AddVehiclePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ name: "", model: "", year: "", registrationNumber: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    if (Object.values(form).some(v => v.trim() === "")) {
      alert("Please fill all fields");
      return;
    }
    try {
      setLoading(true);
      await addVehicle({ name: form.name, model: form.model, year: Number(form.year), registration_number: form.registrationNumber });
      router.push("/dashboard/user/vehicles");
    } catch {
      alert("Failed to save vehicle");
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: "name", label: "Vehicle Name", placeholder: "e.g. My Toyota", icon: Car, type: "text" },
    { name: "model", label: "Model", placeholder: "e.g. Camry XLE", icon: Layers, type: "text" },
    { name: "year", label: "Manufacturing Year", placeholder: "e.g. 2021", icon: CalendarDays, type: "number" },
    { name: "registrationNumber", label: "Registration Number", placeholder: "e.g. ABC1234", icon: Hash, type: "text" },
  ] as const;

return (
  <div className="flex justify-center pt-10 px-6">
    <div className="w-full max-w-md">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Add Vehicle</h1>
        <p className="text-gray-500 text-sm mt-1">
          Register a vehicle to start monitoring its health.
        </p>
      </div>

      <div className="bg-gray-800/40 border border-gray-700/60 rounded-2xl p-5 space-y-4">
        {fields.map(({ name, label, placeholder, icon: Icon, type }) => (
          <div key={name}>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">
              {label}
            </label>

            <div className="relative">
              <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />

              <input
                name={name}
                type={type}
                placeholder={placeholder}
                value={form[name]}
                onChange={handleChange}
                className="w-full pl-9 pr-3 py-2.5 bg-gray-900/60 border border-gray-700 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition"
              />
            </div>
          </div>
        ))}

        <div className="pt-1 flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Saving..." : "Save Vehicle"}
          </button>

          <button
            onClick={() => router.back()}
            className="px-5 py-2.5 bg-gray-700/50 hover:bg-gray-700 text-gray-300 text-sm rounded-xl transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
);
}
