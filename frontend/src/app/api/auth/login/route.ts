import { NextRequest, NextResponse } from "next/server";

import { forwardAuth } from "@/lib/auth-proxy";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  let payload: { email?: unknown; password?: unknown };
  try {
    payload = await req.json();
  } catch {
    return NextResponse.json(
      { error: { code: "bad_request", message: "Invalid request body" } },
      { status: 400 },
    );
  }

  const email = typeof payload.email === "string" ? payload.email : "";
  const password = typeof payload.password === "string" ? payload.password : "";
  if (!email || !password) {
    return NextResponse.json(
      { error: { code: "validation_error", message: "Email and password are required" } },
      { status: 422 },
    );
  }

  return forwardAuth(
    "/auth/login",
    { email, password },
    "Sign-in is unavailable right now.",
  );
}
