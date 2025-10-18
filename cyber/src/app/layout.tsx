import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ClientAuthProvider } from '@/components/ClientAuthProvider'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap', // Reduces layout shift
  preload: true,
  fallback: ['system-ui', 'arial'] // Fallback fonts
})

export const metadata: Metadata = {
  title: 'Cyber Intelligence Platform',
  description: 'Advanced threat monitoring and analysis platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Suppress browser extension runtime errors
              if (typeof window !== 'undefined') {
                // Handle chrome extension runtime errors
                const originalError = console.error;
                console.error = function(...args) {
                  const message = args[0]?.toString() || '';
                  
           // Suppress specific extension-related errors
           if (
             message.includes('runtime.lastError') ||
             message.includes('Extension context invalidated') ||
             message.includes('message channel is closed') ||
             message.includes('message channel closed before a response was received') ||
             message.includes('A listener indicated an asynchronous response by returning true') ||
             message.includes('back/forward cache') ||
             message.includes('ERR_BLOCKED_BY_CLIENT') ||
             message.includes('play.google.com/log') ||
             message.includes('google.com/log') ||
             message.includes('POST https://play.google.com') ||
             message.includes('net::ERR_BLOCKED_BY_CLIENT') ||
             message.includes('https://play.google.com/log') ||
             message.includes('m=mnb,identifier_vie') ||
             message.includes('format=json&hasfast=true') ||
             message.includes('Failed to fetch this Firebase app') ||
             message.includes('Falling back to the measurement ID') ||
             message.includes('[Fast Refresh]') ||
             message.includes('turbopack-hot-reloader')
           ) {
             return; // Suppress these errors
           }
                  
                  // Log other errors normally
                  originalError.apply(console, args);
                };
                
                // Handle unhandled promise rejections that might be extension-related
                window.addEventListener('unhandledrejection', function(event) {
                  const reason = event.reason?.toString() || '';
           if (
             reason.includes('runtime.lastError') ||
             reason.includes('Extension context') ||
             reason.includes('message channel closed before a response was received') ||
             reason.includes('A listener indicated an asynchronous response by returning true') ||
             reason.includes('ERR_BLOCKED_BY_CLIENT') ||
             reason.includes('play.google.com') ||
             reason.includes('net::ERR_BLOCKED_BY_CLIENT') ||
             reason.includes('m=mnb,identifier_vie') ||
             reason.includes('format=json&hasfast=true') ||
             reason.includes('Failed to fetch this Firebase app')
           ) {
             event.preventDefault(); // Prevent logging of extension errors
           }
                });
                
                // Suppress network errors from Google services and extensions
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                  return originalFetch.apply(this, args).catch(error => {
                    const url = args[0]?.toString() || '';
                    if (
                      url.includes('play.google.com') ||
                      url.includes('google.com/log') ||
                      url.includes('format=json&hasfast=true') ||
                      error.message?.includes('ERR_BLOCKED_BY_CLIENT') ||
                      error.message?.includes('net::ERR_BLOCKED_BY_CLIENT')
                    ) {
                      // Silently ignore these blocked requests
                      return Promise.reject(new Error('Request blocked by client - suppressed'));
                    }
                    throw error;
                  });
                };
              }
            `,
          }}
        />
      </head>
      <body suppressHydrationWarning>
        <ClientAuthProvider>
          {children}
        </ClientAuthProvider>
      </body>
    </html>
  )
}
