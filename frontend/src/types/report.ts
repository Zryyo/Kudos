// src/types/report.ts

export interface Evidence {
  snippet: string;
  timestamp: string;
  word_count: number;
  survived: number;
  tier: string;
  confidence: number;
}

export interface Flag {
  type: string;
  evidence: string;
}

export interface Student {
  student_id: string;
  name: string;
  email: string;
  scores: {
    ownership: number;
    substance: number;
    consistency: number;
    total: number;
  };
  tier_breakdown: {
    substantive: number;
    moderate: number;
    low_effort: number;
  };
  confidence: number;
  flags: Flag[];
  evidence: Evidence[];
}

export interface Report {
  document: {
    id: string;
    name: string;
    url: string;
  };
  run: {
    project_start: string;
    project_end: string;
    generated_at: string;
  };
  students: Student[];
  group_summary: {
    contribution_equality: number;
    median_total: number;
    needs_review_count: number;
  };
}