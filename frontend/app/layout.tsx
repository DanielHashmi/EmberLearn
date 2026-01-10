import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/shared/theme-provider";
import { GlowBackground } from "@/components/shared/glow-background";
import { NavHeader } from "@/components/shared/nav-header";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "EmberLearn - AI-Powered Python Tutoring",
  description: "Learn Python programming through conversational AI agents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.variable}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <GlowBackground />
          <NavHeader />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
