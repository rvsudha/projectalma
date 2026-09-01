"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";

import { Alert } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/Field";
import { FileDropzone } from "@/components/ui/FileDropzone";
import { Check } from "@/components/ui/Icons";
import {
  ACCEPTED_RESUME_TYPES,
  leadFormSchema,
  type LeadFormValues,
} from "@/lib/validation";

import styles from "./LeadForm.module.css";

type Submission = "idle" | "submitting" | "done";

export function LeadForm() {
  const [phase, setPhase] = useState<Submission>("idle");
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<LeadFormValues>({
    resolver: zodResolver(leadFormSchema),
    defaultValues: { first_name: "", last_name: "", email: "" },
    mode: "onTouched",
  });

  async function onSubmit(values: LeadFormValues) {
    if (!(values.resume instanceof File)) return;
    setPhase("submitting");
    setServerError(null);

    const body = new FormData();
    body.set("first_name", values.first_name);
    body.set("last_name", values.last_name);
    body.set("email", values.email);
    body.set("resume", values.resume);

    try {
      const res = await fetch("/api/leads", { method: "POST", body });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        setServerError(
          data?.error?.message ??
            "Something went wrong submitting your details. Please try again.",
        );
        setPhase("idle");
        return;
      }
      reset();
      setPhase("done");
    } catch {
      setServerError("Network error — please check your connection and try again.");
      setPhase("idle");
    }
  }

  if (phase === "done") {
    return (
      <div className={styles.success}>
        <span className={styles.successIcon}>
          <Check width={26} height={26} />
        </span>
        <h3>You&apos;re all set</h3>
        <p>
          Thanks — we&apos;ve received your details. A qualified attorney will review your
          profile and contact you by email with a strategic plan for your visa process.
        </p>
        <Button variant="secondary" onClick={() => setPhase("idle")}>
          Submit another
        </Button>
      </div>
    );
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
      {serverError && <Alert kind="error">{serverError}</Alert>}

      <div className={styles.row}>
        <TextField
          label="First name"
          autoComplete="given-name"
          error={errors.first_name?.message}
          {...register("first_name")}
        />
        <TextField
          label="Last name"
          autoComplete="family-name"
          error={errors.last_name?.message}
          {...register("last_name")}
        />
      </div>

      <TextField
        label="Email"
        type="email"
        inputMode="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register("email")}
      />

      <Controller
        control={control}
        name="resume"
        render={({ field }) => (
          <FileDropzone
            label="Resume / CV"
            accept={[...ACCEPTED_RESUME_TYPES, ".pdf", ".doc", ".docx"].join(",")}
            value={field.value}
            onChange={field.onChange}
            error={errors.resume?.message}
          />
        )}
      />

      <Button type="submit" size="lg" block loading={phase === "submitting"}>
        {phase === "submitting" ? "Submitting…" : "Submit"}
      </Button>

      <p className={styles.consent}>
        By submitting, you agree that an attorney may contact you about your visa process.
        We never share your information.
      </p>
    </form>
  );
}
