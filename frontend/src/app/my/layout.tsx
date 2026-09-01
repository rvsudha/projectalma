import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { PortalHeader } from "@/components/portal/PortalHeader";
import styles from "@/components/portal/portal.module.css";
import { getCurrentUser, UnauthorizedError } from "@/lib/api";

export const metadata: Metadata = {
  title: "Your cases",
};

export default async function PortalLayout({ children }: { children: React.ReactNode }) {
  let user;
  try {
    user = await getCurrentUser();
  } catch (err) {
    if (err instanceof UnauthorizedError) redirect("/login?next=/my");
    throw err;
  }
  if (user.role === "attorney") redirect("/leads");

  return (
    <div className={styles.shell}>
      <PortalHeader user={user} />
      <div className={styles.content}>
        <div className="container narrow">{children}</div>
      </div>
    </div>
  );
}
