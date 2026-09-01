import type { Metadata } from "next";

import { AuthShell } from "@/components/auth/AuthShell";

import { SignupForm } from "./SignupForm";

export const metadata: Metadata = {
  title: "Sign up",
};

export default function SignupPage() {
  return (
    <AuthShell
      title="Create your account"
      subtitle="Applicants can track their case; attorneys review submissions."
    >
      <SignupForm />
    </AuthShell>
  );
}
