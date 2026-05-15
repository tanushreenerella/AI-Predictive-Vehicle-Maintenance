'use client';

import { useState } from 'react';
import {
  Shield, Brain, Cpu, BarChart3,
  Car, Zap, CheckCircle,
  ArrowRight, Activity, Star
} from 'lucide-react';
import Link from 'next/link';

const features = [
  {
    icon: Brain,
    title: 'Multi-Agent AI System',
    description: 'Autonomous agents coordinate to predict, diagnose, and recommend maintenance actions in real time.',
  },
  {
    icon: Shield,
    title: 'Proactive Protection',
    description: 'Predict breakdowns before they happen using continuous sensor analysis and ML models.',
  },
  {
    icon: Cpu,
    title: 'Real-time Monitoring',
    description: 'Live sensor data analysis with instant alerts and AI-generated repair recommendations.',
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Root Cause Analysis and continuous learning from your vehicle health data over time.',
  },
];

const stats = [
  { value: '95%', label: 'Prediction Accuracy' },
  { value: '24/7', label: 'Monitoring' },
  { value: '500+', label: 'Vehicles Analysed' },
  { value: '4', label: 'AI Agents Working' },
];

const pipeline = [
  { icon: '📊', step: 1, title: 'Data Collection', desc: 'Vehicle sensors and OBD-II data' },
  { icon: '🤖', step: 2, title: 'ML Prediction', desc: 'XGBoost models analyse patterns' },
  { icon: '🧠', step: 3, title: 'AI Agents', desc: 'LangChain agents make decisions' },
  { icon: '📱', step: 4, title: 'Dashboard', desc: 'Real-time alerts and insights' },
];

const whyUs = [
  { icon: Zap, title: 'Predictive Alerts', desc: 'Get notified days before a breakdown, not after.' },
  { icon: Brain, title: 'Multi-Agent AI', desc: 'Diagnosis, scheduling, and RCA all automated.' },
  { icon: Activity, title: 'Real-time Data', desc: 'Sensor readings processed continuously.' },
  { icon: CheckCircle, title: 'Cost Reduction', desc: 'Avoid expensive emergency repairs.' },
];

const testimonials = [
  { name: 'Priya S.', role: 'Fleet Manager', text: 'ProactiveAI caught a transmission issue 3 days before it would have failed. Saved us thousands.', rating: 5 },
  { name: 'Rahul M.', role: 'Vehicle Owner', text: 'The AI assistant diagnosed my engine noise and booked a service slot in under 2 minutes.', rating: 5 },
  { name: 'Ananya K.', role: 'Logistics Head', text: 'We manage 20+ vehicles. The fleet dashboard gives us complete visibility at a glance.', rating: 5 },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="fixed top-0 w-full bg-gray-950/90 backdrop-blur-lg z-50 border-b border-gray-800/60">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <Car className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white leading-none">ProactiveAI</h1>
              <p className="text-xs text-gray-500 leading-none mt-0.5">Predictive Maintenance</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-sm text-gray-400 hover:text-white transition-colors">Login</Link>
            <Link href="/signup" className="text-sm text-gray-400 hover:text-white transition-colors">Sign Up</Link>
            <Link
              href="/dashboard/user"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Launch Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-400 font-medium mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            Powered by LangGraph Multi-Agent AI
          </div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-[1.1] tracking-tight">
            Predict Vehicle Failures
            <br />
            <span className="text-blue-400">Before They Happen</span>
          </h1>

          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
            AI-powered predictive maintenance that diagnoses symptoms, recommends services,
            and books appointments — automatically.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/signup">
              <button className="group flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-7 py-3 rounded-xl font-semibold transition-colors">
                Start Monitoring Free
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </Link>
            <Link href="/dashboard/user">
              <button className="px-7 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-xl font-semibold transition-colors">
                View Demo Dashboard
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats strip */}
      <section className="py-10 border-y border-gray-800/60">
        <div className="max-w-4xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {stats.map(({ value, label }) => (
              <div key={label}>
                <p className="text-3xl font-bold text-white">{value}</p>
                <p className="text-gray-500 text-sm mt-1">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">How It Works</h2>
            <p className="text-gray-500 text-sm mt-2">Four-stage autonomous pipeline</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4 relative">
            {pipeline.map((step, index) => (
              <div key={index} className="relative">
                <div className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-6 text-center transition-colors">
                  <div className="text-3xl mb-3">{step.icon}</div>
                  <div className="text-xs font-semibold text-blue-500 mb-1">Step {step.step}</div>
                  <h3 className="text-sm font-semibold text-white mb-1">{step.title}</h3>
                  <p className="text-gray-500 text-xs leading-relaxed">{step.desc}</p>
                </div>
                {index < pipeline.length - 1 && (
                  <div className="hidden md:flex absolute top-1/2 -right-2 z-10 -translate-y-1/2">
                    <ArrowRight className="w-4 h-4 text-gray-700" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">Core Capabilities</h2>
            <p className="text-gray-500 text-sm mt-2">Built for reliability and intelligence</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {features.map((f, i) => (
              <div key={i} className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-5 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-xl shrink-0">
                    <f.icon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-1">{f.title}</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">{f.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">Why Choose ProactiveAI</h2>
            <p className="text-gray-500 text-sm mt-2">Maintenance intelligence that actually works</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {whyUs.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="w-8 h-8 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center justify-center mb-3">
                  <Icon className="w-4 h-4 text-blue-400" />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
                <p className="text-gray-500 text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">What Users Say</h2>
            <p className="text-gray-500 text-sm mt-2">Real results from real fleet operators</p>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {testimonials.map(({ name, role, text, rating }) => (
              <div key={name} className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
                <div className="flex gap-0.5">
                  {Array.from({ length: rating }).map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">&ldquo;{text}&rdquo;</p>
                <div>
                  <p className="text-white text-sm font-medium">{name}</p>
                  <p className="text-gray-600 text-xs">{role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-3">
            Prevent Breakdowns Before They Happen
          </h2>
          <p className="text-gray-500 text-sm mb-8">
            Start monitoring your fleet with autonomous AI today. Free to get started.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/signup">
              <button className="px-7 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors">
                Get Started Free
              </button>
            </Link>
            <Link href="/login">
              <button className="px-7 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-xl font-semibold transition-colors">
                Login to Dashboard
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800/60 py-6 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-600 rounded-lg" />
            <span className="font-bold text-white text-sm">ProactiveAI</span>
          </div>
          <p className="text-gray-600 text-xs">© 2024 ProactiveAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
