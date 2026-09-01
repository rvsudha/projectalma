"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { Alert, StateBadge } from "@/components/ui";
import { ChevronDown } from "@/components/ui/Icons";
import styles from "@/components/dashboard/dashboard.module.css";
import { formatDateTime, fullName } from "@/lib/format";
import type { Lead } from "@/lib/types";

import { ReachOutButton } from "./ReachOutButton";

type SortKey = "name" | "email" | "created_at" | "state";
type SortDir = "asc" | "desc";

const COLLATOR = new Intl.Collator("en", { sensitivity: "base" });

function compare(a: Lead, b: Lead, key: SortKey): number {
  switch (key) {
    case "name":
      return COLLATOR.compare(
        fullName(a.first_name, a.last_name),
        fullName(b.first_name, b.last_name),
      );
    case "email":
      return COLLATOR.compare(a.email, b.email);
    case "state":
      return COLLATOR.compare(a.state, b.state);
    case "created_at":
      return a.created_at.localeCompare(b.created_at);
  }
}

export function LeadsTable({ leads }: { leads: Lead[] }) {
  const [sort, setSort] = useState<{ key: SortKey; dir: SortDir }>({
    key: "created_at",
    dir: "desc",
  });
  const [error, setError] = useState<string | null>(null);

  const rows = useMemo(() => {
    const sorted = [...leads].sort((a, b) => compare(a, b, sort.key));
    return sort.dir === "asc" ? sorted : sorted.reverse();
  }, [leads, sort]);

  function toggleSort(key: SortKey) {
    setSort((prev) =>
      prev.key === key
        ? { key, dir: prev.dir === "asc" ? "desc" : "asc" }
        : { key, dir: key === "created_at" ? "desc" : "asc" },
    );
  }

  function header(key: SortKey, label: string) {
    const active = sort.key === key;
    return (
      <th aria-sort={active ? (sort.dir === "asc" ? "ascending" : "descending") : "none"}>
        <button className={styles.sortBtn} onClick={() => toggleSort(key)}>
          {label}
          {active && (
            <ChevronDown
              width={13}
              height={13}
              style={{ transform: sort.dir === "asc" ? "rotate(180deg)" : undefined }}
            />
          )}
        </button>
      </th>
    );
  }

  return (
    <>
      {error && (
        <div style={{ marginBottom: 12 }}>
          <Alert kind="error">{error}</Alert>
        </div>
      )}
      <div className={styles.tableWrap}>
        <div className={styles.scroll}>
          <table className={styles.table}>
            <thead>
              <tr>
                {header("name", "Name")}
                {header("email", "Email")}
                {header("created_at", "Submitted")}
                {header("state", "Status")}
                <th>Current milestone</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {rows.map((lead) => (
                <tr key={lead.id}>
                  <td className={styles.nameCell}>
                    <Link href={`/leads/${lead.id}`}>
                      {fullName(lead.first_name, lead.last_name)}
                    </Link>
                  </td>
                  <td className={styles.emailCell}>{lead.email}</td>
                  <td className={styles.dim}>{formatDateTime(lead.created_at)}</td>
                  <td>
                    <StateBadge state={lead.state} />
                  </td>
                  <td className={styles.milestoneCell}>{lead.milestone}</td>
                  <td className={styles.actionCell}>
                    <ReachOutButton
                      leadId={lead.id}
                      leadName={fullName(lead.first_name, lead.last_name)}
                      toState={lead.state === "PENDING" ? "REACHED_OUT" : "PENDING"}
                      onError={setError}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
