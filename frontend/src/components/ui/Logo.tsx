import { clsx } from "clsx";

import styles from "./Logo.module.css";

/** Plain text wordmark — no logo mark. */
export function Logo({
  className,
  onDark = false,
}: {
  className?: string;
  onDark?: boolean;
}) {
  return (
    <span className={clsx(styles.word, onDark && styles.onDark, className)}>
      ProjectAlma
    </span>
  );
}
