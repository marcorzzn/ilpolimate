import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Conflict Map Dashboard - Real-time World Monitoring",
  description: "High-performance conflict monitoring dashboard for journalistic news outlets. Track global events, conflicts, protests, and disasters in real-time.",
  keywords: ["conflict", "news", "world monitoring", "real-time", "journalism", "map", "crisis", "geopolitics"],
  authors: [{ name: "Conflict Map Team" }],
  icons: {
    icon: "/logo.svg",
  },
  openGraph: {
    title: "Conflict Map Dashboard",
    description: "Real-time world conflict and news monitoring",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Conflict Map Dashboard",
    description: "Real-time world conflict and news monitoring",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground min-h-screen`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
