"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { Button } from "@/components/ui/Button";
import { LogOut } from "@/components/ui/Icons";

export function LogoutButton() {
  const router = useRouter();
  const [pending, start] = useTransition();

  function logout() {
    start(async () => {
      await fetch("/api/auth/logout", { method: "POST" });
      router.replace("/login");
      router.refresh();
    });
  }

  return (
    <Button variant="secondary" size="sm" onClick={logout} loading={pending}>
      <LogOut width={15} height={15} />
      Sign out
    </Button>
  );
}
