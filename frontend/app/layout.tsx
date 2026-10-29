import type { Metadata } from "next";
import { Suspense } from "react";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { AppShell } from "@/components/common/app-shell";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Adaptive Task & Deadline Management",
  description: "Minimalist adaptive task and deadline management platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} font-sans h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const observer = new MutationObserver((mutations) => {
                  for (let i = 0; i < mutations.length; i++) {
                    const m = mutations[i];
                    if (m.type === 'attributes') {
                      const name = m.attributeName;
                      if (name && (name === 'bis_skin_checked' || name === 'bis_register' || name.startsWith('__processed_'))) {
                        m.target.removeAttribute(name);
                      }
                    }
                  }
                });
                observer.observe(document.documentElement, { attributes: true, subtree: true });
              } catch (_) {}
            `,
          }}
        />
      </head>
      <body
        className="min-h-full flex flex-col bg-background text-foreground font-sans"
        suppressHydrationWarning
      >
        <Providers>
          <Suspense fallback={<div suppressHydrationWarning className="min-h-screen w-full bg-background" />}>
            <AppShell>{children}</AppShell>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}
