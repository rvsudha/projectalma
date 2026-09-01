import { NextRequest, NextResponse } from "next/server";

import { API_BASE_URL, SESSION_COOKIE_NAME } from "@/lib/config";

export const runtime = "nodejs";

/** Authenticated resume download proxy — attaches the attorney's JWT server-side. */
export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const token = req.cookies.get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json(
      { error: { code: "unauthorized", message: "Not authenticated" } },
      { status: 401 },
    );
  }

  const upstream = await fetch(`${API_BASE_URL}/leads/${params.id}/resume`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!upstream.ok || !upstream.body) {
    return NextResponse.json(
      { error: { code: "not_available", message: "Could not fetch the resume" } },
      { status: upstream.status || 502 },
    );
  }

  return new NextResponse(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": upstream.headers.get("Content-Type") ?? "application/octet-stream",
      "Content-Disposition": upstream.headers.get("Content-Disposition") ?? "attachment",
      "Cache-Control": "private, no-store",
    },
  });
}
