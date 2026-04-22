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
      icon: <Brain className="w-10 h-10 text-blue-500" />,
      title: "Multi-Agent AI System",
      description: "Autonomous agents coordinate to predict, diagnose, and recommend maintenance"
    },
    {
      icon: <Shield className="w-10 h-10 text-blue-600" />,
      title: "Proactive Protection",
      description: "Predict breakdowns before they happen with real-time failure prediction"
    },
    {
      icon: <Cpu className="w-10 h-10 text-cyan-500" />,
      title: "Real-time Monitoring",
      description: "Live sensor data analysis with instant alerts and recommendations"
    },
    {
      icon: <BarChart3 className="w-10 h-10 text-indigo-500" />,
      title: "Advanced Analytics",
      description: "Root Cause Analysis and continuous learning from vehicle data"
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
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="bg-linear-to-br from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                Intelligent Vehicle
              </span>
              <br />
              <span className="text-white">Predictive Maintenance</span>
            </h1>
            <p className="text-xl text-gray-300 mb-10 max-w-3xl mx-auto">
              AI-powered system that predicts vehicle failures before they happen, 
              saving costs and preventing breakdowns with autonomous agentic AI.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <button className="group bg-linear-to-br from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all flex items-center gap-3">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>
              <Link href="/dashboard/admin">
                <button className="border border-blue-500/30 text-blue-400 px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-900/20 transition-all">
                  Admin Demo
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Flow */}
      <section className="py-16 px-6">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-center mb-12 text-white">
            System Architecture Flow
          </h2>
          
          <div className="relative">
            {/* Connection lines */}
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-linear-to-br from-blue-500/20 via-cyan-500/20 to-teal-500/20 transform -translate-y-1/2 hidden md:block" />
            
            <div className="grid md:grid-cols-4 gap-8 relative">
              {systemArchitecture.map((step, index) => (
                <div key={index} className="relative">
                  <div className={`bg-linear-to-br ${step.color} p-1 rounded-2xl`}>
                    <div className="bg-gray-900 rounded-xl p-6 text-center">
                      <div className="text-3xl mb-4">{step.icon}</div>
                      <h3 className="text-xl font-semibold mb-2 text-white">{step.title}</h3>
                      <p className="text-gray-400 text-sm">{step.description}</p>
                    </div>
                  </div>
                  {index < systemArchitecture.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 -right-4 w-8">
                      <ArrowRight className="w-8 h-8 text-blue-500/50" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6 bg-gray-900/50">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-center mb-12 text-white">
            Core Features
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-2xl border border-blue-800/30 hover:border-blue-500/50 transition-all">
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-blue-900/30 rounded-xl">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2 text-white">{feature.title}</h3>
                    <p className="text-gray-400">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="bg-linear-to-br from-gray-900 to-blue-900/30 rounded-3xl p-8 border border-blue-800/30">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold text-white">Interactive Dashboards</h2>
                <p className="text-gray-400">Real-time monitoring for users and administrators</p>
              </div>
              <div className="flex gap-4">
                <button 
                  onClick={() => setActiveTab('user')}
                  className={`px-4 py-2 rounded-lg transition-all ${activeTab === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                >
                  User View
                </button>
                <button 
                  onClick={() => setActiveTab('admin')}
                  className={`px-4 py-2 rounded-lg transition-all ${activeTab === 'admin' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                >
                  Admin View
                </button>
              </div>
            </div>

            {/* Dashboard Preview */}
            <div className="bg-gray-900/50 rounded-2xl p-6 border border-blue-800/20">
              {activeTab === 'user' ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* User Dashboard Preview */}
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-blue-400">Vehicle Health</h3>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <div className="space-y-3">
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div className="h-full bg-linear-to-br from-green-500 to-cyan-500 w-3/4"></div>
                      </div>
                      <div className="text-sm text-gray-400">Overall Score: 85%</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-blue-400">Active Alerts</h3>
                      <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    </div>
                    <div className="text-2xl font-bold text-white">2</div>
                    <div className="text-sm text-gray-400">Require Attention</div>
                  </div>
                  
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-blue-400">Next Service</h3>
                      <Calendar className="w-5 h-5 text-cyan-500" />
                    </div>
                    <div className="text-lg font-bold text-white">Oct 28, 2023</div>
                    <div className="text-sm text-gray-400">In 12 days</div>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Admin Dashboard Preview */}
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="text-sm text-gray-400">Total Vehicles</div>
                    <div className="text-2xl font-bold text-white">156</div>
                  </div>
                  
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="text-sm text-gray-400">High Risk</div>
                    <div className="text-2xl font-bold text-red-400">12</div>
                  </div>
                  
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="text-sm text-gray-400">AI Agents Active</div>
                    <div className="text-2xl font-bold text-green-400">4</div>
                  </div>
                  
                  <div className="bg-gray-800/30 p-4 rounded-xl">
                    <div className="text-sm text-gray-400">Prediction Accuracy</div>
                    <div className="text-2xl font-bold text-cyan-400">92.4%</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl text-center">
          <div className="bg-linear-to-br from-blue-900/30 to-cyan-900/30 rounded-3xl p-12 border border-blue-800/30">
            <h2 className="text-4xl font-bold mb-6 text-white">
              Ready to Transform Vehicle Maintenance?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of users already preventing breakdowns with AI
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <button className="bg-linear-to-br from-blue-600 to-cyan-600 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all">
                  Start Free Trial
                </button>
              </Link>
              <Link href="/login">
                <button className="border border-blue-500 text-blue-400 px-10 py-4 rounded-xl text-lg font-semibold hover:bg-blue-900/20 transition-all">
                  Login to Dashboard
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-gray-900/80 border-t border-blue-800/30 py-8 px-6">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-linear-to-br from-blue-600 to-cyan-500 rounded-lg"></div>
              <span className="text-xl font-bold bg-linear-to-br from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                ProactiveAI
              </span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2024 ProactiveAI Predictive Maintenance System. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}