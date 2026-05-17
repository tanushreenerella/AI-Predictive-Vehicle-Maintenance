'use client';

import { useEffect, useRef, useState } from 'react';
import { Bot, Calendar, Clock, Send, Wrench, Zap, Activity, Stethoscope, BookOpen, ChevronDown } from 'lucide-react';
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

type DiagnosticAnswer = {
  answer: string;
};

type ConversationState = {
  messages?: unknown[];
  phase?: string;
  symptom?: string | null;
  diagnostic_answers?: DiagnosticAnswer[];
  issue_context?: unknown;
  recommendation?: Recommendation | null;
  scheduling?: Scheduling | null;
  _frontendDiagnosticGuard?: boolean;
  [key: string]: unknown;
};

type ChatResponse = {
  reply?: string;
  state?: ConversationState;
  recommendation?: Recommendation | null;
  scheduling?: Scheduling | null;
  appointment?: Appointment | null;
  tool_calls?: unknown;
};

type Message = {
  role: 'user' | 'agent';
  text: string;
  ts: string;
  recommendation?: Recommendation | null;
  scheduling?: Scheduling | null;
  appointment?: Appointment | null;
  tool_calls?: string[];
};

const PROMPTS = [
  { icon: Stethoscope, label: 'Engine noise', text: 'My engine is making a strange knocking noise' },
  { icon: Zap, label: 'Battery issue', text: 'My battery is draining fast' },
  { icon: Calendar, label: 'Book service', text: 'I want to book a service appointment' },
  { icon: Activity, label: 'Vehicle health', text: 'Show me my vehicle health status' },
  { icon: BookOpen, label: 'Next maintenance', text: 'When is my next maintenance due?' },
];

const MIN_DIAGNOSTIC_ANSWERS = 2;

const DIAGNOSTIC_FOLLOW_UPS = [
  'When does the knocking noise happen most often: during startup, idle, acceleration, or braking?',
  'Is the noise coming from the engine bay, wheels, or under the vehicle? Also, does it get louder with speed?',
];

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function isBookingRequest(text: string) {
  const msg = text.toLowerCase();
  return ['book', 'schedule', 'appointment', 'service'].some((word) => msg.includes(word));
}

function diagnosticAnswerCount(state: ConversationState | null) {
  return Array.isArray(state?.diagnostic_answers) ? state.diagnostic_answers.length : 0;
}

function diagnosticQuestion(count: number) {
  return DIAGNOSTIC_FOLLOW_UPS[Math.min(count, DIAGNOSTIC_FOLLOW_UPS.length - 1)];
}

function hasPrematureRecommendation(data: ChatResponse, text: string) {
  const count = diagnosticAnswerCount(data?.state ?? null);
  return !isBookingRequest(text) && Boolean(data?.recommendation || data?.scheduling) && count < MIN_DIAGNOSTIC_ANSWERS;
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3 bg-gray-800 border border-gray-700/60 rounded-2xl rounded-tl-sm w-fit">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-gray-400"
          style={{ animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
        />
      ))}
    </div>
  );
}

