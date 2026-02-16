import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "BigSpring Knowledge Search",
  description: "AI-powered search for your sales training materials",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', background: "#f5f7fa", color: "#1a1a2e" }}>
        {children}
      </body>
    </html>
  );
}
