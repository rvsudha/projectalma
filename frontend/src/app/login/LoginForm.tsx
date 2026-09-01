"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import styles from "@/components/auth/auth.module.css";
import { Alert } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/Field";
import { postAuthDestination } from "@/lib/redirect";
import { loginFormSchema, type LoginFormValues } from "@/lib/validation";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const nextParam = params.get("next");

  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginFormValues) {
    setFormError(null);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      setFormError(body?.error?.message ?? "Sign in failed. Please try again.");
      return;
    }
    router.replace(postAuthDestination(body?.role ?? "applicant", nextParam));
    router.refresh();
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
      {formError && <Alert kind="error">{formError}</Alert>}
      <TextField
        label="Email"
        type="email"
        autoComplete="username"
        autoFocus
        error={errors.email?.message}
        {...register("email")}
      />
      <TextField
        label="Password"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register("password")}
      />
      <Button type="submit" size="lg" block loading={isSubmitting}>
        {isSubmitting ? "Signing in…" : "Log in"}
      </Button>

      <p className={styles.hint}>
        Demo — attorney: <code>attorney@projectalma.com</code>
        <br />
        applicant: <code>applicant@example.com</code> · both <code>changeme123</code>
      </p>
      <p className={styles.switch}>
        Need an account? <Link href="/signup">Sign up</Link>
      </p>
      <Link href="/" className={styles.back}>
        ← Back to site
      </Link>
    </form>
  );
}
