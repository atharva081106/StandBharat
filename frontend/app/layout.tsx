import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { AuthProvider } from '@/lib/providers/MockProvider'
import { BrandBrainContextProvider } from '@/lib/providers/MockProvider'
import { WebsiteAnalysisProvider } from '@/lib/providers/WebsiteAnalysisProvider'
import { DocumentProvider } from '@/lib/providers/DocumentProvider'
import { AuthModal } from '@/components/auth-modal'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StandBharat - AI CMO',
  description: 'Your AI CMO for Real Growth',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#FAFAF8] text-gray-900`} suppressHydrationWarning>
        <AuthProvider>
          <BrandBrainContextProvider>
            <WebsiteAnalysisProvider>
              <DocumentProvider>
                {children}
                <AuthModal />
              </DocumentProvider>
            </WebsiteAnalysisProvider>
          </BrandBrainContextProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
