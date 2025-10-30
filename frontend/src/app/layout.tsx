import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { WebSocketProvider } from "@/contexts/WebSocketContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "happyStock - 虚拟股票市场",
  description: "A股模拟交易系统 - 学习投资，零风险实战",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${inter.variable} antialiased`}>
        <WebSocketProvider autoConnect={true} autoAdjustThrottle={true}>
          {children}
        </WebSocketProvider>
      </body>
    </html>
  );
}
