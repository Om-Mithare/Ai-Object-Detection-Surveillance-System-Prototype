import React, { useState, useEffect, useRef } from 'react';
import { Activity, Camera, Car, Users, UploadCloud, AlertTriangle, Search } from 'lucide-react';
import { getStats, getEvents, uploadVideo } from './services/api';
import KPICard from './components/KPICard';
import EventCard from './components/EventCard';
import AnalyticsChart from './components/AnalyticsChart';

function App() {
  const [stats, setStats] = useState({ total_events: 0, total_persons: 0, total_vehicles: 0, total_incidents: 0 });
  const [events, setEvents] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef(null);

  const fetchData = async () => {
    try {
      const statsData = await getStats();
      setStats(statsData);
      
      const eventsData = await getEvents(0, 50, searchQuery);
      setEvents(eventsData);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll for new events every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [searchQuery]); // Re-fetch when search query changes

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      await uploadVideo(file);
      alert("Video uploaded and processing started!");
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Is backend running?");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-background text-slate-200">
      {/* Navbar */}
      <nav className="bg-surface border-b border-slate-700 px-6 py-4 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center border border-primary/30 shadow-[0_0_15px_rgba(56,189,248,0.2)]">
            <Camera className="text-primary w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent hidden sm:block">
            Sentinel AI System
          </h1>
        </div>
        
        <div className="flex-1 max-w-md mx-4">
           <div className="relative">
             <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
               <Search className="h-5 w-5 text-slate-400" />
             </div>
             <input
               type="text"
               value={searchQuery}
               onChange={(e) => setSearchQuery(e.target.value)}
               placeholder="Search by object, event, or plate..."
               className="block w-full pl-10 pr-3 py-2 border border-slate-600 rounded-md leading-5 bg-slate-800 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm transition-colors"
             />
           </div>
        </div>

        <div>
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="video/mp4,image/jpeg,image/png"
            className="hidden" 
          />
          <button 
            onClick={handleUploadClick}
            disabled={uploading}
            className="flex items-center space-x-2 bg-primary hover:bg-sky-400 text-slate-900 px-4 py-2 rounded-lg font-medium transition-colors shadow-[0_0_15px_rgba(56,189,248,0.3)] disabled:opacity-50"
          >
            <UploadCloud className="w-5 h-5" />
            <span className="hidden sm:inline">{uploading ? 'Uploading...' : 'Process Video'}</span>
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* KPI Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard title="Total Events" value={stats.total_events} icon={Activity} colorClass="bg-primary text-primary" />
          <KPICard title="Persons Detected" value={stats.total_persons} icon={Users} colorClass="bg-secondary text-secondary" />
          <KPICard title="Vehicles Detected" value={stats.total_vehicles} icon={Car} colorClass="bg-accent text-accent" />
          <KPICard title="Flagged Incidents" value={stats.total_incidents} icon={AlertTriangle} colorClass="bg-red-500 text-red-500" />
        </div>

        {/* Analytics & Events Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Analytics Chart (Left Column, spans 2) */}
          <div className="lg:col-span-2 space-y-6">
            <AnalyticsChart stats={stats} />
          </div>

          {/* Recent Events (Right Column) */}
          <div className="bg-surface rounded-xl border border-slate-700 shadow-lg flex flex-col h-[600px] lg:h-auto">
             <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-white">Event Log</h2>
                {searchQuery && (
                  <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                    Filtered
                  </span>
                )}
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {events.length === 0 ? (
                  <div className="text-center text-slate-500 mt-10">
                    {searchQuery ? "No events match your search." : "No events detected yet."}
                  </div>
                ) : (
                  events.map(event => (
                    <EventCard key={event.id} event={event} />
                  ))
                )}
              </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
