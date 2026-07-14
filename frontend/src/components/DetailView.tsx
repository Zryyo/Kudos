// src/components/DetailView.tsx
import React from 'react';
import { Report } from '../types/report';
import { formatDate } from '../utils/formatters';
import StudentColumn from './StudentColumn';

interface Props {
  report: Report;
  onBack: () => void;
}

export default function DetailView({ report, onBack }: Props) {
  const totalGroupWords = report.students.reduce((sum, s) => sum + (s.tier_breakdown?.substantive || 0) + (s.tier_breakdown?.moderate || 0) + (s.tier_breakdown?.low_effort || 0), 0);
  const totalAllocated = report.students.reduce((sum, s) => sum + (s.scores?.ownership || 0) * 100, 0);

  return (
    <div className="min-h-screen bg-[#dce3ec] text-slate-800 font-sans p-4 md:p-8 flex flex-col">
      
      <div className="mb-4">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-blue-600 font-semibold transition-colors bg-white/60 hover:bg-white px-4 py-2 rounded-lg w-max shadow-sm border border-slate-200"
        >
          ← Back to Dashboard
        </button>
      </div>

      <header className="bg-gradient-to-r from-blue-50 via-purple-50 to-blue-50 py-8 shadow-sm rounded-xl text-center mb-8 border border-slate-100">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-700 tracking-wide uppercase">
          Contribution Analysis
        </h1>
        <h2 className="text-xl text-blue-500 font-medium mt-2">
          {report.document?.name || "Untitled Document"}
        </h2>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        
        {/* Left Column */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className="bg-slate-50 p-6 rounded-2xl shadow-md border border-slate-200">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Project Overview</h3>
            <div className="space-y-3 text-sm text-slate-700">
              <p><span className="font-semibold text-slate-900">Dates:</span> {formatDate(report.run?.project_start)} - {formatDate(report.run?.project_end)}</p>
              <p><span className="font-semibold text-slate-900">Generated:</span> {formatDate(report.run?.generated_at)}</p>
            </div>
          </div>

          <div className="bg-slate-50 p-6 rounded-2xl shadow-md border border-slate-200 flex-1">
            <h3 className="text-xl font-semibold text-slate-800 mb-4 cursor-default">Group Summary</h3>
            <div className="mb-6">
              <p className="text-sm font-semibold text-slate-700">Contribution Equality</p>
              <span className="text-4xl font-extrabold text-emerald-500 leading-none">
                {report.group_summary?.contribution_equality?.toFixed(4) || "0.0000"}
              </span>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">Needs Review Count</p>
              <p className={`text-4xl font-extrabold mt-1 ${report.group_summary?.needs_review_count > 0 ? 'text-rose-500' : 'text-slate-700'}`}>
                {report.group_summary?.needs_review_count || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Right Columns: Students */}
        <div className="lg:col-span-9 grid grid-cols-1 md:grid-cols-3 gap-6">
          {report.students?.map((student) => (
            <StudentColumn key={student.student_id} student={student} />
          ))}
        </div>
      </div>

      <div className="mt-8 text-right pr-4 pb-4">
        <p className="text-lg font-bold text-slate-800">
          Total Group Words: <span className="text-emerald-600">{totalGroupWords}</span> / <span className="text-emerald-400">100%</span>
        </p>
        <p className="text-lg font-bold text-slate-800">
          Total Ownership Allocated: <span className="text-amber-500">{totalAllocated.toFixed(0)}%</span> / <span className="text-emerald-400">100%</span>
        </p>
      </div>

    </div>
  );
}