import React from 'react';

const KPICard = ({ title, value, icon: Icon, colorClass }) => {
  return (
    <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg flex items-center justify-between transition-transform hover:-translate-y-1">
      <div>
        <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-white">{value}</h3>
      </div>
      <div className={`p-4 rounded-full ${colorClass} bg-opacity-20`}>
        <Icon className={`w-8 h-8 ${colorClass.replace('bg-', 'text-')}`} />
      </div>
    </div>
  );
};

export default KPICard;
