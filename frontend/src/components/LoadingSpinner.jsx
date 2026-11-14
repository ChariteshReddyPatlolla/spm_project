import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ label = 'Processing...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-slate-400 gap-3">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      <span className="text-sm font-medium animate-pulse">{label}</span>
    </div>
  );
};

