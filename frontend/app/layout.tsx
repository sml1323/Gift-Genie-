import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { cn } from '@/lib/utils'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['400', '500', '600', '700', '800', '900'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Gift Genie - AI 선물 추천 서비스',
  description: '5분 안에 완벽한 선물을 찾아주는 개인화된 AI 추천 서비스',
  keywords: ['선물', '추천', 'AI', '인공지능', '개인화', '생일선물', '기념일선물'],
  authors: [{ name: 'Gift Genie Team' }],
  openGraph: {
    title: 'Gift Genie - AI 선물 추천 서비스',
    description: '5분 안에 완벽한 선물을 찾아주는 개인화된 AI 추천 서비스',
    type: 'website',
    locale: 'ko_KR',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body 
        className={cn(
          "min-h-screen bg-trend-white font-sans antialiased",
          inter.variable
        )}
      >
        <main className="relative flex min-h-screen flex-col">
          {children}
        </main>
        <Toaster />
      </body>
    </html>
  )
}