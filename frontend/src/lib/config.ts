export const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v1";

export const SESSION_COOKIE_NAME =
  process.env.SESSION_COOKIE_NAME ?? "projectalma_session";

export const COOKIE_SECURE = process.env.COOKIE_SECURE === "1";
