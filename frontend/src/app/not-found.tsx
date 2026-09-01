import { ButtonLink } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";

export default function NotFound() {
  return (
    <main
      style={{
        minHeight: "100dvh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        textAlign: "center",
      }}
    >
      <div>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
          <Logo />
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: 8 }}>Page not found</h1>
        <p className="muted" style={{ marginBottom: 22 }}>
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
        <ButtonLink href="/">Go home</ButtonLink>
      </div>
    </main>
  );
}
