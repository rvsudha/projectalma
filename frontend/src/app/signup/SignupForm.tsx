"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import styles from "@/components/auth/auth.module.css";
import { Alert } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { SelectField, TextField } from "@/components/ui/Field";
import { postAuthDestination } from "@/lib/redirect";
import { signupFormSchema, type SignupFormValues } from "@/lib/validation";

export function SignupForm() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupFormSchema),
    defaultValues: {
      role: "applicant",
      full_name: "",
      email: "",
      password: "",
      invite_code: "",
    },
  });

  const role = watch("role");

  async function onSubmit(values: SignupFormValues) {
    setFormError(null);
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      setFormError(body?.error?.message ?? "Sign up failed. Please try again.");
      return;
    }
    router.replace(postAuthDestination(body?.role ?? values.role, null));
    router.refresh();
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
      {formError && <Alert kind="error">{formError}</Alert>}

      <SelectField
        label="I am signing up as"
        error={errors.role?.message}
        {...register("role")}
      >
        <option value="applicant">An applicant — I want to submit / track a case</option>
        <option value="attorney">
          An attorney — internal staff (invite code required)
        </option>
      </SelectField>

      <TextField
        label="Full name"
        autoComplete="name"
        error={errors.full_name?.message}
        {...register("full_name")}
      />
      <TextField
        label="Email"
        type="email"
        autoComplete="username"
        error={errors.email?.message}
        {...register("email")}
      />
      <TextField
        label="Password"
        type="password"
        autoComplete="new-password"
        hint="At least 8 characters"
        error={errors.password?.message}
        {...register("password")}
      />

      {role === "attorney" && (
        <TextField
          label="Invite code"
          autoComplete="off"
          error={errors.invite_code?.message}
          {...register("invite_code")}
        />
      )}

      <Button type="submit" size="lg" block loading={isSubmitting}>
        {isSubmitting ? "Creating account…" : "Sign up"}
      </Button>

      {role === "attorney" && (
        <p className={styles.hint}>
          Demo invite code: <code>welcome</code>
        </p>
      )}
      <p className={styles.switch}>
        Already have an account? <Link href="/login">Log in</Link>
      </p>
      <Link href="/" className={styles.back}>
        ← Back to site
      </Link>
    </form>
  );
}
