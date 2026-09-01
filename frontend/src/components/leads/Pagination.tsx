import Link from "next/link";

import buttons from "@/components/ui/Button.module.css";
import styles from "@/components/dashboard/dashboard.module.css";
import type { PageMeta } from "@/lib/types";

function href(base: URLSearchParams, page: number): string {
  const next = new URLSearchParams(base);
  if (page <= 1) next.delete("page");
  else next.set("page", String(page));
  const qs = next.toString();
  return `/leads${qs ? `?${qs}` : ""}`;
}

const pill = `${buttons.btn} ${buttons.secondary} ${buttons.sm}`;

export function Pagination({
  meta,
  searchParams,
}: {
  meta: PageMeta;
  searchParams: Record<string, string>;
}) {
  const pageSize = meta.limit;
  const currentPage = Math.floor(meta.offset / pageSize) + 1;
  const totalPages = Math.max(1, Math.ceil(meta.total / pageSize));
  if (totalPages <= 1) return null;

  const base = new URLSearchParams();
  for (const [k, v] of Object.entries(searchParams)) {
    if (v && k !== "page") base.set(k, v);
  }

  const from = meta.offset + 1;
  const to = meta.offset + Math.min(pageSize, meta.total - meta.offset);
  const hasPrev = currentPage > 1;
  const hasNext = currentPage < totalPages;

  return (
    <nav className={styles.pagination} aria-label="Pagination">
      <span>
        {from}–{to} of {meta.total}
      </span>
      <div className={styles.pageBtns}>
        {hasPrev ? (
          <Link href={href(base, currentPage - 1)} className={pill}>
            Previous
          </Link>
        ) : (
          <span className={pill} aria-disabled>
            Previous
          </span>
        )}
        {hasNext ? (
          <Link href={href(base, currentPage + 1)} className={pill}>
            Next
          </Link>
        ) : (
          <span className={pill} aria-disabled>
            Next
          </span>
        )}
      </div>
    </nav>
  );
}
