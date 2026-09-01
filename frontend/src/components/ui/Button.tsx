import { clsx } from "clsx";
import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";

import styles from "./Button.module.css";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

interface CommonProps {
  variant?: Variant;
  size?: Size;
  block?: boolean;
  loading?: boolean;
  children: ReactNode;
}

const variantClass: Record<Variant, string | undefined> = {
  primary: undefined,
  secondary: styles.secondary,
  ghost: styles.ghost,
  danger: styles.danger,
};

const sizeClass: Record<Size, string | undefined> = {
  sm: styles.sm,
  md: undefined,
  lg: styles.lg,
};

function classes(p: CommonProps, extra?: string) {
  return clsx(
    styles.btn,
    variantClass[p.variant ?? "primary"],
    sizeClass[p.size ?? "md"],
    p.block && styles.block,
    extra,
  );
}

export function Button({
  variant,
  size,
  block,
  loading,
  children,
  className,
  disabled,
  ...rest
}: CommonProps & ComponentPropsWithoutRef<"button">) {
  return (
    <button
      className={classes({ variant, size, block, loading, children }, className)}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <span className={styles.spinner} aria-hidden />}
      {children}
    </button>
  );
}

export function ButtonLink({
  variant,
  size,
  block,
  children,
  className,
  ...rest
}: CommonProps & ComponentPropsWithoutRef<typeof Link>) {
  return (
    <Link className={classes({ variant, size, block, children }, className)} {...rest}>
      {children}
    </Link>
  );
}
