'use client';

import { useState } from 'react';
import { 
  Calendar as CalendarIcon, ChevronLeft, ChevronRight, 
  Plus, Clock, MapPin, User, Car
} from 'lucide-react';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, 
  eachDayOfInterval, isSameMonth, isToday, isSameDay } from 'date-fns';

interface ServiceEvent {
  id: number;
  title: string;
  description: string;
  vehicle: string;
  serviceType: 'routine' | 'emergency' | 'inspection';
  date: Date;
  time: string;
  duration: number; // in hours
  location: string;
  technician?: string;
  status: 'scheduled' | 'in-progress' | 'completed' | 'cancelled';
}

export default function ServiceCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week' | 'day'>('month');

  // Mock service events
  const [serviceEvents, setServiceEvents] = useState<ServiceEvent[]>([
    {
      id: 1,
      title: 'Oil Change Service',
      description: 'Routine oil change and filter replacement',
      vehicle: 'Tesla Model 3',
      serviceType: 'routine',
      date: new Date(new Date().getFullYear(), new Date().getMonth(), 15),
      time: '09:00 AM',
      duration: 2,
      location: 'Main Service Center',
      technician: 'John Doe',
      status: 'scheduled'
    },
    {
      id: 2,
      title: 'Brake System Inspection',
      description: 'Complete brake system check and pad replacement',
      vehicle: 'BMW X5',
      serviceType: 'inspection',
      date: new Date(new Date().getFullYear(), new Date().getMonth(), 18),
      time: '02:00 PM',
      duration: 3,
      location: 'Downtown Service',
      technician: 'Jane Smith',
      status: 'scheduled'
    },
    {
      id: 3,
      title: 'Engine Diagnostics',
      description: 'Comprehensive engine diagnostic and tuning',
      vehicle: 'Ford F-150',
      serviceType: 'emergency',
      date: new Date(new Date().getFullYear(), new Date().getMonth(), 20),
      time: '10:30 AM',
      duration: 4,
      location: 'Main Service Center',
      status: 'scheduled'
    },
    {
      id: 4,
      title: 'Tire Rotation',
      description: 'Tire rotation and pressure check',
      vehicle: 'Toyota Camry',
      serviceType: 'routine',
      date: new Date(new Date().getFullYear(), new Date().getMonth(), 22),
      time: '11:00 AM',
      duration: 1.5,
      location: 'West Service Center',
      technician: 'Mike Johnson',
      status: 'scheduled'
    }
  ]);

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getEventsForDate = (date: Date) => {
    return serviceEvents.filter(event => isSameDay(event.date, date));
  };

  const getServiceTypeColor = (type: string) => {
    switch (type) {
      case 'routine': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'emergency': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'inspection': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-500/20 text-blue-400';
      case 'in-progress': return 'bg-yellow-500/20 text-yellow-400';
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'cancelled': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <CalendarIcon className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">Service Calendar</h2>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentDate(subMonths(currentDate, 1))}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            
            <h3 className="text-lg font-semibold text-white min-w-32 text-center">
              {format(currentDate, 'MMMM yyyy')}
            </h3>
            
            <button
              onClick={() => setCurrentDate(addMonths(currentDate, 1))}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex gap-2">
            {(['month', 'week', 'day'] as const).map((viewType) => (
              <button
                key={viewType}
                onClick={() => setView(viewType)}
                className={`px-4 py-2 rounded-lg capitalize ${
                  view === viewType
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {viewType}
              </button>
            ))}
          </div>
          
          <button className="flex items-center gap-2 px-4 py-2 bg-linear-to-br from-blue-600 to-cyan-600 text-white rounded-lg hover:shadow-lg hover:shadow-blue-500/30 transition-all">
            <Plus className="w-4 h-4" />
            <span>Schedule Service</span>
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2 mb-4">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <div key={day} className="text-center py-2 text-sm font-semibold text-gray-400">
            {day}
          </div>
        ))}
        
        {Array.from({ length: new Date(monthStart).getDay() }).map((_, index) => (
          <div key={`empty-${index}`} className="h-32 bg-gray-900/20 rounded-lg"></div>
        ))}
        
        {days.map((day) => {
          const dayEvents = getEventsForDate(day);
          const isCurrentDay = isToday(day);
          const isSelectedDay = isSameDay(day, selectedDate);
          
          return (
            <div
              key={day.toISOString()}
              onClick={() => setSelectedDate(day)}
              className={`h-32 p-2 rounded-lg border cursor-pointer transition-all ${
                isCurrentDay
                  ? 'border-blue-500 bg-blue-500/10'
                  : isSelectedDay
                  ? 'border-blue-500/50 bg-blue-500/5'
                  : 'border-gray-700/50 hover:border-blue-500/30'
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className={`font-semibold ${
                  isCurrentDay ? 'text-blue-400' : 'text-gray-300'
                }`}>
                  {format(day, 'd')}
                </span>
                
                {dayEvents.length > 0 && (
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                )}
              </div>
              
              <div className="space-y-1 max-h-20 overflow-y-auto">
                {dayEvents.slice(0, 2).map((event) => (
                  <div
                    key={event.id}
                    className={`p-1.5 text-xs rounded border ${getServiceTypeColor(event.serviceType)}`}
                  >
                    <div className="font-medium truncate">{event.title}</div>
                    <div className="text-xs opacity-75 truncate">{event.time}</div>
                  </div>
                ))}
                
                {dayEvents.length > 2 && (
                  <div className="text-xs text-gray-500 text-center">
                    +{dayEvents.length - 2} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Day Events */}
      <div className="border-t border-gray-800 pt-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Services for {format(selectedDate, 'MMMM d, yyyy')}
        </h3>
        
        {getEventsForDate(selectedDate).length > 0 ? (
          <div className="space-y-4">
            {getEventsForDate(selectedDate).map((event) => (
              <div
                key={event.id}
                className="bg-gray-900/50 p-4 rounded-xl border border-gray-700/50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold text-white">{event.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${getServiceTypeColor(event.serviceType)}`}>
                        {event.serviceType}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(event.status)}`}>
                        {event.status}
                      </span>
                    </div>
                    
                    <p className="text-gray-400 text-sm mb-3">{event.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="flex items-center gap-2">
                        <Car className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-300">{event.vehicle}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-300">
                          {event.time} ({event.duration}h)
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-300">{event.location}</span>
                      </div>
                      
                      {event.technician && (
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-300">{event.technician}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="ml-4 flex flex-col gap-2">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Reschedule
                    </button>
                    <button className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors">
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <CalendarIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No services scheduled for this day</p>
            <button className="mt-4 text-blue-400 hover:text-blue-300">
              Schedule a service →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}