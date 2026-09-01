import type { ReactNode } from "react";

import { Card } from "@/components/ui";
import { Logo } from "@/components/ui/Logo";

import styles from "./auth.module.css";

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <main className={styles.wrap}>
      <div className={styles.panel}>
        <div className={styles.brand}>
          <Logo />
        </div>
        <Card>
          <h1>{title}</h1>
          <p className={styles.sub}>{subtitle}</p>
          {children}
        </Card>
      </div>
    </main>
  );
}
