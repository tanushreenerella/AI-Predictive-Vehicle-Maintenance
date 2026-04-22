'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE = 'http://localhost:8000';

type Appointment = {
  id: string;
  vehicle_id: string;
  service_type: string;
  appointment_date: string;
  appointment_time: string;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'CONFIRMED' | 'COMPLETED';

  ai_warning?: {
    level: 'LOW' | 'MEDIUM' | 'HIGH';
    message: string;
    suggestion?: string;
  };
};


export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  const router = useRouter();
  const [editingId, setEditingId] = useState<string | null>(null);
const [newDate, setNewDate] = useState('');
const [newTime, setNewTime] = useState('');

  useEffect(() => {
    fetch(`${API_BASE}/schedule/me`, { credentials: 'include' })
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(setAppointments)
      .catch(() => router.replace('/login'))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">My Appointments</h1>
        <p className="text-gray-400">All your scheduled services</p>
      </div>

      {loading && (
        <p className="text-gray-400">Loading appointments…</p>
      )}

      {!loading && appointments.length === 0 && (
        <div className="bg-gray-800/40 p-6 rounded-xl border border-gray-700">
          <p className="text-gray-400">
            You don’t have any scheduled appointments yet.
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {appointments.map(appt => (
          <div
  key={appt.id}
  className="bg-gray-800/40 p-6 rounded-xl border border-gray-700 flex flex-col justify-between"
>
  {/* Top */}
  <div className="space-y-4">
    <div className="flex justify-between items-center gap-2">
      <p className="text-white font-semibold text-lg">
        {appt.service_type}
      </p>

     <div className="flex gap-2">
  <span className={`text-xs px-3 py-1 rounded-full font-semibold
    ${appt.status === 'COMPLETED'
      ? 'bg-gray-600/20 text-gray-400'
      : 'bg-blue-600/20 text-blue-400'
    }`}>
    {appt.status}
  </span>

  <span className={`text-xs px-3 py-1 rounded-full font-semibold
    ${
      appt.urgency === 'HIGH'
        ? 'bg-red-600/20 text-red-400'
        : appt.urgency === 'MEDIUM'
        ? 'bg-yellow-600/20 text-yellow-400'
        : 'bg-green-600/20 text-green-400'
    }`}>
    {appt.urgency}
  </span>
</div>

    </div>

    <p className="text-gray-400 text-sm">
      📅 {appt.appointment_date} &nbsp; ⏰ {appt.appointment_time}
    </p>
    {appt.ai_warning && (
  <div
    className={`rounded-lg p-3 text-sm border
      ${appt.ai_warning.level === 'HIGH'
        ? 'bg-red-600/20 border-red-600/40 text-red-300'
        : appt.ai_warning.level === 'MEDIUM'
        ? 'bg-yellow-600/20 border-yellow-600/40 text-yellow-300'
        : 'bg-green-600/20 border-green-600/40 text-green-300'
      }`}
  >
    <div className="flex items-start justify-between gap-3">
      <p>⚠️ {appt.ai_warning.message}</p>

      {appt.ai_warning.level === 'HIGH' && appt.status !== 'COMPLETED' && (
        <button
          onClick={() => {
            setEditingId(appt.id);
            setNewDate(appt.appointment_date);
            setNewTime(appt.appointment_time);
          }}
          className="text-xs underline hover:text-red-200"
        >
          Reschedule now
        </button>
      )}
    </div>

    {appt.ai_warning.suggestion && (
      <p className="mt-1 text-xs opacity-80">
        💡 {appt.ai_warning.suggestion}
      </p>
    )}
  </div>
)}

  </div>

  {/* Divider */}
  <div className="mt-4 mb-6  border-t border-gray-700" />

  {/* Edit Mode */}
  {editingId === appt.id ? (
    <div className="space-y-10 pt-2">
      <div className="grid grid-cols-2 gap-3">
        <input
          type="date"
          value={newDate}
          onChange={e => setNewDate(e.target.value)}
          className="bg-gray-900 border border-gray-600 rounded-lg p-2 text-white"
        />

        <input
          type="time"
          value={newTime}
          onChange={e => setNewTime(e.target.value)}
          className="bg-gray-900 border border-gray-600 rounded-lg p-2 text-white"
        />
      </div>

      <div className="flex justify-end gap-3 cursor-pointer">
        <button
          onClick={async () => {
            await fetch(`${API_BASE}/schedule/${appt.id}`, {
              method: 'PATCH',
              credentials: 'include',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                appointment_date: newDate,
                appointment_time: newTime,
              }),
            });

            setAppointments(prev =>
              prev.map(a =>
                a.id === appt.id
                  ? {
                      ...a,
                      appointment_date: newDate,
                      appointment_time: newTime,
                    }
                  : a
              )
            );

            setEditingId(null);
          }}
          className="px-4 py-2 bg-blue-600 rounded-lg text-white text-sm cursor-pointer"
        >
          Save changes
        </button>

        <button
          onClick={() => setEditingId(null)}
          className="px-4 py-2 text-gray-400 text-sm cursor-pointer"
        >
          Cancel
        </button>
      </div>
    </div>
  ) : (
    /* Footer Actions */
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex gap-4">
        <button
  disabled={appt.ai_warning?.level === 'HIGH'}
  onClick={() => {
    setEditingId(appt.id);
    setNewDate(appt.appointment_date);
    setNewTime(appt.appointment_time);
  }}
  className={`text-sm cursor-pointer
    ${
      appt.ai_warning?.level === 'HIGH'
        ? 'text-gray-500 cursor-not-allowed'
        : 'text-blue-400 hover:text-blue-300'
    }`}
>
  Reschedule
</button>


        <button
          onClick={async () => {
            if (!confirm('Cancel this appointment?')) return;

            await fetch(`${API_BASE}/schedule/${appt.id}`, {
              method: 'DELETE',
              credentials: 'include',
            });

            setAppointments(prev =>
              prev.filter(a => a.id !== appt.id)
            );
          }}
          className="text-sm text-red-400 hover:text-red-300 cursor-pointer"
        >
          Cancel
        </button>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() =>
            router.push(`/dashboard/user/appointments/${appt.id}`)
          }
          className="text-sm text-green-400 hover:text-green-300 cursor-pointer"
        >
          View receipt
        </button>

        <a
          href={`${API_BASE}/schedule/receipt/${appt.id}/pdf`}
          className="px-3 py-1.5 bg-green-600 rounded-lg text-sm text-white"
        >
          PDF
        </a>
      </div>
    </div>
  )}
</div>

        ))}
      </div>
    </div>
  );
}
