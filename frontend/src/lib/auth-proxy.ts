import { NextResponse } from "next/server";

import { API_BASE_URL, COOKIE_SECURE, SESSION_COOKIE_NAME } from "./config";

/**
 * Forwards a credentials payload to a FastAPI auth endpoint and, on success,
 * sets the JWT as an httpOnly session cookie. Shared by /api/auth/login and
 * /api/auth/register so the cookie handling lives in one place.
 */
export async function forwardAuth(
  path: "/auth/login" | "/auth/register",
  body: Record<string, unknown>,
  fallbackError: string,
): Promise<NextResponse> {
  let upstream: Response;
  try {
    upstream = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json(
      { error: { code: "upstream_unreachable", message: fallbackError } },
      { status: 502 },
    );
  }

  if (!upstream.ok) {
    const payload = await upstream.json().catch(() => null);
    return NextResponse.json(
      { error: payload?.error ?? { code: "error", message: fallbackError } },
      { status: upstream.status },
    );
  }

  const { access_token, expires_in, role } = await upstream.json();
  const res = NextResponse.json({ ok: true, role });
  res.cookies.set(SESSION_COOKIE_NAME, access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: COOKIE_SECURE,
    path: "/",
    maxAge: typeof expires_in === "number" ? expires_in : 60 * 60 * 8,
  });
  return res;
}
