"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Camera, Terminal, Waves } from 'lucide-react'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  // Page 'Impact' (Page 2) sudah dihapus dari daftar navItems
  const navItems = [
    { name: 'Detector', href: '/', icon: Camera },
    { name: 'Recycler', href: '/recycler', icon: Terminal },
  ]

  return (
    <html lang="en">
      <body className="bg-[#050505] text-white flex min-h-screen">
        {/* SIDEBAR NAVIGATION */}
        <aside className="w-24 md:w-64 border-r border-white/10 flex flex-col p-6 space-y-10 bg-black/50 backdrop-blur-md">
          <div className="flex items-center gap-3 px-2">
            <div className="bg-blue-600 p-2 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.4)]">
              <Waves size={24} className="text-white" />
            </div>
            <span className="hidden md:block font-black text-xl italic tracking-tighter">GHOST-RAY</span>
          </div>

          <nav className="flex-1 space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-4 p-4 rounded-2xl transition-all duration-300 group ${
                    isActive 
                      ? 'bg-blue-600 text-white shadow-lg' 
                      : 'hover:bg-white/5 text-slate-500 hover:text-white'
                  }`}
                >
                  <item.icon size={22} className={isActive ? 'text-white' : 'group-hover:text-blue-400'} />
                  <span className={`hidden md:block font-bold text-sm ${isActive ? 'text-white' : ''}`}>
                    {item.name}
                  </span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 bg-white/5 rounded-2xl border border-white/5 hidden md:block">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Network</p>
            <div className="flex items-center gap-2 text-[10px] font-bold text-emerald-400">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" /> SOLANA DEVNET
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto min-h-screen">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}