import Link from "next/link";

import { ButtonLink } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";

import styles from "./marketing.module.css";

export function PublicHeader() {
  return (
    <header className={styles.header}>
      <div className={`container ${styles.headerInner}`}>
        <Link href="/" aria-label="Home">
          <Logo />
        </Link>
        <nav className={styles.nav} aria-label="Account">
          <Link href="/login" className={styles.navLink}>
            Log in
          </Link>
          <ButtonLink href="/signup" variant="secondary" size="sm">
            Sign up
          </ButtonLink>
        </nav>
      </div>
    </header>
  );
}
