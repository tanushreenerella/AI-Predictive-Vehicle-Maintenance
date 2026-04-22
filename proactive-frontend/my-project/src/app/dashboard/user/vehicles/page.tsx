'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import { Vehicle } from '@/lib/types';

const API_BASE = 'http://localhost:8000';

export default function MyVehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadVehicles() {
      try {
        const res = await fetch(`${API_BASE}/vehicles/me`, {
          credentials: 'include',
        });

        if (!res.ok) throw new Error('Unauthorized');

        const data = await res.json();
        setVehicles(data);
      } catch (err) {
        console.error('Failed to fetch vehicles', err);
      } finally {
        setLoading(false);
      }
    }

    loadVehicles();
  }, []);

  if (loading) {
    return <p className="text-gray-400">Loading vehicles...</p>;
  }

  return (
    <div className="space-y-6 text-white">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">My Vehicles</h1>
        <Link
          href="/dashboard/user/vehicles/add"
          className="bg-blue-600 hover:bg-blue-500 transition px-4 py-2 rounded text-white"
        >
          + Add Vehicle
        </Link>
      </div>

      {/* Empty state */}
      {vehicles.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="mb-4">No vehicles added yet.</p>
          <Link
            href="/dashboard/user/vehicles/add"
            className="inline-block bg-blue-600 hover:bg-blue-500 px-5 py-2 rounded text-white"
          >
            ➕ Add Your First Vehicle
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vehicles.map(vehicle => (
            <div
              key={vehicle.id}
              className="rounded-xl p-4 bg-gray-800 border border-gray-700"
            >
              <h2 className="font-semibold text-lg">{vehicle.name}</h2>
              <p className="text-sm text-gray-400">{vehicle.model}</p>
              <p className="text-sm">Year: {vehicle.year}</p>
              <p className="text-sm">
                Reg: {vehicle.registrationNumber}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
