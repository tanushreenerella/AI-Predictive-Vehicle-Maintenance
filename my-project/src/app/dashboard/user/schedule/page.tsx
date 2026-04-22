'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { DashboardVehicle } from '@/lib/types';
const API_BASE = 'http://localhost:8000';

type ScheduleSuggestion = {
  urgency: 'LOW' | 'MEDIUM' | 'HIGH';
  recommended_window_days: number[];
  suggested_date: string;
  reasoning: string;
  confidence: number;
  agent: string;
};

export default function ScheduleAppointmentPage() {
  // Vehicles come from /vehicles/health/me
  const [vehicles, setVehicles] = useState<DashboardVehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<string | null>(null);

  // Scheduling agent output
  const [suggestion, setSuggestion] = useState<ScheduleSuggestion | null>(null);
  const [loading, setLoading] = useState(false);

  // Manual scheduling (human-in-the-loop)
  const [serviceType, setServiceType] = useState('General Checkup');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const router = useRouter();

  // 🔹 Load vehicles for this user
  useEffect(() => {
    fetch(`${API_BASE}/vehicles/health/me`, { credentials: 'include' })
      .then(res => {
        if (!res.ok) throw new Error('Unauthorized');
        return res.json();
      })
      .then(setVehicles)
      .catch(() => router.replace('/login'));
  }, [router]);

  // 🔹 Ask Scheduling Agent for recommendation
  const fetchSuggestion = async (vehicleId: string) => {
    setLoading(true);
    setSuggestion(null);

    try {
      const res = await fetch(
        `${API_BASE}/schedule/suggestion/${vehicleId}`,
        { credentials: 'include' }
      );

      if (!res.ok) throw new Error('Failed to fetch suggestion');

      const data: ScheduleSuggestion = await res.json();
      setSuggestion(data);

      // Pre-fill date with AI suggestion
      setDate(data.suggested_date);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Confirm appointment (persist to backend)
  const confirmAppointment = async () => {
    if (!selectedVehicle || !suggestion || !date || !time) return;

    setSubmitting(true);

    try {
      const res = await fetch(`${API_BASE}/schedule`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicle_id: selectedVehicle,
          service_type: serviceType,
          appointment_date: date,
          appointment_time: time,
          urgency: suggestion.urgency,
        }),
      });

      if (!res.ok) throw new Error('Failed to schedule');

      alert('✅ Appointment scheduled successfully');
      router.push('/dashboard/user');
    } catch {
      alert('❌ Failed to schedule appointment');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">
          Schedule Appointment
        </h1>
        <p className="text-gray-400">
          AI-guided scheduling with full control.
        </p>
      </div>

      {/* Vehicle Selection */}
      <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
        <h2 className="text-xl font-semibold mb-4 text-white">
          Select Vehicle
        </h2>

        <div className="grid md:grid-cols-3 gap-4">
          {vehicles.map(vehicle => (
            <button
              key={vehicle.id}
              onClick={() => {
                setSelectedVehicle(vehicle.id);
                fetchSuggestion(vehicle.id);
              }}
              className={`p-4 rounded-xl border text-left transition
                ${
                  selectedVehicle === vehicle.id
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-600 hover:border-gray-500'
                }`}
            >
              <p className="font-semibold text-white">{vehicle.name}</p>
              <p className="text-sm text-gray-400">{vehicle.model}</p>
              <p className="text-sm mt-1 text-gray-300">
                Health: {vehicle.health}%
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* AI Recommendation */}
      <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
        <h2 className="text-xl font-semibold mb-4 text-white">
          🤖 AI Recommendation
        </h2>

        {!selectedVehicle && (
          <p className="text-gray-400">
            Select a vehicle to see AI recommendations.
          </p>
        )}

        {loading && (
          <p className="text-gray-400">
            Analyzing vehicle condition…
          </p>
        )}

        {suggestion && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold
                  ${
                    suggestion.urgency === 'HIGH'
                      ? 'bg-red-600/20 text-red-400'
                      : suggestion.urgency === 'MEDIUM'
                      ? 'bg-yellow-600/20 text-yellow-400'
                      : 'bg-green-600/20 text-green-400'
                  }`}
              >
                {suggestion.urgency} URGENCY
              </span>

              <span className="text-sm text-gray-400">
                Confidence: {Math.round(suggestion.confidence * 100)}%
              </span>
            </div>

            <p className="text-gray-300">{suggestion.reasoning}</p>

            <div className="bg-gray-900/40 p-4 rounded-xl border border-gray-600">
              <p className="text-sm text-gray-400">Recommended Window</p>
              <p className="text-white font-medium">
                {suggestion.recommended_window_days[0]}–{suggestion.recommended_window_days[1]} days
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Manual Scheduling */}
      {suggestion && (
        <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
          <h2 className="text-xl font-semibold mb-4 text-white">
            Customize Schedule
          </h2>

          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-400">Service Type</label>
              <select
                value={serviceType}
                onChange={e => setServiceType(e.target.value)}
                className="w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg p-2 text-white"
              >
                <option>General Checkup</option>
                <option>Cooling System</option>
                <option>Oil Change</option>
                <option>AI Recommended</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400">Date</label>
              <input
                type="date"
                value={date}
                onChange={e => setDate(e.target.value)}
                className="w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg p-2 text-white"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400">Time</label>
              <input
                type="time"
                value={time}
                onChange={e => setTime(e.target.value)}
                className="w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg p-2 text-white"
              />
            </div>
          </div>
<button
  onClick={confirmAppointment}
  disabled={submitting}
  className={`mt-6 px-6 py-3 rounded-xl text-white font-semibold transition
    ${
      submitting
        ? 'bg-gray-600 cursor-not-allowed'
        : 'bg-blue-600 hover:bg-blue-500'
    }`}
>
  {submitting ? 'Scheduling…' : 'Confirm Appointment'}
</button>


        </div>
      )}
    </div>
  );
}
