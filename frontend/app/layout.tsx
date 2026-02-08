"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Camera, Terminal, Waves } from 'lucide-react'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  const navItems = [
    { name: 'Detector', href: '/', icon: Camera },
    { name: 'Recycler', href: '/recycler', icon: Terminal },
  ]

  return (
    <html lang="en">
      <body className="bg-slate-950 text-white flex min-h-screen">
        {/* SIDEBAR NAVIGATION */}
        <aside className="w-24 md:w-64 border-r border-slate-800 flex flex-col p-6 space-y-10 bg-slate-900">
          <div className="flex items-center gap-3 px-2">
            <div className="bg-purple-600 p-2 rounded-lg">
              <Waves size={24} className="text-white" />
            </div>
            <span className="hidden md:block font-bold text-xl text-purple-100">GHOST-RAY</span>
          </div>

          <nav className="flex-1 space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
                    isActive 
                      ? 'bg-purple-600 text-white' 
                      : 'hover:bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <item.icon size={22} />
                  <span className={`hidden md:block font-medium text-sm`}>
                    {item.name}
                  </span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 bg-slate-800 rounded-xl border border-slate-700 hidden md:block">
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Network</p>
            <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" /> Solana Devnet
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <div className="max-w-7xl mx-auto min-h-screen">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}