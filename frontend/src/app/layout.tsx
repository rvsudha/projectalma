import type { Metadata, Viewport } from "next";
import { Inter, Lora } from "next/font/google";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const serif = Lora({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("http://localhost:3000"),
  title: {
    default: "ProjectAlma",
    template: "%s · ProjectAlma",
  },
  description:
    "Share your background and resume. A qualified attorney will review your profile and contact you with a strategic plan for your visa process.",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#0b756e",
  colorScheme: "light",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${serif.variable}`}>
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
