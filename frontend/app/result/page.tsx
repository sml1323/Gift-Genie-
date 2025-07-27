"use client"

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ExternalLink, Star, ShoppingCart, Heart, Share2 } from 'lucide-react'
import type { EnhancedRecommendationResponse } from '@/types/gift'

export default function ResultPage() {
  const router = useRouter()
  const [recommendations, setRecommendations] = useState<EnhancedRecommendationResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get recommendations from session storage
    const stored = sessionStorage.getItem('giftRecommendations')
    if (stored) {
      try {
        const data = JSON.parse(stored)
        setRecommendations(data)
      } catch (error) {
        console.error('Failed to parse recommendations:', error)
      }
    }
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="modern-bg min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-trend-orange-500 mx-auto mb-4"></div>
          <p className="modern-subtitle">결과를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  if (!recommendations) {
    return (
      <div className="modern-bg min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-8">
          <h2 className="modern-title mb-4">추천 결과를 찾을 수 없습니다</h2>
          <p className="modern-subtitle mb-8">다시 추천을 받아보세요.</p>
          <Button onClick={() => router.push('/recommendations')} className="modern-button-primary">
            새로 추천받기
          </Button>
        </div>
      </div>
    )
  }

  const { recommendations: gifts, search_results, pipeline_metrics, total_processing_time } = recommendations

  return (
    <div className="modern-bg min-h-screen">
      {/* Header */}
      <div className="relative pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-8">
          <div className="flex items-center justify-between mb-8">
            <Button 
              onClick={() => router.push('/recommendations')}
              className="flex items-center space-x-2 text-trend-gray-600 hover:text-trend-gray-800"
              variant="ghost"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>새로 추천받기</span>
            </Button>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                <Heart className="h-5 w-5 text-trend-gray-600" />
              </button>
              <button className="p-2 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                <Share2 className="h-5 w-5 text-trend-gray-600" />
              </button>
            </div>
          </div>
          
          <div className="text-center">
            <h1 className="modern-display mb-6">
              당신을 위한 <span className="text-trend-orange-500">완벽한 선물</span>
            </h1>
            <p className="modern-subtitle mb-4">
              AI가 {total_processing_time.toFixed(1)}초 만에 찾은 {gifts.length}개의 맞춤 추천
            </p>
            
            {/* Metrics */}
            <div className="flex justify-center items-center space-x-8 text-sm text-trend-gray-500">
              <div>AI 분석: {pipeline_metrics.ai_generation_time.toFixed(1)}s</div>
              <div>상품 검색: {pipeline_metrics.search_execution_time.toFixed(1)}s</div>
              <div>검색 결과: {pipeline_metrics.search_results_count}개</div>
              {recommendations.simulation_mode && (
                <div className="text-trend-orange-600 font-medium">시뮬레이션 모드</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="max-w-6xl mx-auto px-8 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Recommendations */}
          <div className="lg:col-span-2">
            <h2 className="modern-title mb-6">🎁 추천 선물</h2>
            <div className="space-y-8">
              {gifts.map((gift, index) => (
                <div key={index} className="modern-card-elevated overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-lg font-bold text-trend-orange-500">#{index + 1}</span>
                          <span className="text-xs bg-trend-orange-100 text-trend-orange-700 px-2 py-1 rounded-full">
                            {gift.category}
                          </span>
                        </div>
                        <h3 className="text-xl font-bold text-trend-gray-800 mb-2">{gift.title}</h3>
                        <p className="text-trend-gray-600 mb-4 leading-relaxed">{gift.description}</p>
                      </div>
                      
                      {gift.image_url && (
                        <div className="ml-6">
                          <img 
                            src={gift.image_url} 
                            alt={gift.title}
                            className="w-24 h-24 object-cover rounded-lg"
                          />
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-2xl font-bold text-trend-orange-600">
                          ₩{gift.estimated_price?.toLocaleString() || '가격 정보 없음'}
                        </div>
                        <div className="flex items-center space-x-1">
                          {[...Array(5)].map((_, i) => (
                            <Star 
                              key={i} 
                              className={`h-4 w-4 ${
                                i < Math.floor(gift.confidence_score * 5) 
                                  ? 'text-yellow-400 fill-current' 
                                  : 'text-trend-gray-300'
                              }`} 
                            />
                          ))}
                          <span className="text-sm text-trend-gray-500 ml-1">
                            {(gift.confidence_score * 100).toFixed(0)}% 만족도
                          </span>
                        </div>
                      </div>
                      
                      {gift.purchase_link && (
                        <Button 
                          onClick={() => window.open(gift.purchase_link, '_blank')}
                          className="bg-trend-orange-500 hover:bg-trend-orange-600 text-white"
                        >
                          <ShoppingCart className="h-4 w-4 mr-2" />
                          구매하기
                        </Button>
                      )}
                    </div>
                    
                    {/* Reasoning */}
                    <div className="mt-4 p-4 bg-trend-gray-50 rounded-lg">
                      <h4 className="text-sm font-semibold text-trend-gray-700 mb-2">💡 추천 이유</h4>
                      <p className="text-sm text-trend-gray-600">{gift.reasoning}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Search Results */}
            {search_results && search_results.length > 0 && (
              <div className="modern-card mb-8">
                <div className="p-6">
                  <h3 className="modern-title mb-4">🔍 발견한 상품들</h3>
                  <div className="space-y-4">
                    {search_results.slice(0, 5).map((result, index) => (
                      <div key={index} className="border-b border-trend-gray-200 pb-4 last:border-b-0">
                        <h4 className="font-medium text-trend-gray-800 text-sm mb-1">
                          {result.title.length > 50 
                            ? `${result.title.substring(0, 50)}...` 
                            : result.title
                          }
                        </h4>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-trend-gray-500">{result.domain}</span>
                          <div className="flex items-center space-x-2">
                            {result.price && (
                              <span className="font-medium text-trend-orange-600">₩{result.price.toLocaleString()}</span>
                            )}
                            {result.rating && (
                              <div className="flex items-center space-x-1">
                                <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                <span className="text-trend-gray-500">{result.rating}</span>
                              </div>
                            )}
                          </div>
                        </div>
                        {result.url && (
                          <a 
                            href={result.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-xs text-trend-orange-600 hover:text-trend-orange-700 flex items-center mt-1"
                          >
                            보기 <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {/* Tips */}
            <div className="modern-card">
              <div className="p-6">
                <h3 className="modern-title mb-4">💡 선물 팁</h3>
                <div className="space-y-3 text-sm text-trend-gray-600">
                  <div className="flex items-start space-x-2">
                    <span>🎯</span>
                    <span>개인의 취향을 고려한 맞춤형 추천입니다</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span>💰</span>
                    <span>설정한 예산 범위 내의 최적 가격대입니다</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span>⭐</span>
                    <span>신뢰도가 높을수록 만족도가 높습니다</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span>🛒</span>
                    <span>실제 구매 가능한 상품들입니다</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* CTA */}
            <div className="text-center mt-8">
              <Button 
                onClick={() => router.push('/recommendations')}
                className="w-full modern-button-primary"
              >
                다른 선물도 찾아보기
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}