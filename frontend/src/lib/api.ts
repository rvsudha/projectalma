import "server-only";

import { cache } from "react";

import { API_BASE_URL } from "./config";
import { getSessionToken } from "./session";
import type {
  ActivityItem,
  CurrentUser,
  Lead,
  LeadDetail,
  LeadEvent,
  LeadState,
  LeadStats,
  Page,
  Role,
} from "./types";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code = "error",
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message = "Unauthorized") {
    super(401, message, "unauthorized");
    this.name = "UnauthorizedError";
  }
}

interface RequestOpts extends RequestInit {
  auth?: boolean;
}

async function request<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const { auth = true, headers, ...rest } = opts;
  const finalHeaders = new Headers(headers);

  if (auth) {
    const token = getSessionToken();
    if (!token) throw new UnauthorizedError("No session");
    finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      headers: finalHeaders,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(503, "The service is unavailable.", "upstream_unreachable");
  }

  if (res.status === 401) throw new UnauthorizedError();

  if (!res.ok) {
    let message = res.statusText || "Request failed";
    let code = "error";
    try {
      const body = await res.json();
      message = body?.error?.message ?? message;
      code = body?.error?.code ?? code;
    } catch {
      /* keep statusText */
    }
    throw new ApiError(res.status, message, code);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// --- Auth ---

export interface TokenResponse {
  access_token: string;
  expires_in: number;
  role: Role;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return request("/auth/login", {
    method: "POST",
    auth: false,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function register(input: {
  full_name: string;
  email: string;
  password: string;
  role: Role;
  invite_code?: string;
}): Promise<TokenResponse> {
  return request("/auth/register", {
    method: "POST",
    auth: false,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export const getCurrentUser = cache(() => request<CurrentUser>("/auth/me"));

// --- Leads ---

export const listLeads = cache(async function listLeads(params: {
  state?: LeadState;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<Page<Lead>> {
  const qs = new URLSearchParams();
  if (params.state) qs.set("state", params.state);
  if (params.search) qs.set("search", params.search);
  if (params.limit != null) qs.set("limit", String(params.limit));
  if (params.offset != null) qs.set("offset", String(params.offset));
  const suffix = qs.toString() ? `?${qs}` : "";
  return request<Page<Lead>>(`/leads${suffix}`);
});

export const getLead = cache((id: string) => request<LeadDetail>(`/leads/${id}`));

export const getLeadEvents = cache((id: string) =>
  request<LeadEvent[]>(`/leads/${id}/events`),
);

export async function updateLeadState(id: string, state: LeadState): Promise<Lead> {
  return request<Lead>(`/leads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
}

export const getLeadStats = cache(() => request<LeadStats>("/leads/stats"));

export const getActivity = cache((limit = 12) =>
  request<ActivityItem[]>(`/leads/activity?limit=${limit}`),
);

// --- Applicant portal ---

export const getMyLeads = cache(() => request<LeadDetail[]>("/my/leads"));
