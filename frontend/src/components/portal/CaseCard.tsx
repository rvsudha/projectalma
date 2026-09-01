import { ActivityTimeline } from "@/components/leads/ActivityTimeline";
import { StateBadge } from "@/components/ui";
import { Check, FileText } from "@/components/ui/Icons";
import { formatBytes, formatDateTime, fullName } from "@/lib/format";
import type { LeadDetail } from "@/lib/types";

import styles from "./portal.module.css";

export function CaseCard({ lead }: { lead: LeadDetail }) {
  return (
    <article className={styles.card}>
      <div className={styles.cardHead}>
        <h2>{fullName(lead.first_name, lead.last_name)}</h2>
        <StateBadge state={lead.state} />
      </div>
      <p className={styles.submitted}>Submitted {formatDateTime(lead.created_at)}</p>

      <div className={styles.milestone}>
        <Check width={16} height={16} />
        <span>{lead.milestone}</span>
      </div>

      <dl className={styles.meta}>
        <dt>Email</dt>
        <dd>{lead.email}</dd>
        <dt>Resume</dt>
        <dd style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <FileText width={14} height={14} />
          <a href={`/api/my/leads/${lead.id}/resume`} target="_blank" rel="noreferrer">
            {lead.resume_filename}
          </a>{" "}
          <span style={{ color: "var(--ink-faint)" }}>
            ({formatBytes(lead.resume_size_bytes)})
          </span>
        </dd>
        {lead.reached_out_at && (
          <>
            <dt>Contacted</dt>
            <dd>{formatDateTime(lead.reached_out_at)}</dd>
          </>
        )}
      </dl>

      <p className={styles.timelineLabel}>Progress</p>
      <ActivityTimeline events={lead.events} />
    </article>
  );
}
