import { clsx } from "clsx";
import type { CSSProperties, ReactNode } from "react";

import { AlertCircle, Check } from "./Icons";
import styles from "./primitives.module.css";

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={clsx(styles.card, className)}>{children}</div>;
}

export function StateBadge({ state }: { state: "PENDING" | "REACHED_OUT" }) {
  const isReached = state === "REACHED_OUT";
  return (
    <span
      className={clsx(
        styles.badge,
        isReached ? styles.badgeReached : styles.badgePending,
      )}
    >
      {isReached ? "Reached out" : "Pending"}
    </span>
  );
}

type AlertKind = "error" | "success" | "info";

export function Alert({
  kind = "info",
  children,
}: {
  kind?: AlertKind;
  children: ReactNode;
}) {
  const cls = {
    error: styles.alertError,
    success: styles.alertSuccess,
    info: styles.alertInfo,
  }[kind];
  return (
    <div className={clsx(styles.alert, cls)} role={kind === "error" ? "alert" : "status"}>
      {kind === "success" ? (
        <Check width={16} height={16} />
      ) : (
        <AlertCircle width={16} height={16} />
      )}
      <div>{children}</div>
    </div>
  );
}

export function Spinner({ size = 20, label }: { size?: number; label?: string }) {
  return (
    <span
      className={styles.spinner}
      style={{ "--size": `${size}px` } as CSSProperties}
      role="status"
      aria-label={label ?? "Loading"}
    />
  );
}

export function CenteredSpinner({ label }: { label?: string }) {
  return (
    <div className={styles.center}>
      <Spinner size={28} label={label} />
    </div>
  );
}
