import type { Metadata } from "next";
import "./styles/globals.css";

export const metadata: Metadata = {
  title: "EmberLearn - AI-Powered Python Tutoring",
  description: "Master Python with personalized AI tutors",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  );
}
