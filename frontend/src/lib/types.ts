export type LeadState = "PENDING" | "REACHED_OUT";
export type Role = "applicant" | "attorney";

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  state: LeadState;
  milestone: string;
  resume_filename: string;
  resume_content_type: string;
  resume_size_bytes: number;
  reached_out_at: string | null;
  reached_out_by_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadEvent {
  id: string;
  type: "CREATED" | "STATE_CHANGED" | "EMAIL_SENT";
  message: string;
  actor_id: string | null;
  created_at: string;
}

export interface LeadDetail extends Lead {
  events: LeadEvent[];
}

export interface LeadStats {
  total: number;
  pending: number;
  reached_out: number;
}

export interface ActivityItem {
  id: string;
  lead_id: string;
  lead_name: string;
  type: LeadEvent["type"];
  message: string;
  actor_name: string | null;
  created_at: string;
}

export interface PageMeta {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: unknown[];
    request_id: string | null;
  };
}
