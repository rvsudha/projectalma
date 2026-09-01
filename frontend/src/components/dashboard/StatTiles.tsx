import { clsx } from "clsx";

import styles from "./dashboard.module.css";
import type { LeadStats } from "@/lib/types";

export function StatTiles({ stats }: { stats: LeadStats }) {
  const tiles = [
    { label: "Total leads", value: stats.total, cls: undefined },
    { label: "Pending", value: stats.pending, cls: styles.tilePending },
    { label: "Reached out", value: stats.reached_out, cls: styles.tileReached },
  ];
  return (
    <div className={styles.stats}>
      {tiles.map((t) => (
        <div key={t.label} className={clsx(styles.tile, t.cls)}>
          <div className={styles.tileLabel}>{t.label}</div>
          <div className={styles.tileValue}>{t.value}</div>
        </div>
      ))}
    </div>
  );
}
