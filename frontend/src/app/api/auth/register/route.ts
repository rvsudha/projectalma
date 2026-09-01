import { NextRequest, NextResponse } from "next/server";

import { forwardAuth } from "@/lib/auth-proxy";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return NextResponse.json(
      { error: { code: "bad_request", message: "Invalid request body" } },
      { status: 400 },
    );
  }

  const role = payload.role === "attorney" ? "attorney" : "applicant";
  const required = ["full_name", "email", "password"] as const;
  const body: Record<string, unknown> = { role };
  for (const key of required) {
    if (typeof payload[key] !== "string" || !(payload[key] as string).trim()) {
      return NextResponse.json(
        { error: { code: "validation_error", message: "All fields are required" } },
        { status: 422 },
      );
    }
    body[key] = payload[key];
  }
  if (role === "attorney") body.invite_code = payload.invite_code ?? "";

  return forwardAuth("/auth/register", body, "Sign-up is unavailable right now.");
}
