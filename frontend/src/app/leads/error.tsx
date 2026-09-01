"use client";

import { useEffect } from "react";

import { Alert } from "@/components/ui";
import { Button } from "@/components/ui/Button";

export default function LeadsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div style={{ maxWidth: 460 }}>
      <h1 style={{ fontSize: "1.6rem", marginBottom: 12 }}>Something went wrong</h1>
      <Alert kind="error">
        We couldn&apos;t load this page. This is usually temporary.
      </Alert>
      <div style={{ marginTop: 16 }}>
        <Button onClick={reset}>Try again</Button>
      </div>
    </div>
  );
}
