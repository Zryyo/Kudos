import React, { useState, useEffect } from 'react';
import { Report } from './types/report';
import DashboardView from './components/DashboardView';
import DetailView from './components/DetailView';

export default function App() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch initial list of reports on load
  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    fetch(`${baseUrl}/api/reports`)
      .then((res) => res.json())
      .then((data) => {
        setReports(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
      });
  }, []);

  // When the form successfully generates a new report
  const handleNewReport = (newReport: Report) => {
    setReports((prev) => [newReport, ...prev]); // Add to the top of the list
    setSelectedDocId(newReport.document.id);    // Open the new report immediately
  };

  if (loading) {
    return <div className="min-h-screen bg-[#dce3ec] flex items-center justify-center font-bold text-slate-500 animate-pulse">Loading documents...</div>;
  }

  // Show Dashboard if no specific document is selected
  if (!selectedDocId) {
    return (
      <DashboardView 
        reports={reports} 
        onSelectReport={setSelectedDocId} 
        onNewReport={handleNewReport} // <-- Pass down the function
      />
    );
  }

  // Show Detail View
  const selectedReport = reports.find(r => r.document?.id === selectedDocId);
  if (!selectedReport) return null;

  return (
    <DetailView 
      report={selectedReport} 
      onBack={() => setSelectedDocId(null)} 
    />
  );
}