'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/fetchWithAuth';
import { Calendar, Clock, AlertTriangle, Lightbulb, FileText } from 'lucide-react';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

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
    fetchWithAuth(`${API_BASE}/schedule/me`)
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(setAppointments)
      .catch(() => router.replace('/login'))
      .finally(() => setLoading(false));
  }, [router]);

  const urgencyBadge = (u: string) =>
    u === ‘HIGH’ ? ‘bg-red-500/10 text-red-400 border-red-500/20’
    : u === ‘MEDIUM’ ? ‘bg-yellow-500/10 text-yellow-400 border-yellow-500/20’
    : ‘bg-green-500/10 text-green-400 border-green-500/20’;

  const warningBg = (level: string) =>
    level === ‘HIGH’ ? ‘bg-red-500/5 border-red-500/20 text-red-300’
    : level === ‘MEDIUM’ ? ‘bg-yellow-500/5 border-yellow-500/20 text-yellow-300’
    : ‘bg-gray-800/40 border-gray-700 text-gray-400’;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">My Appointments</h1>
        <p className="text-gray-500 text-sm mt-1">All your scheduled services</p>
      </div>

      {loading && <p className="text-gray-500 text-sm">Loading appointments…</p>}

      {!loading && appointments.length === 0 && (
        <div className="bg-gray-800/40 p-6 rounded-xl border border-gray-700/60 text-center">
          <p className="text-gray-400 text-sm">No appointments scheduled yet.</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {appointments.map(appt => (
          <div key={appt.id} className="bg-gray-800/40 p-5 rounded-xl border border-gray-700/60 flex flex-col gap-4">

            {/* Header */}
            <div className="flex items-start justify-between gap-2">
              <p className="text-white font-semibold text-base leading-snug">{appt.service_type}</p>
              <div className="flex gap-1.5 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${appt.status === ‘COMPLETED’ ? ‘bg-gray-700/40 text-gray-400 border-gray-600/40’ : ‘bg-blue-500/10 text-blue-400 border-blue-500/20’}`}>
                  {appt.status}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${urgencyBadge(appt.urgency)}`}>
                  {appt.urgency}
                </span>
              </div>
            </div>

            {/* Date/Time */}
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" />{appt.appointment_date}</span>
              <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />{appt.appointment_time}</span>
            </div>

            {/* AI Warning */}
            {appt.ai_warning && (
              <div className={`rounded-lg p-3 text-sm border ${warningBg(appt.ai_warning.level)}`}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                    <p>{appt.ai_warning.message}</p>
                  </div>
                  {appt.ai_warning.level === ‘HIGH’ && appt.status !== ‘COMPLETED’ && (
                    <button onClick={() => { setEditingId(appt.id); setNewDate(appt.appointment_date); setNewTime(appt.appointment_time); }} className="text-xs underline shrink-0 opacity-70 hover:opacity-100">
                      Reschedule
                    </button>
                  )}
                </div>
                {appt.ai_warning.suggestion && (
                  <div className="flex items-start gap-1.5 mt-1.5 text-xs opacity-70">
                    <Lightbulb className="w-3 h-3 mt-0.5 shrink-0" />
                    {appt.ai_warning.suggestion}
                  </div>
                )}
              </div>
            )}

            <div className="border-t border-gray-700/60" />

            {/* Edit Mode */}
            {editingId === appt.id ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <input type="date" value={newDate} onChange={e => setNewDate(e.target.value)} className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
                  <input type="time" value={newTime} onChange={e => setNewTime(e.target.value)} className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={async () => {
                      await fetchWithAuth(`${API_BASE}/schedule/${appt.id}`, { method: ‘PATCH’, body: JSON.stringify({ appointment_date: newDate, appointment_time: newTime }) });
                      setAppointments(prev => prev.map(a => a.id === appt.id ? { ...a, appointment_date: newDate, appointment_time: newTime } : a));
                      setEditingId(null);
                    }}
                    className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm transition-colors"
                  >
                    Save
                  </button>
                  <button onClick={() => setEditingId(null)} className="px-4 py-1.5 text-gray-400 hover:text-gray-200 text-sm transition-colors">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <div className="flex gap-3">
                  <button
                    disabled={appt.ai_warning?.level === ‘HIGH’}
                    onClick={() => { setEditingId(appt.id); setNewDate(appt.appointment_date); setNewTime(appt.appointment_time); }}
                    className="text-sm text-gray-400 hover:text-gray-200 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
                  >
                    Reschedule
                  </button>
                  <button
                    onClick={async () => {
                      if (!confirm(‘Cancel this appointment?’)) return;
                      await fetchWithAuth(`${API_BASE}/schedule/${appt.id}`, { method: ‘DELETE’ });
                      setAppointments(prev => prev.filter(a => a.id !== appt.id));
                    }}
                    className="text-sm text-red-400/70 hover:text-red-400 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
                <div className="flex gap-3 items-center">
                  <button onClick={() => router.push(`/dashboard/user/appointments/${appt.id}`)} className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200 transition-colors">
                    <FileText className="w-3.5 h-3.5" /> Receipt
                  </button>
                  <a href={`${API_BASE}/schedule/receipt/${appt.id}/pdf`} className="px-2.5 py-1 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs text-white transition-colors">
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
