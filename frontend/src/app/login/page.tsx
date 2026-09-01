import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthShell } from "@/components/auth/AuthShell";

import { LoginForm } from "./LoginForm";

export const metadata: Metadata = {
  title: "Attorney sign in",
};

export default function LoginPage() {
  return (
    <AuthShell title="Attorney sign in" subtitle="Internal access only.">
      <Suspense fallback={null}>
        <LoginForm />
      </Suspense>
    </AuthShell>
  );
}
