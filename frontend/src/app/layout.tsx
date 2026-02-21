import type { Metadata } from "next";
import { Geist, Geist_Mono, Newsreader } from "next/font/google";
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import { Toaster } from "sonner";
import { StoreHydration } from "@/components/StoreHydration";
import "./globals.css";

/**
 * Quantum Studio Root Layout v3.1
 * 
 * Canvas Layer: 全屏背景画布
 * Fonts: Geist Sans + Geist Mono + Newsreader
 * State: NuqsAdapter for URL state management
 */

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "Quantum Studio",
  description: "AI-Powered Web3 Research & Creation Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`
          ${geistSans.variable} 
          ${geistMono.variable} 
          ${newsreader.variable} 
          font-sans antialiased
          bg-canvas text-ink-primary
          min-h-screen
        `}
        suppressHydrationWarning
      >
        <StoreHydration />
        <NuqsAdapter>
          {children}
        </NuqsAdapter>
        <Toaster position="bottom-right" richColors />
      </body>
    </html>
  );
}

