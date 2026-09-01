import { LeadForm } from "@/components/leads/LeadForm";
import { PublicHeader } from "@/components/marketing/PublicHeader";
import { SiteFooter } from "@/components/marketing/SiteFooter";
import { Check } from "@/components/ui/Icons";

import styles from "@/components/marketing/marketing.module.css";

const POINTS = [
  {
    label: "Licensed Legal Counsel",
    body: "Guaranteed oversight by practicing immigration attorneys.",
  },
  {
    label: "Accelerated Timelines",
    body: "Comprehensive case preparation in approximately two weeks.",
  },
  {
    label: "Dedicated Support",
    body: "A single, consistent point of contact from consultation to completion.",
  },
];

export default function HomePage() {
  return (
    <>
      <PublicHeader />
      <main id="main" className={styles.hero}>
        <div className={styles.heroWash} aria-hidden />
        <div className={`container ${styles.heroGrid}`}>
          <div className={styles.heroCopy}>
            <h1>
              Navigating Your Immigration
              <br />
              Journey with Expertise
            </h1>
            <p className={styles.heroLede}>
              Share your background and resume with us to get started. A qualified
              attorney will review your profile and contact you with a customized,
              strategic plan for your visa process.
            </p>
            <ul className={styles.heroPoints}>
              {POINTS.map((point) => (
                <li key={point.label}>
                  <Check width={18} height={18} />
                  <span>
                    <strong>{point.label}:</strong> {point.body}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className={styles.formPanel}>
            <h2 className={styles.formTitle}>Get started</h2>
            <p className={styles.formSub}>
              First name, last name, email, and your resume or CV.
            </p>
            <LeadForm />
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
