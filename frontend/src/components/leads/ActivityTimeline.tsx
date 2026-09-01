import { clsx } from "clsx";

import { formatDateTime, relativeTime } from "@/lib/format";
import type { LeadEvent } from "@/lib/types";

import styles from "./ActivityTimeline.module.css";

const LABEL: Record<LeadEvent["type"], string> = {
  CREATED: "Lead submitted",
  STATE_CHANGED: "State changed",
  EMAIL_SENT: "Email sent",
};

export function ActivityTimeline({ events }: { events: LeadEvent[] }) {
  if (events.length === 0) {
    return <p className="muted">No activity yet.</p>;
  }
  // newest first
  const ordered = [...events].sort((a, b) => b.created_at.localeCompare(a.created_at));

  return (
    <ol className={styles.timeline}>
      {ordered.map((event, i) => (
        <li key={event.id} className={styles.item}>
          <span className={clsx(styles.dot, i !== 0 && styles.dotMuted)} aria-hidden />
          <div className={styles.what}>
            {event.type === "STATE_CHANGED" ? event.message : LABEL[event.type]}
          </div>
          <div className={styles.when}>
            {formatDateTime(event.created_at)} · {relativeTime(event.created_at)}
          </div>
        </li>
      ))}
    </ol>
  );
}
