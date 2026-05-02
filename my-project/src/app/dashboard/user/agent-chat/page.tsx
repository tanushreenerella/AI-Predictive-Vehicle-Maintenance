'use client';

import { useState, useEffect, useRef } from 'react';
import { fetchWithAuth } from '@/lib/fetchWithAuth';
import { Bot, Send, Calendar, AlertTriangle } from 'lucide-react';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

type Message = {
  role: 'user' | 'agent';
  text: string;
  appointment?: {
    appointment_id: string;
    vehicle: string;
    date: string;
    time: string;
    urgency: string;
    service_type: string;
  } | null;
};

export default function AgentChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      text: "Hi! I'm your AI vehicle assistant. Ask me about your vehicle's health, or say 'book an appointment' to schedule a service.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/vehicles/health/me`)
      .then(r => r.ok ? r.json() : [])
      .then((data: any[]) => {
        setVehicles(data);
        if (data.length > 0) setSelectedVehicleId(String(data[0].id));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = { role: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetchWithAuth(`${API_BASE}/agent/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: text,
          vehicle_id: selectedVehicleId || undefined,
        }),
      });

      const data = await res.json();
      setMessages(prev => [
        ...prev,
        { role: 'agent', text: data.reply, appointment: data.appointment ?? null },
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'agent', text: 'Sorry, I could not connect to the AI service. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const urgencyColor = (u: string) =>
    u === 'HIGH' ? 'border-red-500/50 bg-red-500/10 text-red-400'
    : u === 'MEDIUM' ? 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400'
    : 'border-green-500/50 bg-green-500/10 text-green-400';

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center gap-3">
        <Bot className="w-7 h-7 text-blue-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">AI Assistant</h1>
          <p className="text-gray-400 text-sm">Ask about your vehicle health or book a service appointment</p>
        </div>
      </div>

      {/* Vehicle selector */}
      {vehicles.length > 0 && (
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-400 whitespace-nowrap">Active vehicle:</label>
          <select
            value={selectedVehicleId}
            onChange={e => setSelectedVehicleId(e.target.value)}
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {vehicles.map((v: any) => (
              <option key={v.id} value={String(v.id)}>
                {v.name} {v.ai_risk_level ? `— ${v.ai_risk_level} risk` : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Chat window */}
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-4 h-[420px] overflow-y-auto space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col gap-2 ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`p-3 rounded-2xl max-w-[85%] text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-100'
              }`}
            >
              {m.text}
            </div>

            {/* Appointment receipt card */}
            {m.appointment && (
              <div className={`max-w-[85%] rounded-2xl border p-4 space-y-2 text-sm ${urgencyColor(m.appointment.urgency)}`}>
                <div className="flex items-center gap-2 font-semibold">
                  <Calendar className="w-4 h-4" />
                  Appointment Confirmed
                </div>
                <div className="space-y-1 text-gray-300">
                  <p><span className="text-gray-500">Vehicle:</span> {m.appointment.vehicle}</p>
                  <p><span className="text-gray-500">Service:</span> {m.appointment.service_type}</p>
                  <p><span className="text-gray-500">Date:</span> {m.appointment.date} at {m.appointment.time}</p>
                  <p>
                    <span className="text-gray-500">Urgency:</span>{' '}
                    <span className="font-semibold">{m.appointment.urgency}</span>
                  </p>
                </div>
                <a
                  href="/dashboard/user/appointments"
                  className="inline-block mt-1 text-blue-400 underline text-xs"
                >
                  View in appointments →
                </a>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            AI is thinking…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask about your vehicle or say 'book an appointment'…"
          className="flex-1 bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white transition-colors"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>

      <p className="text-xs text-gray-600 text-center">
        Tip: Say "book a service" or "schedule appointment" to auto-book based on your vehicle's risk level.
      </p>
    </div>
  );
}
