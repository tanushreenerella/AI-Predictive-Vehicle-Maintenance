'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/fetchWithAuth';
import { Bot, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

const SERVICE_TYPES = [
  'General Checkup',
  'Oil Change',
  'Cooling System',
  'Brake Inspection',
  'Tyre Rotation',
  'Engine Diagnostic',
  'Battery Check',
  'AI Recommended',
];

type Suggestion = {
  urgency: 'LOW' | 'MEDIUM' | 'HIGH';
  recommended_window_days: number[];
  suggested_date: string;
  reasoning: string;
  confidence: number;
  agent: string;
};

export default function ScheduleAppointmentPage() {
  const router = useRouter();
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<any | null>(null);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [suggestionLoading, setSuggestionLoading] = useState(false);
  const [suggestionError, setSuggestionError] = useState(false);

  // Form state (always visible)
  const [serviceType, setServiceType] = useState('General Checkup');
  const [apptDate, setApptDate] = useState('');
  const [apptTime, setApptTime] = useState('10:00');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/vehicles/health/me`)
      .then(r => r.ok ? r.json() : [])
      .then(setVehicles)
      .catch(() => router.replace('/login'));
  }, [router]);

  const selectVehicle = async (vehicle: any) => {
    setSelectedVehicle(vehicle);
    setSuggestion(null);
    setSuggestionError(false);
    setSuggestionLoading(true);

    try {
      const res = await fetchWithAuth(`${API_BASE}/schedule/suggestion/${vehicle.id}`);
      if (!res.ok) throw new Error();
      const data: Suggestion = await res.json();
      setSuggestion(data);
      setApptDate(data.suggested_date);
    } catch {
      setSuggestionError(true);
    } finally {
      setSuggestionLoading(false);
    }
  };

  const urgencyColor = (u: string) =>
    u === 'HIGH' ? 'bg-red-600/20 text-red-400 border-red-600/40'
    : u === 'MEDIUM' ? 'bg-yellow-600/20 text-yellow-400 border-yellow-600/40'
    : 'bg-green-600/20 text-green-400 border-green-600/40';

  const handleSubmit = async () => {
    if (!selectedVehicle || !apptDate || !apptTime) {
      alert('Please select a vehicle, date, and time.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await fetchWithAuth(`${API_BASE}/schedule`, {
        method: 'POST',
        body: JSON.stringify({
          vehicle_id: selectedVehicle.id,
          service_type: serviceType,
          appointment_date: apptDate,
          appointment_time: apptTime,
          urgency: suggestion?.urgency ?? 'MEDIUM',
        }),
      });
      if (!res.ok) throw new Error();
      setSuccess(true);
    } catch {
      alert('Failed to schedule appointment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6 text-center">
        <CheckCircle className="w-16 h-16 text-green-400" />
        <div>
          <h2 className="text-2xl font-bold text-white">Appointment Scheduled!</h2>
          <p className="text-gray-400 mt-1">
            {serviceType} for {selectedVehicle?.name} on {apptDate} at {apptTime}
          </p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => router.push('/dashboard/user/appointments')}
            className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-500"
          >
            View Appointments
          </button>
          <button
            onClick={() => {
              setSuccess(false);
              setSelectedVehicle(null);
              setSuggestion(null);
              setApptDate('');
              setApptTime('10:00');
            }}
            className="px-6 py-3 bg-gray-700 text-white rounded-xl hover:bg-gray-600"
          >
            Book Another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Schedule Appointment</h1>
        <p className="text-gray-400">AI-guided scheduling with full manual control.</p>
      </div>

      {/* Step 1: Vehicle Selection */}
      <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">1. Select Vehicle</h2>
        {vehicles.length === 0 ? (
          <p className="text-gray-400">
            No vehicles found.{' '}
            <a href="/dashboard/user/vehicles/add" className="text-blue-400 underline">
              Add one first.
            </a>
          </p>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {vehicles.map(v => (
              <button
                key={v.id}
                onClick={() => selectVehicle(v)}
                className={`p-4 rounded-xl border text-left transition ${
                  selectedVehicle?.id === v.id
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-600 hover:border-gray-500 bg-gray-900/30'
                }`}
              >
                <p className="font-semibold text-white">{v.name}</p>
                <p className="text-sm text-gray-400">{v.model}</p>
                <p className="text-sm mt-1 text-gray-300">Health: {v.health}%</p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Step 2: AI Recommendation */}
      <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          2. AI Recommendation
        </h2>

        {!selectedVehicle && (
          <p className="text-gray-500 text-sm">Select a vehicle above to get an AI recommendation.</p>
        )}

        {suggestionLoading && (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Analysing vehicle condition…
          </div>
        )}

        {suggestionError && (
          <div className="flex items-center gap-2 text-yellow-400 text-sm">
            <AlertTriangle className="w-4 h-4" />
            Could not get AI recommendation. You can still book manually below.
          </div>
        )}

        {suggestion && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${urgencyColor(suggestion.urgency)}`}>
                {suggestion.urgency} URGENCY
              </span>
              <span className="text-sm text-gray-400">
                Confidence: {Math.round(suggestion.confidence * 100)}%
              </span>
              <span className="text-xs text-gray-600">via {suggestion.agent}</span>
            </div>

            <p className="text-gray-300 text-sm">{suggestion.reasoning}</p>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-900/50 rounded-xl p-3">
                <p className="text-xs text-gray-500">Recommended Window</p>
                <p className="text-white font-medium">
                  {suggestion.recommended_window_days[0]}–{suggestion.recommended_window_days[1]} days
                </p>
              </div>
              <div className="bg-gray-900/50 rounded-xl p-3">
                <p className="text-xs text-gray-500">Suggested Date</p>
                <p className="text-white font-medium">{suggestion.suggested_date}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Step 3: Book Appointment (always visible once vehicle selected) */}
      {selectedVehicle && (
        <div className="bg-gray-800/40 p-6 rounded-2xl border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            3. Book Appointment
          </h2>

          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Service Type</label>
              <select
                value={serviceType}
                onChange={e => setServiceType(e.target.value)}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {SERVICE_TYPES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Date</label>
              <input
                type="date"
                value={apptDate}
                min={new Date().toISOString().split('T')[0]}
                onChange={e => setApptDate(e.target.value)}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Time</label>
              <input
                type="time"
                value={apptTime}
                onChange={e => setApptTime(e.target.value)}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Summary */}
          <div className="mt-4 p-4 bg-gray-900/50 rounded-xl border border-gray-700 text-sm text-gray-300 space-y-1">
            <p><span className="text-gray-500">Vehicle:</span> {selectedVehicle.name} ({selectedVehicle.model})</p>
            <p><span className="text-gray-500">Service:</span> {serviceType}</p>
            <p><span className="text-gray-500">Urgency:</span> {suggestion?.urgency ?? 'MEDIUM'}</p>
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting || !apptDate || !apptTime}
            className="mt-5 px-8 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition"
          >
            {submitting ? 'Scheduling…' : 'Confirm Appointment'}
          </button>
        </div>
      )}
    </div>
  );
}
