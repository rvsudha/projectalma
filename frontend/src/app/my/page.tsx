import { redirect } from "next/navigation";

import { CaseCard } from "@/components/portal/CaseCard";
import styles from "@/components/portal/portal.module.css";
import { ButtonLink } from "@/components/ui/Button";
import { getMyLeads, UnauthorizedError } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MyCasesPage() {
  let cases;
  try {
    cases = await getMyLeads();
  } catch (err) {
    if (err instanceof UnauthorizedError) redirect("/login?next=/my");
    throw err;
  }

  return (
    <>
      <h1>Your cases</h1>
      <p className={styles.lede}>
        Track the status of everything you&apos;ve submitted. An attorney updates it as
        your case progresses.
      </p>

      {cases.length === 0 ? (
        <div className={styles.empty}>
          <h2>Nothing here yet</h2>
          <p style={{ marginBottom: 18 }}>
            Submissions you make with this email address will appear here.
          </p>
          <ButtonLink href="/">Start a submission</ButtonLink>
        </div>
      ) : (
        <div className={styles.cases}>
          {cases.map((lead) => (
            <CaseCard key={lead.id} lead={lead} />
          ))}
        </div>
      )}
    </>
  );
}
