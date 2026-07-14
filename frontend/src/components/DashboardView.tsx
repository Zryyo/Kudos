import React, { useState } from 'react';
import { Report } from '../types/report';
import { formatDate } from '../utils/formatters';
import NewAnalysisForm from './NewAnalysisForm'; // <-- Import the form

interface Props {
  reports: Report[];
  onSelectReport: (id: string) => void;
  onNewReport: (report: Report) => void; // <-- Add this prop
}

export default function DashboardView({ reports, onSelectReport, onNewReport }: Props) {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="min-h-screen bg-[#dce3ec] text-slate-800 font-sans p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        
        {/* Header & New Analysis Button */}
        <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div className="flex items-center gap-4">
                <div className="w-15 h-15 bg-white rounded-xl shadow-sm border border-slate-200 flex items-center justify-center overflow-hidden shrink-0">
                    <img src="/kudos-logo.svg" alt="Kudos Logo" className="w-10 h-10" />
                </div>
                
                <div>
                    <h1 className="text-3xl md:text-4xl font-extrabold text-slate-700 tracking-wide uppercase mb-1">
                        Kudos Dashboard
                    </h1>
                    <p className="text-slate-500 font-medium">Select a group project document to view its contribution analysis.</p>
                </div>
            </div>
          {!showForm && (
            <button 
              onClick={() => setShowForm(true)}
              className="bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-2.5 px-6 rounded-lg shadow-sm hover:shadow-md transition-all active:scale-95 whitespace-nowrap"
            >
              + Run New Analysis
            </button>
          )}
        </header>

        {/* The Form */}
        {showForm && (
          <NewAnalysisForm 
            onCancel={() => setShowForm(false)} 
            onReportGenerated={(newReport) => {
              setShowForm(false);
              onNewReport(newReport); // Tell App.tsx we have a new report
            }} 
          />
        )}

        {/* Document Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report) => (
            <div 
              key={report.document?.id || Math.random().toString()} 
              onClick={() => onSelectReport(report.document?.id)}
              className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col h-full group"
            >
              <div className="flex-1">
                <h2 className="text-xl font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
                  {report.document?.name || "Untitled Document"}
                </h2>
                <p className="text-sm text-slate-500 mb-4">
                  {formatDate(report.run?.project_start)} - {formatDate(report.run?.project_end)}
                </p>
                
                <div className="space-y-2 mb-6 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Students:</span>
                    <span className="font-semibold text-slate-700">{report.students?.length || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Equality Score:</span>
                    <span className="font-semibold text-emerald-600">{(report.group_summary?.contribution_equality || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Needs Review:</span>
                    <span className={`font-semibold ${(report.group_summary?.needs_review_count || 0) > 0 ? 'text-rose-500' : 'text-slate-700'}`}>
                      {report.group_summary?.needs_review_count || 0}
                    </span>
                  </div>
                </div>
              </div>
              
              <button className="w-full py-2.5 bg-slate-100 group-hover:bg-blue-50 text-slate-700 group-hover:text-blue-600 font-semibold rounded-lg transition-colors">
                View Analysis →
              </button>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}