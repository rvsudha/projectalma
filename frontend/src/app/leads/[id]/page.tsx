import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { ActivityTimeline } from "@/components/leads/ActivityTimeline";
import { DetailReachOut } from "@/components/leads/DetailReachOut";
import { Card, StateBadge } from "@/components/ui";
import { Download } from "@/components/ui/Icons";
import { ApiError, getLead, UnauthorizedError } from "@/lib/api";
import { formatBytes, formatDateTime, fullName } from "@/lib/format";

import styles from "./detail.module.css";

export const dynamic = "force-dynamic";

async function loadLead(id: string) {
  try {
    return await getLead(id);
  } catch (err) {
    if (err instanceof UnauthorizedError) redirect(`/login?next=/leads/${id}`);
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  try {
    const lead = await getLead(params.id);
    return { title: fullName(lead.first_name, lead.last_name) };
  } catch {
    return { title: "Lead" };
  }
}

export default async function LeadDetailPage({ params }: { params: { id: string } }) {
  const lead = await loadLead(params.id);
  const name = fullName(lead.first_name, lead.last_name);

  return (
    <div style={{ maxWidth: 880 }}>
      <Link href="/leads" className={styles.back}>
        ← All leads
      </Link>

      <div className={styles.head}>
        <h1>{name}</h1>
        <StateBadge state={lead.state} />
      </div>
      <p className={styles.submitted}>Submitted {formatDateTime(lead.created_at)}</p>

      <div className={styles.grid}>
        <Card>
          <dl className={styles.dl}>
            <dt>Email</dt>
            <dd>
              <a href={`mailto:${lead.email}`}>{lead.email}</a>
            </dd>

            <dt>Resume</dt>
            <dd>
              <a
                className={styles.resumeLink}
                href={`/api/leads/${lead.id}/resume`}
                target="_blank"
                rel="noreferrer"
              >
                <Download width={15} height={15} />
                {lead.resume_filename}
                <span className={styles.resumeMeta}>
                  {formatBytes(lead.resume_size_bytes)}
                </span>
              </a>
            </dd>

            <dt>Reached out</dt>
            <dd>{formatDateTime(lead.reached_out_at)}</dd>
          </dl>

          <div className={styles.actions}>
            <DetailReachOut leadId={lead.id} leadName={name} state={lead.state} />
          </div>
        </Card>

        <Card>
          <p className={styles.panelTitle}>Activity</p>
          <ActivityTimeline events={lead.events} />
        </Card>
      </div>
    </div>
  );
}
