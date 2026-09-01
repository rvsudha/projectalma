import "server-only";

import { cookies } from "next/headers";

import { SESSION_COOKIE_NAME } from "./config";

/** Returns the attorney's JWT from the session cookie, or null. */
export function getSessionToken(): string | null {
  return cookies().get(SESSION_COOKIE_NAME)?.value ?? null;
}
