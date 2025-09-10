import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Helios Console - Continuum Overworld",
  description: "Enterprise Agricultural Data Platform Console",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn(inter.className, "min-h-screen bg-background")}>
        <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 items-center">
            <div className="mr-4 hidden md:flex">
              <a className="mr-6 flex items-center space-x-2" href="/">
                <span className="hidden font-bold sm:inline-block">
                  Helios Console
                </span>
              </a>
              <nav className="flex items-center space-x-6 text-sm font-medium">
                <a
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                  href="/ops"
                >
                  Operations
                </a>
                <a
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                  href="/trace"
                >
                  Trace
                </a>
                <a
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                  href="/agents"
                >
                  Agents
                </a>
                <a
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                  href="/admin/farms"
                >
                  Admin
                </a>
              </nav>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}