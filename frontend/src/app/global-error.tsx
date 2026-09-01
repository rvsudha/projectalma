"use client";

export default function GlobalError({ reset }: { error: Error; reset: () => void }) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "system-ui, sans-serif",
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          margin: 0,
          background: "#fbfaf7",
          color: "#16181d",
        }}
      >
        <div style={{ textAlign: "center", padding: 24 }}>
          <h1 style={{ fontSize: "1.6rem" }}>Something went wrong</h1>
          <p style={{ color: "#4b4f5a" }}>The application hit an unexpected error.</p>
          <button
            onClick={reset}
            style={{
              marginTop: 12,
              padding: "10px 18px",
              borderRadius: 8,
              border: "none",
              background: "#0b756e",
              color: "#fff",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Reload
          </button>
        </div>
      </body>
    </html>
  );
}
