import { redirect } from "next/navigation";

import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { StatTiles } from "@/components/dashboard/StatTiles";
import styles from "@/components/dashboard/dashboard.module.css";
import { ActivityHint } from "@/components/leads/EmptyState";
import { LeadsTable } from "@/components/leads/LeadsTable";
import { LeadsToolbar } from "@/components/leads/LeadsToolbar";
import { Pagination } from "@/components/leads/Pagination";
import { getActivity, getLeadStats, listLeads, UnauthorizedError } from "@/lib/api";
import { flatten, one, type SearchParams } from "@/lib/params";
import type { LeadState } from "@/lib/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 20;

function parseState(value: string | undefined): LeadState | undefined {
  return value === "PENDING" || value === "REACHED_OUT" ? value : undefined;
}

export default async function LeadsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const flat = flatten(searchParams);
  const state = parseState(one(searchParams.state));
  const search = one(searchParams.search);
  const page = Math.max(1, Number(one(searchParams.page)) || 1);
  const offset = (page - 1) * PAGE_SIZE;

  let data;
  let stats;
  let activity;
  try {
    [data, stats, activity] = await Promise.all([
      listLeads({ state, search, limit: PAGE_SIZE, offset }),
      getLeadStats(),
      getActivity(10),
    ]);
  } catch (err) {
    if (err instanceof UnauthorizedError) redirect("/login?next=/leads");
    throw err;
  }

  const filtered = Boolean(state || search);

  return (
    <>
      <div className={styles.pageHead}>
        <h1>Dashboard</h1>
      </div>

      <StatTiles stats={stats} />

      <div className={styles.pageHead}>
        <h2 style={{ fontSize: "1.15rem" }}>Leads</h2>
        <span className={styles.count}>
          {data.meta.total} {data.meta.total === 1 ? "lead" : "leads"}
          {filtered ? " matching" : " total"}
        </span>
      </div>

      <LeadsToolbar />

      {data.items.length === 0 ? (
        <ActivityHint filtered={filtered} />
      ) : (
        <>
          <LeadsTable leads={data.items} />
          <Pagination meta={data.meta} searchParams={flat} />
        </>
      )}

      <RecentActivity items={activity} />
    </>
  );
}
