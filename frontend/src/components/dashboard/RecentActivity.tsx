import Link from "next/link";

import styles from "./dashboard.module.css";
import { relativeTime } from "@/lib/format";
import type { ActivityItem } from "@/lib/types";

function describe(item: ActivityItem): string {
  if (item.type === "STATE_CHANGED") {
    if (item.message.includes("(reopened)")) return "reopened the lead";
    const to = item.message.split("->").pop()?.trim().replace("_", " ").toLowerCase();
    return `marked ${to}`;
  }
  if (item.type === "CREATED") return "submitted a lead";
  return item.message;
}

export function RecentActivity({ items }: { items: ActivityItem[] }) {
  return (
    <section className={styles.activity} aria-label="Recent activity">
      <h2>Recent activity</h2>
      {items.length === 0 ? (
        <p className={styles.activityEmpty}>No activity yet.</p>
      ) : (
        <ul className={styles.activityList}>
          {items.map((item) => (
            <li key={item.id} className={styles.activityRow}>
              <span className={styles.activityDot} aria-hidden />
              <span>
                <Link href={`/leads/${item.lead_id}`}>{item.lead_name}</Link> —{" "}
                {describe(item)}
                {item.actor_name ? ` by ${item.actor_name}` : ""}
              </span>
              <span className={styles.activityWhen}>{relativeTime(item.created_at)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
