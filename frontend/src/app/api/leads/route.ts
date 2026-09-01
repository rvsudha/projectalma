import { NextRequest, NextResponse } from "next/server";

import { API_BASE_URL } from "@/lib/config";

export const runtime = "nodejs";

/**
 * Public proxy for lead submission. The browser only ever talks to this origin;
 * the FastAPI base URL and any future server-side concerns stay here.
 */
export async function POST(req: NextRequest) {
  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json(
      { error: { code: "bad_request", message: "Expected multipart form data" } },
      { status: 400 },
    );
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_BASE_URL}/leads`, {
      method: "POST",
      body: formData,
    });
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "upstream_unreachable",
          message: "The service is unavailable. Please try again shortly.",
        },
      },
      { status: 502 },
    );
  }

  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("Content-Type") ?? "application/json",
    },
  });
}
