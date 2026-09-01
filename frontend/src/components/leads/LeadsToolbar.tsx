"use client";

import { clsx } from "clsx";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Search } from "@/components/ui/Icons";
import styles from "@/components/dashboard/dashboard.module.css";

const TABS = [
  { label: "All", value: "" },
  { label: "Pending", value: "PENDING" },
  { label: "Reached out", value: "REACHED_OUT" },
];

export function LeadsToolbar() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const activeState = params.get("state") ?? "";
  const [term, setTerm] = useState(params.get("search") ?? "");
  const firstRender = useRef(true);

  // Debounce search -> URL
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    const id = setTimeout(() => {
      const next = new URLSearchParams(params.toString());
      if (term) next.set("search", term);
      else next.delete("search");
      next.delete("page");
      router.replace(`${pathname}?${next.toString()}`);
    }, 300);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [term]);

  function setState(value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set("state", value);
    else next.delete("state");
    next.delete("page");
    router.replace(`${pathname}?${next.toString()}`);
  }

  return (
    <div className={styles.toolbar}>
      <div className={styles.tabs} role="tablist" aria-label="Filter by state">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            role="tab"
            aria-selected={activeState === tab.value}
            className={clsx(styles.tab, activeState === tab.value && styles.tabActive)}
            onClick={() => setState(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className={styles.search}>
        <Search width={16} height={16} />
        <input
          className={styles.searchInput}
          type="search"
          placeholder="Search name or email"
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          aria-label="Search leads"
        />
      </div>
    </div>
  );
}
