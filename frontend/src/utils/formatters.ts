// src/utils/formatters.ts

export const formatPct = (val: number) => `${(val * 100).toFixed(2)}%`;

export const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
};