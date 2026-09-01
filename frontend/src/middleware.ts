import { NextRequest, NextResponse } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/config";

/**
 * Coarse guard: bounce visitors with no session away from the signed-in areas
 * before the page renders. Role (attorney vs applicant) is enforced server-side
 * in the route layouts; the API enforces it on every request regardless.
 */
export function middleware(req: NextRequest) {
  const hasSession = Boolean(req.cookies.get(SESSION_COOKIE_NAME)?.value);
  const { pathname, search } = req.nextUrl;

  if (!hasSession) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("next", pathname + search);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/leads/:path*", "/my/:path*"],
};
