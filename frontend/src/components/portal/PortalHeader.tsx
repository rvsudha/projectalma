import Link from "next/link";

import { LogoutButton } from "@/components/dashboard/LogoutButton";
import { Logo } from "@/components/ui/Logo";
import type { CurrentUser } from "@/lib/types";

import styles from "./portal.module.css";

export function PortalHeader({ user }: { user: CurrentUser }) {
  return (
    <header className={styles.topbar}>
      <div className={`container ${styles.topbarInner}`}>
        <Link href="/my" aria-label="Your cases">
          <Logo />
        </Link>
        <div className={styles.user}>
          <span>{user.full_name}</span>
          <LogoutButton />
        </div>
      </div>
    </header>
  );
}
