// Letter types
export interface Letter {
  id: number;
  subject: string;
  content: string;
  sender: string;
  sender_email: string;
  received_at: string;
  request_category: string | null;
  processing_params: ProcessingParams | null;
  client_id: number | null;
  correspondence_thread_id: number | null;
  created_at: string;
  updated_at: string;
  drafts: Draft[];
  approvals: Approval[];
}

export interface LetterCreate {
  subject: string;
  content: string;
  sender: string;
  sender_email: string;
  client_id?: number | null;
  correspondence_thread_id?: number | null;
}

export interface LetterResponse extends Letter {}

// Processing Params
export interface ProcessingParams {
  letter_type?: string;
  formality_level?: string;
  response_style?: string;
  urgency_level?: string;
  sla_deadline?: string;
  operation_amount?: number;
  department?: string;
  risk_level?: string;
  geography?: string;
  client_type?: string;
  document_type?: string;
  change_type?: string;
}

// Draft types
export type DraftStatus = 'draft' | 'validated' | 'approved' | 'sent' | 'rejected';

export interface Draft {
  id: number;
  letter_id: number;
  content: string;
  style: string | null;
  validation_score: number | null;
  validation_result: ValidationResult | null;
  status: DraftStatus;
  created_at: string;
  updated_at: string;
}

// Validation types
export interface ValidationResult {
  score: number;
  auto_send_eligible: boolean;
  issues?: string[];
  recommendations?: string[];
}

// Approval types
export interface Approval {
  id: number;
  letter_id: number;
  draft_id: number | null;
  route: string[] | Record<string, any> | null;
  current_approver: string | null;
  approval_status: 'pending' | 'approved' | 'rejected' | 'auto_sent' | null;
  operation_amount: number | null;
  request_category: string | null;
  department: string | null;
  risk_level: string | null;
  geography: string | null;
  client_type: string | null;
  document_type: string | null;
  change_type: string | null;
  created_at: string;
  updated_at: string;
}

// Analytics types
export interface Metrics {
  average_processing_time_hours: number;
  letter_types_statistics: Record<string, number>;
  status_distribution: Record<string, number>;
  total_letters: number;
  total_drafts: number;
}

export interface SLAMonitoring {
  sla_compliance_rate_percent: number;
  sla_compliant_count: number;
  sla_violated_count: number;
  violated_letters: ViolatedLetter[];
  total_checked: number;
}

export interface ViolatedLetter {
  letter_id: number;
  subject: string;
  received_at: string | null;
  sla_deadline: string;
  sent_at: string | null;
  violation_hours: number;
}

