'use client';

import {
  Shield, Brain, Cpu, BarChart3,
  Car, ArrowRight, Activity,
  AlertTriangle, CheckCircle, Bot, Calendar
} from 'lucide-react';
import Link from 'next/link';

const features = [
  {
    icon: Brain,
    title: 'Multi-Agent AI',
    description: 'Four autonomous agents — sensor analysis, diagnostic questioning, recommendation, and scheduling — work together in one pipeline.',
  },
  {
    icon: Shield,
    title: 'Failure Prediction',
    description: 'XGBoost ML model trained on engine sensor data predicts failures before they cause breakdowns.',
  },
  {
    icon: Cpu,
    title: 'Real-time Analysis',
    description: 'Submit sensor readings and get instant risk assessments, affected component identification, and confidence scores.',
  },
  {
    icon: BarChart3,
    title: 'Root Cause Reports',
    description: 'Automated RCA reports explain what is causing the risk and what to do about it — in plain language.',
  },
];

const pipeline = [
  { icon: Activity, step: 1, title: 'Submit Sensor Data', desc: 'RPM, temperature, oil pressure, battery voltage' },
  { icon: Brain, step: 2, title: 'ML Risk Scoring', desc: 'XGBoost model scores failure probability in real time' },
  { icon: Bot, step: 3, title: 'AI Agent Diagnosis', desc: 'LangGraph agents diagnose, recommend, and schedule' },
  { icon: Calendar, step: 4, title: 'Auto-book Service', desc: 'Appointment confirmed in the same conversation' },
];