export default function AgentChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      text: "Hi! I'm your AI vehicle assistant. Tell me a symptom and I'll diagnose it step by step, or say you want to book service.",
      ts: now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState<VehicleOption[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>('');
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const messagesRef = useRef<HTMLDivElement>(null);
  const isFirstRender = useRef(true);

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
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function sendMessageWithText(text: string) {
    if (!text.trim() || loading) return;

    setMessages((prev) => [...prev, { role: 'user', text, ts: now() }]);
    setInput('');
    setLoading(true);

    try {
      let stateForRequest = conversationState;

      if (conversationState?._frontendDiagnosticGuard) {
        const answers = [
          ...(Array.isArray(conversationState.diagnostic_answers) ? conversationState.diagnostic_answers : []),
          { answer: text },
        ];

        stateForRequest = {
          ...conversationState,
          diagnostic_answers: answers,
          recommendation: null,
          scheduling: null,
          issue_context: null,
          phase: answers.length >= MIN_DIAGNOSTIC_ANSWERS ? 'recommended' : 'diagnosing',
        };

        if (answers.length < MIN_DIAGNOSTIC_ANSWERS) {
          setConversationState(stateForRequest);
          setMessages((prev) => [
            ...prev,
            {
              role: 'agent',
              text: diagnosticQuestion(answers.length),
              ts: now(),
              tool_calls: ['supervisor', 'diagnostic_questions_tool'],
            },
          ]);
          return;
        }
      }

      const res = await fetchWithAuth(`${API_BASE}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: text,
          vehicle_id: selectedVehicleId || undefined,
          state: stateForRequest,
        }),
      });

      const data: ChatResponse = await res.json();

      if (hasPrematureRecommendation(data, text)) {
        const guardedState = {
          ...(data.state ?? {}),
          _frontendDiagnosticGuard: true,
          phase: 'diagnosing',
          symptom: data.state?.symptom || text,
          diagnostic_answers: Array.isArray(data.state?.diagnostic_answers) ? data.state.diagnostic_answers : [],
          issue_context: null,
          recommendation: null,
          scheduling: null,
        };

        setConversationState(guardedState);
        setMessages((prev) => [
          ...prev,
          {
            role: 'agent',
            text: diagnosticQuestion(diagnosticAnswerCount(guardedState)),
            ts: now(),
            tool_calls: ['supervisor', 'diagnostic_questions_tool'],
          },
        ]);
        return;
      }

      setConversationState(data.state ?? null);
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          text: data.reply,
          ts: now(),
          recommendation: data.recommendation ?? null,
          scheduling: data.scheduling ?? null,
          appointment: data.appointment ?? null,
          tool_calls: Array.isArray(data.tool_calls) && data.tool_calls.length > 0 ? data.tool_calls : undefined,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'agent', text: 'Sorry, I could not connect to the AI service. Please try again.', ts: now() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function sendMessage() {
    sendMessageWithText(input.trim());
  }

  const urgencyColor = (urgency?: string) =>
    urgency === 'HIGH'
      ? 'border-red-500/40 bg-red-500/5 text-red-300'
      : urgency === 'MEDIUM'
        ? 'border-yellow-500/40 bg-yellow-500/5 text-yellow-200'
        : 'border-green-500/40 bg-green-500/5 text-green-200';

  const hasConversation = messages.length > 1;

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-120px)] gap-0">
      {/* Header */}
      <div className="flex items-center justify-between pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <Bot className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">AI Assistant</h1>
            <p className="text-gray-500 text-xs">Diagnosis, recommendations & booking</p>
          </div>
        </div>

        {vehicles.length > 0 && (
          <div className="relative">
            <select
              value={selectedVehicleId}
              onChange={(e) => {
                setSelectedVehicleId(e.target.value);
                setConversationState(null);
              }}
              className="appearance-none bg-gray-800/60 border border-gray-700/60 rounded-xl px-4 py-2 pr-8 text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
            >
              {vehicles.map((v) => (
                <option key={v.id} value={String(v.id)}>
                  {v.name}{v.ai_risk_level ? ` · ${v.ai_risk_level} risk` : ''}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
          </div>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 bg-gray-900/60 border border-gray-700/60 rounded-2xl overflow-hidden flex flex-col">
        <div ref={messagesRef} className="flex-1 overflow-y-auto p-4 space-y-4">

          {/* Welcome card — shown only on first visit */}
          {!hasConversation && (
            <div className="bg-gray-800/60 border border-gray-700/40 rounded-2xl p-5 mb-2">
              <div className="flex items-center gap-2 mb-1">
                <Bot className="w-4 h-4 text-blue-400" />
                <span className="text-white font-medium text-sm">AI Vehicle Assistant</span>
                <span className="text-xs text-gray-500 ml-auto">{messages[0].ts}</span>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">{messages[0].text}</p>
            </div>
          )}

          {/* Suggested prompts — shown only before conversation starts */}
          {!hasConversation && (
            <div>
              <p className="text-xs text-gray-600 mb-2 px-1">Try asking...</p>
              <div className="flex flex-wrap gap-2">
                {PROMPTS.map(({ icon: Icon, label, text }) => (
                  <button
                    key={label}
                    onClick={() => sendMessageWithText(text)}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-800/60 border border-gray-700/60 hover:border-gray-600 hover:bg-gray-800 rounded-xl text-sm text-gray-300 transition-colors"
                  >
                    <Icon className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages (skip index 0 if not hasConversation since we show welcome card) */}
          {(hasConversation ? messages : messages.slice(1)).map((message, index) => (
            <div key={index} className={`flex flex-col gap-2 ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className="flex items-center gap-1.5 mb-0.5">
                {message.role === 'agent' && <Bot className="w-3 h-3 text-blue-400" />}
                <span className="text-xs text-gray-600">{message.ts}</span>
              </div>

              <div
                className={`px-4 py-3 rounded-2xl max-w-[82%] text-sm leading-relaxed ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-gray-800 border border-gray-700/60 text-gray-100 rounded-tl-sm'
                }`}
              >
                {message.text}
              </div>

              {message.role === 'agent' && message.tool_calls && message.tool_calls.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap max-w-[82%]">
                  <span className="text-xs text-gray-600">Agents:</span>
                  {message.tool_calls.map((tool, i) => (
                    <span key={i} className="flex items-center gap-1 text-xs px-2 py-0.5 bg-gray-800/60 border border-gray-700/40 rounded-full text-gray-500">
                      <span className="w-1 h-1 rounded-full bg-blue-500 shrink-0" />
                      {tool}
                    </span>
                  ))}
                </div>
              )}

              {message.recommendation && !message.appointment && (
                <div className={`max-w-[82%] rounded-xl border p-4 space-y-2.5 text-sm ${urgencyColor(message.recommendation.urgency)}`}>
                  <div className="flex items-center gap-2 font-semibold">
                    <Wrench className="w-4 h-4" />
                    Service Recommendation
                    <span className="ml-auto text-xs font-normal px-2 py-0.5 rounded-full bg-black/20 border border-current/20">
                      {message.recommendation.urgency}
                    </span>
                  </div>
                  <div className="grid gap-1.5 text-sm">
                    <p><span className="text-gray-400">Issue:</span> {message.recommendation.likely_issue}</p>
                    <p><span className="text-gray-400">Service:</span> {message.recommendation.recommended_service}</p>
                    <p><span className="text-gray-400">Cost:</span> {message.recommendation.estimated_cost}</p>
                    <p><span className="text-gray-400">Timeframe:</span> {message.recommendation.timeframe}</p>
                  </div>
                </div>
              )}

              {message.scheduling && !message.appointment && (
                <div className="max-w-[82%] rounded-xl border border-blue-500/30 bg-blue-500/5 p-4 space-y-2 text-sm text-blue-100">
                  <div className="flex items-center gap-2 font-semibold">
                    <Clock className="w-4 h-4" />
                    Suggested Appointment
                  </div>
                  <div className="space-y-1 text-gray-300">
                    <p><span className="text-gray-500">Service:</span> {message.scheduling.service_type}</p>
                    <p><span className="text-gray-500">Priority:</span> {message.scheduling.recommended_urgency}</p>
                    {message.scheduling.selected_slot && (
                      <p><span className="text-gray-500">Slot:</span> {message.scheduling.selected_slot.date} at {message.scheduling.selected_slot.time}</p>
                    )}
                    <p className="text-gray-500 text-xs">{message.scheduling.reason}</p>
                  </div>
                </div>
              )}

              {message.appointment && (
                <div className={`max-w-[82%] rounded-xl border p-4 space-y-2 text-sm ${urgencyColor(message.appointment.urgency)}`}>
                  <div className="flex items-center gap-2 font-semibold">
                    <Calendar className="w-4 h-4" />
                    Appointment Confirmed
                  </div>
                  <div className="space-y-1 text-gray-300">
                    <p><span className="text-gray-400">Vehicle:</span> {message.appointment.vehicle}</p>
                    <p><span className="text-gray-400">Service:</span> {message.appointment.service_type}</p>
                    <p><span className="text-gray-400">Date:</span> {message.appointment.date} at {message.appointment.time}</p>
                  </div>
                  <Link href="/dashboard/user/appointments" className="inline-flex items-center gap-1 mt-1 text-blue-300 hover:text-blue-200 text-xs underline">
                    View in appointments
                  </Link>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex flex-col items-start gap-1">
              <div className="flex items-center gap-1.5 mb-0.5">
                <Bot className="w-3 h-3 text-blue-400" />
                <span className="text-xs text-gray-600">thinking...</span>
              </div>
              <TypingDots />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-gray-700/60 p-3">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask about a symptom, answer a question, or confirm a booking..."
              className="flex-1 bg-gray-800/60 border border-gray-700/60 rounded-xl px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-white transition-colors"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
