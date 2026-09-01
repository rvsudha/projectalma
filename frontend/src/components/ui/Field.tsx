"use client";

import { clsx } from "clsx";
import { forwardRef } from "react";
import type { ComponentPropsWithoutRef, ReactNode } from "react";

import styles from "./Field.module.css";

interface FieldShellProps {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
  children: ReactNode;
}

export function FieldShell({
  id,
  label,
  hint,
  error,
  optional,
  children,
}: FieldShellProps) {
  return (
    <div className={clsx(styles.field, error && styles.invalid)}>
      <label className={styles.label} htmlFor={id}>
        {label}
        {optional && <span className={styles.optional}>optional</span>}
      </label>
      {hint && (
        <p className={styles.hint} id={`${id}-hint`}>
          {hint}
        </p>
      )}
      {children}
      {error && (
        <p className={styles.error} id={`${id}-error`} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

type InputProps = {
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
} & ComponentPropsWithoutRef<"input">;

export const TextField = forwardRef<HTMLInputElement, InputProps>(function TextField(
  { label, hint, error, optional, id, ...rest },
  ref,
) {
  const fieldId = id ?? rest.name ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <FieldShell id={fieldId} label={label} hint={hint} error={error} optional={optional}>
      <input
        ref={ref}
        id={fieldId}
        className={styles.control}
        aria-invalid={error ? true : undefined}
        aria-describedby={
          clsx(hint && `${fieldId}-hint`, error && `${fieldId}-error`) || undefined
        }
        {...rest}
      />
    </FieldShell>
  );
});

type SelectProps = {
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
  children: ReactNode;
} & ComponentPropsWithoutRef<"select">;

export const SelectField = forwardRef<HTMLSelectElement, SelectProps>(
  function SelectField({ label, hint, error, optional, id, children, ...rest }, ref) {
    const fieldId = id ?? rest.name ?? label.toLowerCase().replace(/\s+/g, "-");
    return (
      <FieldShell
        id={fieldId}
        label={label}
        hint={hint}
        error={error}
        optional={optional}
      >
        <select ref={ref} id={fieldId} className={styles.control} {...rest}>
          {children}
        </select>
      </FieldShell>
    );
  },
);
