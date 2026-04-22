"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { addVehicle} from "@/lib/vehicleApi";

export default function AddVehiclePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    model: "",
    year: "",
    registrationNumber: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    if (Object.values(form).some(v => v.trim() === "")) {
      alert("Fill all fields");
      return;
    }

    try {
      setLoading(true);

      await addVehicle({
        name: form.name,
        model: form.model,
        year: Number(form.year),
        registration_number: form.registrationNumber,
      });

      router.push("/dashboard/user/vehicles");
    } catch (err) {
      console.error(err);
      alert("Failed to save vehicle");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl space-y-4 ml-10 mt-20">
      <h1 className="text-2xl font-bold">Add Vehicle</h1>

      <input
        name="name"
        placeholder="Vehicle Name"
        className="w-full p-2 border rounded"
        value={form.name}
        onChange={handleChange}
      />
      <input
        name="model"
        placeholder="Model"
        className="w-full p-2 border rounded"
        value={form.model}
        onChange={handleChange}
      />
      <input
        name="year"
        type="number"
        placeholder="Year"
        className="w-full p-2 border rounded"
        value={form.year}
        onChange={handleChange}
      />
      <input
        name="registrationNumber"
        placeholder="Registration Number"
        className="w-full p-2 border rounded"
        value={form.registrationNumber}
        onChange={handleChange}
      />

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save Vehicle"}
      </button>
    </div>
  );
}
