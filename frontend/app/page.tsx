import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Gift Genie - AI로 찾아내는 취향저격 선물',
  description: '5분 안에 완벽한 선물을 찾아드립니다.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Minimal Centered Layout Container */}
      <div className="min-h-screen flex items-center justify-center px-8">
        <div className="text-center max-w-2xl mx-auto">
          {/* Main Heading */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black text-gray-900 mb-16 leading-tight">
            AI로 찾아내는<br/>
            취향저격 선물
          </h1>
          
          {/* Main CTA Button */}
          <Link href="/recommendations">
            <button className="inline-block bg-gray-900 text-white px-12 py-6 text-xl font-semibold rounded-2xl hover:bg-gray-800 transition-colors duration-200 mb-24">
              선물 추천 받기
            </button>
          </Link>
          
          {/* Minimal Supporting Information */}
          <div className="space-y-6 text-gray-600 text-lg">
            <p>5분 안에 완벽한 선물을 찾아드립니다</p>
            <p>AI가 개인 취향을 분석해 최적의 선물을 추천합니다</p>
          </div>
        </div>
      </div>
    </div>
  )
}