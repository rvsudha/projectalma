"use client";

import { useState } from "react";

import { Alert } from "@/components/ui";

import type { LeadState } from "@/lib/types";

import { ReachOutButton } from "./ReachOutButton";

export function DetailReachOut({
  leadId,
  leadName,
  state,
}: {
  leadId: string;
  leadName: string;
  state: LeadState;
}) {
  const [error, setError] = useState<string | null>(null);
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {error && <Alert kind="error">{error}</Alert>}
      <ReachOutButton
        leadId={leadId}
        leadName={leadName}
        toState={state === "PENDING" ? "REACHED_OUT" : "PENDING"}
        size="md"
        onError={setError}
      />
    </div>
  );
}
