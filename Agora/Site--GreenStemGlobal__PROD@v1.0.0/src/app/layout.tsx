import './globals.css'

export const metadata = {
  title: "GreenStem Global",
  description: "From Leaf to Root — Traceable Freshness.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 text-neutral-900">
        <header className="px-6 py-4 border-b bg-white">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <a href="/" className="font-semibold">GreenStem Global</a>
            <nav className="text-sm">
              <a className="mr-4 hover:underline" href="/buyers">Buyers</a>
              <a className="hover:underline" href="/investors">Investors</a>
            </nav>
          </div>
        </header>
        <main className="px-6 py-8">
          <div className="max-w-6xl mx-auto">{children}</div>
        </main>
        <footer className="px-6 py-6 text-sm text-neutral-500">
          <div className="max-w-6xl mx-auto">© {new Date().getFullYear()} GreenStem Global</div>
        </footer>
      </body>
    </html>
  );
}