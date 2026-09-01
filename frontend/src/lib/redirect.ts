import type { Role } from "./types";

const HOME: Record<Role, string> = { attorney: "/leads", applicant: "/my" };
const SAFE_INTERNAL = /^\/(?!\/)/;

/** Where to send a user after auth, honouring `next` only within their own area. */
export function postAuthDestination(role: Role, next: string | null): string {
  const home = HOME[role];
  if (next && SAFE_INTERNAL.test(next) && next.startsWith(home)) return next;
  return home;
}
