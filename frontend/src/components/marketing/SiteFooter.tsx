import styles from "./marketing.module.css";

export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.footerInner}`}>
        <span>© {new Date().getFullYear()} ProjectAlma</span>
        <span>Built with FastAPI &amp; Next.js</span>
      </div>
    </footer>
  );
}
