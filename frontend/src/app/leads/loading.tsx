import styles from "@/components/dashboard/dashboard.module.css";

export default function Loading() {
  return (
    <>
      <div className={styles.pageHead}>
        <h1>Leads</h1>
      </div>
      <div className={styles.toolbar}>
        <div className={styles.skelBar} style={{ width: 220, margin: 0, height: 34 }} />
      </div>
      <div className={styles.tableWrap}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className={styles.skelRow}>
            <div className={styles.skelBar} style={{ width: `${60 - i * 4}%` }} />
          </div>
        ))}
      </div>
    </>
  );
}
