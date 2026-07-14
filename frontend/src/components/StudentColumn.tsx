// src/components/StudentColumn.tsx
import React from 'react';
import { Student } from '../types/report';
import { formatPct } from '../utils/formatters';

interface Props {
  student: Student;
}

export default function StudentColumn({ student }: Props) {
  const substantive = student.tier_breakdown?.substantive || 0;
  const moderate = student.tier_breakdown?.moderate || 0;
  const low_effort = student.tier_breakdown?.low_effort || 0;
  
  const totalWords = substantive + moderate + low_effort;
  const ownershipPct = (student.scores?.ownership || 0) * 100;
  const hasFlags = student.flags && student.flags.length > 0;

  const subPct = totalWords ? (substantive / totalWords) * 100 : 0;
  const modPct = totalWords ? (moderate / totalWords) * 100 : 0;
  const lowPct = totalWords ? (low_effort / totalWords) * 100 : 0;

  return (
    <div className={`bg-slate-50 p-6 rounded-2xl shadow-md border hover:shadow-lg transition-all duration-300 flex flex-col h-full ${hasFlags ? 'border-rose-300' : 'border-slate-200'}`}>
      
      {/* Name & Email */}
      <div className="mb-6 relative group">
        <h3 className="text-xl font-bold text-slate-900 flex items-center justify-between cursor-default">
          {student.name?.split(' ')[0] || "Unknown"}
          {hasFlags && (
            <span className="text-[10px] bg-rose-500 text-white px-2 py-0.5 rounded-full uppercase tracking-widest cursor-help">
              Flagged
            </span>
          )}
        </h3>
        <p className="text-sm text-slate-500 truncate">{student.email}</p>

        {hasFlags && (
          <div className="absolute top-full right-0 mt-2 w-48 opacity-0 group-hover:opacity-100 transition-opacity bg-rose-900 text-rose-50 text-[10px] px-3 py-2 rounded pointer-events-none z-20 shadow-xl">
            <strong>{student.flags[0].type}:</strong> {student.flags[0].evidence}
          </div>
        )}
      </div>

      {/* Contribution Share & Pie Chart */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <p className="text-xs font-semibold text-slate-700 mb-1">Contribution Share</p>
          <p className="text-3xl font-extrabold text-slate-800">{ownershipPct.toFixed(2)}%</p>
        </div>
        <div className="relative group cursor-pointer hover:scale-105 transition-transform duration-300">
          <div 
            className="w-16 h-16 rounded-full shadow-inner border border-slate-200 shrink-0"
            style={{ background: `conic-gradient(#10b981 ${ownershipPct}%, #cbd5e1 0)` }}
          />
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white text-xs px-2 py-1 rounded pointer-events-none z-10 shadow-md">
            {totalWords} total words
          </div>
        </div>
      </div>

      {/* Work Quality Stacked Bar */}
      <div className="mb-6">
        <p className="text-sm font-semibold text-slate-700 mb-2">Work Quality</p>
        <div className="w-full h-4 bg-slate-200 rounded-full overflow-visible flex shadow-inner">
          <div style={{ width: `${subPct}%` }} className="bg-emerald-500 h-full hover:opacity-80 transition-opacity" title={`Substantive: ${substantive}`} />
          <div style={{ width: `${modPct}%` }} className="bg-amber-400 h-full hover:opacity-80 transition-opacity" title={`Moderate: ${moderate}`} />
          <div style={{ width: `${lowPct}%` }} className="bg-rose-400 h-full hover:opacity-80 transition-opacity" title={`Low-effort: ${low_effort}`} />
        </div>
      </div>

      {/* Evidence List */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
        {student.evidence?.map((ev, idx) => {
          const isSub = ev.tier === 'substantive';
          const isMod = ev.tier === 'moderate';
          const badgeColor = isSub ? 'bg-emerald-500' : isMod ? 'bg-amber-400' : 'bg-rose-500';
          const cardBg = isSub ? 'bg-emerald-50/50' : isMod ? 'bg-amber-50/50' : 'bg-rose-50/50';

          return (
            <div key={idx} className={`${cardBg} p-3 rounded-lg border border-slate-200 text-xs shadow-sm`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`${badgeColor} text-white px-2 py-0.5 rounded font-bold text-[10px] uppercase tracking-wide`}>
                  {ev.tier}
                </span>
                <span className="text-slate-500 font-medium">Score: {formatPct(ev.confidence)}</span>
              </div>
              <p className="text-slate-700 italic line-clamp-3">"{ev.snippet}"</p>
            </div>
          );
        })}
        {(!student.evidence || student.evidence.length === 0) && (
           <p className="text-slate-400 text-xs italic">No evidence snippets available.</p>
        )}
      </div>

    </div>
  );
}