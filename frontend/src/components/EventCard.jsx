import React from 'react';
import { AlertCircle, Car, User } from 'lucide-react';

const EventCard = ({ event }) => {
  const getIcon = () => {
    if (event.event_type.includes('INCIDENT')) return <AlertCircle className="text-red-400 w-5 h-5" />;
    if (event.object_type.includes('person')) return <User className="text-primary w-5 h-5" />;
    return <Car className="text-accent w-5 h-5" />;
  };

  const getBadgeColor = () => {
    if (event.event_type.includes('INCIDENT')) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (event.object_type.includes('person')) return 'bg-primary/20 text-primary border-primary/30';
    return 'bg-accent/20 text-accent border-accent/30';
  };

  return (
    <div className="bg-surface p-4 rounded-lg border border-slate-700/50 hover:bg-slate-800 transition-colors flex items-center space-x-4">
      <div className="flex-shrink-0">
        {/* Placeholder for actual cropped image if served by static backend */}
        <div className="w-16 h-16 bg-slate-700 rounded-md flex items-center justify-center overflow-hidden">
           {getIcon()}
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">
          {event.source_id}
        </p>
        <div className="flex items-center mt-1 space-x-2 text-xs text-slate-400">
          <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
          <span>•</span>
          <span>Conf: {(event.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="flex flex-col items-end space-y-2">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeColor()}`}>
          {event.event_type.replace('_', ' ')}
        </span>
        {event.plate_number && (
          <span className="text-xs font-mono bg-slate-900 px-2 py-1 rounded text-yellow-400 border border-yellow-400/30">
            {event.plate_number}
          </span>
        )}
      </div>
    </div>
  );
};

export default EventCard;
