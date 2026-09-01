"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { transitionLead } from "@/app/leads/actions";
import { Button } from "@/components/ui/Button";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { Check, RotateCcw } from "@/components/ui/Icons";
import type { LeadState } from "@/lib/types";

interface Props {
  leadId: string;
  leadName: string;
  /** The state to move the lead to. Defaults to REACHED_OUT (the common case). */
  toState?: LeadState;
  size?: "sm" | "md";
  onError?: (message: string) => void;
}

const COPY = {
  REACHED_OUT: {
    trigger: "Mark reached out",
    title: "Mark this lead as reached out?",
    body: (name: string) =>
      `Confirm that you've contacted ${name}. You can reopen the lead later if this was a mistake.`,
    confirm: "Mark reached out",
  },
  PENDING: {
    trigger: "Reopen lead",
    title: "Reopen this lead?",
    body: (name: string) =>
      `This moves ${name} back to pending and clears the reached-out record. The change is logged in the activity trail.`,
    confirm: "Reopen lead",
  },
} as const;

export function ReachOutButton({
  leadId,
  leadName,
  toState = "REACHED_OUT",
  size = "sm",
  onError,
}: Props) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [pending, start] = useTransition();
  const copy = COPY[toState];

  function confirm() {
    start(async () => {
      const result = await transitionLead(leadId, toState);
      setOpen(false);
      if (!result.ok) {
        onError?.(result.error ?? "Update failed");
        return;
      }
      router.refresh();
    });
  }

  return (
    <>
      <Button variant="secondary" size={size} onClick={() => setOpen(true)}>
        {toState === "REACHED_OUT" ? (
          <Check width={14} height={14} />
        ) : (
          <RotateCcw width={14} height={14} />
        )}
        {copy.trigger}
      </Button>
      <ConfirmDialog
        open={open}
        title={copy.title}
        description={copy.body(leadName)}
        confirmLabel={copy.confirm}
        loading={pending}
        onConfirm={confirm}
        onCancel={() => setOpen(false)}
      />
    </>
  );
}
