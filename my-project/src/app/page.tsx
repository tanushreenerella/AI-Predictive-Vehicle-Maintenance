'use client';

import { useState } from 'react';
import { 
  Shield, Brain, Cpu, BarChart3, 
  Car, Users, Zap, CheckCircle, 
  ArrowRight, AlertTriangle, Settings,Calendar
} from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState('overview');

  const features = [
    {
      icon: <Brain className="w-5 h-5 text-blue-400" />,
      title: "Multi-Agent AI System",
      description: "Autonomous agents coordinate to predict, diagnose, and recommend maintenance actions."
    },
    {
      icon: <Shield className="w-5 h-5 text-blue-400" />,
      title: "Proactive Protection",
      description: "Predict breakdowns before they happen using real-time sensor analysis."
    },
    {
      icon: <Cpu className="w-5 h-5 text-blue-400" />,
      title: "Real-time Monitoring",
      description: "Live sensor data analysis with instant alerts and AI recommendations."
    },
    {
      icon: <BarChart3 className="w-5 h-5 text-blue-400" />,
      title: "Advanced Analytics",
      description: "Root Cause Analysis and continuous learning from vehicle health data."
    }
  ];

  const systemArchitecture = [
    {
      title: "Data Collection",
      description: "Vehicle sensors and OBD-II data",
      icon: "📊",
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "ML Prediction",
      description: "XGBoost models analyze patterns",
      icon: "🤖",
      color: "from-cyan-500 to-teal-500"
    },
    {
      title: "AI Agents",
      description: "LangChain agents make decisions",
      icon: "🧠",
      color: "from-teal-500 to-green-500"
    },
    {
      title: "Dashboard",
      description: "Real-time visualization & alerts",
      icon: "📱",
      color: "from-green-500 to-emerald-500"
    }
  ];

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-900 via-blue-900/20 to-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gray-900/90 backdrop-blur-lg z-50 border-b border-blue-800/30">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-linear-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center">
                <Car className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-linear-to-br from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  ProactiveAI
                </h1>
                <p className="text-xs text-gray-400">Predictive Maintenance System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <Link href="/login" className="text-gray-300 hover:text-white transition-colors">
                Login
              </Link>
              <Link href="/signup" className="text-gray-300 hover:text-white transition-colors">
                Sign Up
              </Link>
              <Link 
                href="/dashboard/user" 
                className="bg-linear-to-br from-blue-600 to-cyan-600 text-white px-6 py-2 rounded-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all"
              >
                Launch Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-24 px-6">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-400 font-medium mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              Powered by LangGraph Multi-Agent AI
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              <span className="bg-linear-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent">
                Intelligent Vehicle
              </span>
              <br />
              <span className="text-white">Predictive Maintenance</span>
            </h1>
            <p className="text-gray-400 mb-10 max-w-2xl mx-auto text-lg leading-relaxed">
              AI-powered system that predicts vehicle failures before they happen,
              with autonomous multi-agent diagnosis and scheduling.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link href="/signup">
                <button className="group flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-7 py-3 rounded-xl font-semibold transition-colors">
                  Get Started Free
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </Link>
              <Link href="/dashboard/admin">
                <button className="px-7 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-xl font-semibold transition-colors">
                  Admin Demo
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Flow */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">How It Works</h2>
            <p className="text-gray-500 text-sm mt-2">Four-stage autonomous pipeline</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4 relative">
            {systemArchitecture.map((step, index) => (
              <div key={index} className="relative group">
                <div className="bg-gray-800/40 border border-gray-700/60 hover:border-blue-500/40 rounded-xl p-5 text-center transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-0.5 cursor-default">
                  <div className="text-2xl mb-3">{step.icon}</div>
                  <div className="text-xs font-semibold text-blue-500 mb-1">Step {index + 1}</div>
                  <h3 className="text-sm font-semibold text-white mb-1">{step.title}</h3>
                  <p className="text-gray-500 text-xs leading-relaxed">{step.description}</p>
                </div>
                {index < systemArchitecture.length - 1 && (
                  <div className="hidden md:flex absolute top-1/2 -right-2 z-10 -translate-y-1/2">
                    <ArrowRight className="w-4 h-4 text-gray-600" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">Core Capabilities</h2>
            <p className="text-gray-500 text-sm mt-2">Built for reliability and intelligence</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <div key={index} className="group bg-gray-800/40 border border-gray-700/60 hover:border-gray-600 rounded-xl p-5 transition-all duration-200 hover:-translate-y-0.5">
                <div className="flex items-start gap-4">
                  <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-xl shrink-0">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-1">{feature.title}</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* CTA Section */}
      <section className="py-20 px-6 border-t border-gray-800/60">
        <div className="container mx-auto max-w-2xl text-center">
          <h2 className="text-2xl font-bold text-white mb-3">
            Ready to Transform Vehicle Maintenance?
          </h2>
          <p className="text-gray-500 mb-8 text-sm">
            Start monitoring your fleet with autonomous AI today.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/signup">
              <button className="px-7 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors">
                Start Free Trial
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

      <footer className="border-t border-gray-800/60 py-6 px-6">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-3">
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