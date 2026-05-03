'use client';

import { useEffect, useRef, useState } from 'react';
import { Bot, Calendar, Clock, Send, Wrench } from 'lucide-react';
import Link from 'next/link';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

type Recommendation = {
  likely_issue: string;
  recommended_service: string;
  urgency: string;
  estimated_cost: string;
  timeframe: string;
  reasoning?: string;
};

type Scheduling = {
  recommended_urgency: string;
  reason: string;
  service_type: string;
  selected_slot?: { date: string; time: string; label?: string };
  suggested_slots?: { date: string; time: string; label?: string }[];
};

type Appointment = {
  appointment_id: string;
  vehicle: string;
  date: string;
  time: string;
  urgency: string;
  service_type: string;
};

type VehicleOption = {
  id: string;
  name: string;
  ai_risk_level?: string | null;
};

type ConversationState = Record<string, unknown>;

type Message = {
  role: 'user' | 'agent';
  text: string;
  recommendation?: Recommendation | null;
  scheduling?: Scheduling | null;
  appointment?: Appointment | null;
};

export default function AgentChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      text: "Hi! I'm your AI vehicle assistant. Tell me a symptom and I'll diagnose it step by step, or say you want to book service.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState<VehicleOption[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>('');
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/vehicles/health/me`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data: VehicleOption[]) => {
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
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetchWithAuth(`${API_BASE}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: text,
          vehicle_id: selectedVehicleId || undefined,
          state: conversationState,
        }),
      });

      const data = await res.json();
      setConversationState(data.state ?? null);
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          text: data.reply,
          recommendation: data.recommendation ?? null,
          scheduling: data.scheduling ?? null,
          appointment: data.appointment ?? null,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'agent', text: 'Sorry, I could not connect to the AI service. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const urgencyColor = (urgency?: string) =>
    urgency === 'HIGH'
      ? 'border-red-500/50 bg-red-500/10 text-red-300'
      : urgency === 'MEDIUM'
        ? 'border-yellow-500/50 bg-yellow-500/10 text-yellow-200'
        : 'border-green-500/50 bg-green-500/10 text-green-200';

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center gap-3">
        <Bot className="w-7 h-7 text-blue-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">AI Assistant</h1>
          <p className="text-gray-400 text-sm">Diagnosis, recommendations, and booking in one chat</p>
        </div>
      </div>

      {vehicles.length > 0 && (
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-400 whitespace-nowrap">Active vehicle:</label>
          <select
            value={selectedVehicleId}
            onChange={(e) => {
              setSelectedVehicleId(e.target.value);
              setConversationState(null);
            }}
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {vehicles.map((v) => (
              <option key={v.id} value={String(v.id)}>
                {v.name} {v.ai_risk_level ? `- ${v.ai_risk_level} risk` : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 h-[420px] overflow-y-auto space-y-3">
        {messages.map((message, index) => (
          <div key={index} className={`flex flex-col gap-2 ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`p-3 rounded-lg max-w-[85%] text-sm leading-relaxed ${
                message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-100'
              }`}
            >
              {message.text}
            </div>

            {message.recommendation && (
              <div className={`max-w-[85%] rounded-lg border p-4 space-y-3 text-sm ${urgencyColor(message.recommendation.urgency)}`}>
                <div className="flex items-center gap-2 font-semibold">
                  <Wrench className="w-4 h-4" />
                  Service Recommendation
                </div>
                <div className="grid gap-2 text-gray-200">
                  <p><span className="text-gray-400">Likely issue:</span> {message.recommendation.likely_issue}</p>
                  <p><span className="text-gray-400">Service:</span> {message.recommendation.recommended_service}</p>
                  <p><span className="text-gray-400">Urgency:</span> <span className="font-semibold">{message.recommendation.urgency}</span></p>
                  <p><span className="text-gray-400">Estimated cost:</span> {message.recommendation.estimated_cost}</p>
                  <p><span className="text-gray-400">Timeframe:</span> {message.recommendation.timeframe}</p>
                </div>
              </div>
            )}

            {message.scheduling && !message.appointment && (
              <div className="max-w-[85%] rounded-lg border border-blue-500/40 bg-blue-500/10 p-4 space-y-3 text-sm text-blue-100">
                <div className="flex items-center gap-2 font-semibold">
                  <Clock className="w-4 h-4" />
                  Suggested Appointment
                </div>
                <div className="space-y-1 text-gray-200">
                  <p><span className="text-gray-400">Service:</span> {message.scheduling.service_type}</p>
                  <p><span className="text-gray-400">Priority:</span> {message.scheduling.recommended_urgency}</p>
                  {message.scheduling.selected_slot && (
                    <p><span className="text-gray-400">Slot:</span> {message.scheduling.selected_slot.date} at {message.scheduling.selected_slot.time}</p>
                  )}
                  <p className="text-gray-400">{message.scheduling.reason}</p>
                </div>
              </div>
            )}

            {message.appointment && (
              <div className={`max-w-[85%] rounded-lg border p-4 space-y-2 text-sm ${urgencyColor(message.appointment.urgency)}`}>
                <div className="flex items-center gap-2 font-semibold">
                  <Calendar className="w-4 h-4" />
                  Appointment Confirmed
                </div>
                <div className="space-y-1 text-gray-200">
                  <p><span className="text-gray-400">Vehicle:</span> {message.appointment.vehicle}</p>
                  <p><span className="text-gray-400">Service:</span> {message.appointment.service_type}</p>
                  <p><span className="text-gray-400">Date:</span> {message.appointment.date} at {message.appointment.time}</p>
                  <p><span className="text-gray-400">Urgency:</span> <span className="font-semibold">{message.appointment.urgency}</span></p>
                </div>
                <Link href="/dashboard/user/appointments" className="inline-block mt-1 text-blue-300 underline text-xs">
                  View in appointments
                </Link>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            AI is thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about a symptom, answer a question, or confirm a booking..."
          className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white transition-colors"
          aria-label="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
