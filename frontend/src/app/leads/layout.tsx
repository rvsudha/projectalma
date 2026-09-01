import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import styles from "@/components/dashboard/dashboard.module.css";
import { getCurrentUser, UnauthorizedError } from "@/lib/api";

export const metadata: Metadata = {
  title: "Leads",
};

export default async function LeadsLayout({ children }: { children: React.ReactNode }) {
  let user;
  try {
    user = await getCurrentUser();
  } catch (err) {
    if (err instanceof UnauthorizedError) redirect("/login?next=/leads");
    throw err;
  }
  if (user.role !== "attorney") redirect("/my");

  return (
    <div className={styles.shell}>
      <DashboardHeader user={user} />
      <div className={styles.content}>
        <div className="container">{children}</div>
      </div>
    </div>
  );
}
