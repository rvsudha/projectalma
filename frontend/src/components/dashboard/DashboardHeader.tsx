import Link from "next/link";

import { Logo } from "@/components/ui/Logo";
import { initials } from "@/lib/format";
import type { CurrentUser } from "@/lib/types";

import { LogoutButton } from "./LogoutButton";
import styles from "./dashboard.module.css";

export function DashboardHeader({ user }: { user: CurrentUser }) {
  const [first = "", last = ""] = user.full_name.split(" ");
  return (
    <header className={styles.topbar}>
      <div className={`container ${styles.topbarInner}`}>
        <Link href="/leads" aria-label="Leads dashboard">
          <Logo />
        </Link>
        <div className={styles.user}>
          <span className={styles.avatar} aria-hidden>
            {initials(first, last) || "A"}
          </span>
          <span>{user.full_name}</span>
          <LogoutButton />
        </div>
      </div>
    </header>
  );
}
