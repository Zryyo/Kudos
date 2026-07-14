// src/components/NewAnalysisForm.tsx
import React, { useState } from 'react';
import { Report } from '../types/report';

interface Props {
  onReportGenerated: (report: Report) => void;
  onCancel: () => void;
}

export default function NewAnalysisForm({ onReportGenerated, onCancel }: Props) {
  const [source, setSource] = useState<'mock' | 'live'>('mock');
  const [documentId, setDocumentId] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsAnalyzing(true);

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          document_id: source === 'live' ? documentId : null,
          roster: 'roster.json' // Hardcoded for now, could become an upload field later
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to analyze document');
      }

      const newReport = await response.json();
      onReportGenerated(newReport); // Pass the new report back up to App.tsx
      
    } catch (err: any) {
      setError(err.message);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-blue-100 mb-8 animate-in fade-in slide-in-from-top-4 duration-300">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Run New Analysis</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Source Toggle */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Data Source</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                checked={source === 'mock'} 
                onChange={() => setSource('mock')}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-slate-700">Mock Data</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                checked={source === 'live'} 
                onChange={() => setSource('live')}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-slate-700">Live Google Doc</span>
            </label>
          </div>
        </div>

        {/* Document ID Input (Conditional) */}
        {source === 'live' && (
          <div className="animate-in fade-in duration-300">
            <label className="block text-sm font-semibold text-slate-700 mb-1">Google Doc ID</label>
            <input
              type="text"
              required
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value)}
              placeholder="e.g. 1NovaBrewMarketingPlan..."
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
            <p className="text-xs text-slate-500 mt-1">Make sure the Google Doc is accessible by your service account.</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-sm font-medium">
            Error: {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={isAnalyzing}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Processing Document...
              </>
            ) : 'Run Pipeline'}
          </button>
          
          <button
            type="button"
            onClick={onCancel}
            disabled={isAnalyzing}
            className="px-6 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}