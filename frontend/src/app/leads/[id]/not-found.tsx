import Link from "next/link";

import { ButtonLink } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <div style={{ maxWidth: 420 }}>
      <Link href="/leads" style={{ fontSize: "0.88rem", color: "var(--ink-soft)" }}>
        ← All leads
      </Link>
      <h1 style={{ fontSize: "1.6rem", margin: "14px 0 8px" }}>Lead not found</h1>
      <p className="muted" style={{ marginBottom: 18 }}>
        This lead may have been removed, or the link is incorrect.
      </p>
      <ButtonLink href="/leads">Back to leads</ButtonLink>
    </div>
  );
}
