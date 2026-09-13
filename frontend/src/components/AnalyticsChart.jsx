import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AnalyticsChart = ({ stats }) => {
  // Convert stats object to array for Recharts
  const data = [
    { name: 'Persons', count: stats.total_persons, fill: '#818cf8' },
    { name: 'Vehicles', count: stats.total_vehicles, fill: '#22d3ee' },
    { name: 'Incidents', count: stats.total_incidents, fill: '#ef4444' },
  ];

  return (
    <div className="bg-surface rounded-xl border border-slate-700 shadow-lg p-6 h-[400px]">
      <h2 className="text-lg font-semibold text-white mb-4">Detection Distribution</h2>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip 
            cursor={{fill: '#334155'}}
            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AnalyticsChart;
