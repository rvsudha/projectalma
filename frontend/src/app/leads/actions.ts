"use server";

import { revalidatePath } from "next/cache";

import { ApiError, updateLeadState } from "@/lib/api";
import type { LeadState } from "@/lib/types";

export interface ActionResult {
  ok: boolean;
  error?: string;
}

export async function transitionLead(
  leadId: string,
  toState: LeadState,
): Promise<ActionResult> {
  try {
    await updateLeadState(leadId, toState);
  } catch (err) {
    if (err instanceof ApiError) return { ok: false, error: err.message };
    return { ok: false, error: "Could not update the lead. Please try again." };
  }
  revalidatePath("/leads");
  revalidatePath(`/leads/${leadId}`);
  return { ok: true };
}
