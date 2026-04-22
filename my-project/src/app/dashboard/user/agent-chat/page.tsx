'use client';

import { useState } from 'react';

const API_BASE = 'http://localhost:8000';

type Message = {
  role: 'user' | 'agent';
  text: string;
};

export default function AgentChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

   const userMsg: Message = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
      }),
    });

    const data = await res.json();

    setMessages(prev => [
      ...prev,
      { role: 'agent', text: data.reply },
    ]);

    setLoading(false);
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold text-white">
        🤖 AI Assistant
      </h1>

      <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 h-100 overflow-y-auto space-y-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%]
              ${m.role === 'user'
                ? 'bg-blue-600 text-white ml-auto'
                : 'bg-gray-700 text-gray-100'}
            `}
          >
            {m.text}
          </div>
        ))}

        {loading && (
          <p className="text-gray-400 text-sm">AI is thinking…</p>
        )}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about your vehicle or appointment…"
          className="flex-1 bg-gray-800 border border-gray-600 rounded-lg p-3 text-white"
        />
        <button
          onClick={sendMessage}
          className="px-5 bg-blue-600 rounded-lg text-white"
        >
          Send
        </button>
      </div>
    </div>
  );
}
