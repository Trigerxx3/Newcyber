'use client'

import Link from 'next/link'
import { ArrowRight, Shield, LogOut } from 'lucide-react'
import { SiteHeader } from '@/components/site-header'
import { useAuth } from '@/contexts/AuthContext'

export default function HomePage() {
  const { user, systemUser, signOut } = useAuth()
  
  // Determine dashboard URL based on user role
  const getDashboardUrl = () => {
    if (systemUser?.role === 'Admin' || systemUser?.role === 'ADMIN') {
      return '/admin'
    }
    return '/dashboard'
  }
  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)]">
      <SiteHeader />

      {/* Hero */}
      <section className="relative flex-1">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nNDAnIGhlaWdodD0nNDAnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zyc+PHBhdGggZD0nTTAgMjBoNDBNIDIwIDB2NDBNIDAgMGg0MCcgc3Ryb2tlPSdyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpJyBmaWxsPSdub25lJyBzdHJva2Utd2lkdGg9JzAuNScvPjwvc3ZnPg==')] opacity-40 pointer-events-none" />
        <div className="container mx-auto px-6 py-16 md:py-24">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight md:leading-[1.1]">
              Combating Digital Narcotics Trafficking
            </h1>
            <p className="mt-6 text-lg md:text-xl text-muted-foreground">
              Detect. Analyze. Intervene.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href={getDashboardUrl()}
                className="animated-gradient-border-button inline-flex items-center gap-2 rounded-md border border-white/10 bg-black/40 px-6 py-3 font-medium shadow-lg hover:bg-black/30"
              >
                <span className="inline-flex items-center gap-2">
                  <Shield className="h-4 w-4 text-primary" />
                  Launch Dashboard
                </span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              {!user ? (
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/5 px-6 py-3 font-medium text-foreground hover:bg-white/10"
                >
                  Sign in
                </Link>
              ) : (
                <button
                  type="button"
                  onClick={async () => { await signOut(); location.href = '/login' }}
                  className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/5 px-6 py-3 font-medium text-foreground hover:bg-white/10"
                >
                  <LogOut className="h-4 w-4" /> Sign out
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="pb-20">
        <div className="container mx-auto px-6">
          <h2 className="text-center text-2xl md:text-3xl font-semibold">Platform Capabilities</h2>
          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Real-Time Monitoring',
                desc: 'Actively monitor public channels and groups across major platforms for suspicious activities.',
              },
              {
                title: 'AI-Powered Analysis',
                desc: 'Leverage AI to analyze text, images, and behavior for trafficking indicators.',
              },
              {
                title: 'OSINT Integration',
                desc: 'Cross-reference usernames and data points to uncover linked identities and networks.',
              },
            ].map((card) => (
              <div key={card.title} className="glassmorphism rounded-xl p-6">
                <h3 className="text-lg font-semibold">{card.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