const roles = [
  {
    icon: Car,
    title: 'Vehicle Owner',
    desc: 'Add your vehicles, submit sensor readings, and let the AI assistant diagnose symptoms, recommend services, and book appointments.',
    features: ['AI chat diagnosis', 'Failure probability scoring', 'Auto appointment booking', 'Health dashboard'],
  },
  {
    icon: BarChart3,
    title: 'Administrator',
    desc: 'Manage the platform — view all users, vehicles, appointments, and system-wide alerts from a dedicated admin panel.',
    features: ['User management', 'Fleet-wide alerts', 'Appointment oversight', 'System analytics'],
  },
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
      <section className="relative pt-36 pb-24 px-6 overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-150 h-100 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center relative">
          {/* Left */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-400 font-medium mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              LangGraph · XGBoost · FastAPI · Next.js
            </div>

            <h1 className="text-4xl md:text-5xl font-bold mb-5 leading-[1.15] tracking-tight">
              Predict Vehicle Failures
              <br />
              <span className="text-blue-400">Before They Happen</span>
            </h1>

            <p className="text-gray-400 text-base mb-8 leading-relaxed max-w-md">
              An end-to-end multi-agent AI system that monitors engine health,
              diagnoses faults through conversation, and books service automatically.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link href="/signup">
                <button className="group flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors">
                  Get Started Free
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </Link>
              <Link href="/dashboard/user">
                <button className="px-6 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-xl font-semibold transition-colors">
                  View Demo
                </button>
              </Link>
            </div>

            <div className="flex items-center gap-5 mt-8 pt-6 border-t border-gray-800/60">
              {[
                { icon: CheckCircle, label: 'Free to sign up' },
                { icon: CheckCircle, label: 'No credit card required' },
                { icon: CheckCircle, label: 'Live AI backend' },
              ].map(({ icon: Icon, label }) => (
                <div key={label} className="flex items-center gap-1.5 text-xs text-gray-500">
                  <Icon className="w-3.5 h-3.5 text-blue-500" />
                  {label}
                </div>
              ))}
            </div>
          </div>

          {/* Right — AI chat preview card */}
          <div className="hidden md:block">
            <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-2xl">
              {/* Window bar */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800 bg-gray-900/80">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-gray-700" />
                  <div className="w-3 h-3 rounded-full bg-gray-700" />
                  <div className="w-3 h-3 rounded-full bg-gray-700" />
                </div>
                <div className="flex-1 text-center text-xs text-gray-600">AI Assistant — ProactiveAI</div>
              </div>

              {/* Chat preview */}
              <div className="p-4 space-y-3 text-sm">
                <div className="flex items-start gap-2.5">
                  <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5 text-white" />
                  </div>
                  <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-3.5 py-2.5 text-gray-200 text-xs leading-relaxed max-w-xs">
                    Hi! Tell me a symptom and I'll diagnose your vehicle step by step.
                  </div>
                </div>

                <div className="flex justify-end">
                  <div className="bg-blue-600 rounded-2xl rounded-tr-sm px-3.5 py-2.5 text-white text-xs max-w-xs">
                    My engine is making a knocking sound at idle
                  </div>
                </div>

                <div className="flex items-start gap-2.5">
                  <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5 text-white" />
                  </div>
                  <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-3.5 py-2.5 text-gray-200 text-xs leading-relaxed max-w-xs">
                    Understood. How long has the sound been present — did it start suddenly or gradually?
                  </div>
                </div>

                {/* Recommendation card */}
                <div className="bg-red-500/5 border border-red-500/30 rounded-xl p-3 text-xs space-y-1.5 ml-8">
                  <div className="flex items-center gap-1.5 text-red-400 font-semibold">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Likely Issue: Rod Bearing Wear
                  </div>
                  <p className="text-gray-400">Urgency: <span className="text-red-400 font-medium">HIGH</span></p>
                  <p className="text-gray-400">Action: Schedule engine inspection within 48 hours</p>
                </div>
              </div>

              {/* Input bar */}
              <div className="px-4 pb-4">
                <div className="flex gap-2 bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 items-center">
                  <span className="text-xs text-gray-600 flex-1">Ask about a symptom...</span>
                  <div className="w-6 h-6 rounded-lg bg-blue-600 flex items-center justify-center">
                    <ArrowRight className="w-3 h-3 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">How It Works</h2>
            <p className="text-gray-500 text-sm mt-2">From sensor data to booked appointment in one flow</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {pipeline.map(({ icon: Icon, step, title, desc }, index) => (
              <div key={step} className="relative">
                <div className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-5 text-center transition-colors h-full">
                  <div className="w-10 h-10 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <Icon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="text-xs font-semibold text-blue-500 mb-1">Step {step}</div>
                  <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
                  <p className="text-gray-500 text-xs leading-relaxed">{desc}</p>
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
            <h2 className="text-2xl font-bold text-white">What It Does</h2>
            <p className="text-gray-500 text-sm mt-2">A full-stack AI maintenance platform</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {features.map((f, i) => (
              <div key={i} className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-6 transition-colors group">
                <div className="flex items-start gap-4">
                  <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-xl shrink-0 group-hover:bg-blue-500/15 transition-colors">
                    <f.icon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-1.5">{f.title}</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">{f.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who it's for */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">Two Roles, One Platform</h2>
            <p className="text-gray-500 text-sm mt-2">Separate dashboards for vehicle owners and administrators</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {roles.map(({ icon: Icon, title, desc, features }) => (
              <div key={title} className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <div className="w-10 h-10 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-base font-semibold text-white mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed mb-4">{desc}</p>
                <ul className="space-y-1.5">
                  {features.map(f => (
                    <li key={f} className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech stack strip */}
      <section className="py-10 border-t border-gray-800/60">
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-center text-xs text-gray-600 mb-6 uppercase tracking-wider">Built with</p>
          <div className="flex flex-wrap justify-center gap-3">
            {['LangGraph', 'LangChain', 'XGBoost', 'FastAPI', 'Next.js 15', 'Tailwind CSS', 'PostgreSQL', 'Railway'].map(tech => (
              <span key={tech} className="px-3 py-1.5 bg-gray-900 border border-gray-800 rounded-lg text-xs text-gray-400">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-3">
            Ready to Try It?
          </h2>
          <p className="text-gray-500 text-sm mb-8 leading-relaxed">
            Sign up, add your vehicle, and let the AI assistant walk you through a full diagnosis.
            The entire multi-agent pipeline runs live.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/signup">
              <button className="px-7 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors">
                Create Free Account
              </button>
            </Link>
            <Link href="/login">
              <button className="px-7 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-xl font-semibold transition-colors">
                Sign In
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
          <p className="text-gray-600 text-xs">Built with LangGraph + XGBoost. All AI runs live.</p>
        </div>
      </footer>
    </div>
  );
}
