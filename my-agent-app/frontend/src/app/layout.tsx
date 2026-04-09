import type { Metadata } from "next";
import React from "react";
import { NuqsAdapter } from "nuqs/adapters/next/app";

import "./globals.css";

export const metadata: Metadata = {
  title: "Medical Booking Assistant",
  description:
    "Chatbot goi y chuyen khoa va ho tro dat lich kham voi giao dien tap trung vao luong hoi thoai AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="antialiased">
        <NuqsAdapter>{children}</NuqsAdapter>
      </body>
    </html>
  );
}
