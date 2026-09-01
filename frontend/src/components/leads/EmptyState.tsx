import styles from "@/components/dashboard/dashboard.module.css";

export function ActivityHint({ filtered }: { filtered: boolean }) {
  return (
    <div className={styles.tableWrap}>
      <div className={styles.empty}>
        <h3>{filtered ? "No leads match your filters" : "No leads yet"}</h3>
        <p>
          {filtered
            ? "Try clearing the search or switching tabs."
            : "New submissions from the public form will appear here."}
        </p>
      </div>
    </div>
  );
}
