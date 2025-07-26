"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { useGiftGenieStore } from '@/lib/store'
import { Sparkles } from 'lucide-react'

export function GiftRecommendationForm() {
  const { formProgress, setCurrentStep } = useGiftGenieStore()

  return (
    <div className="modern-bg min-h-screen">
      {/* Centered Header with more whitespace */}
      <div className="relative pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <h1 className="modern-display mb-6">
            맞춤형 선물을<br/>
            <span className="text-trend-orange-500">찾아드릴게요</span>
          </h1>
          <p className="modern-subtitle mb-12 max-w-2xl mx-auto">
            단 5가지 질문으로 완벽한 선물을 추천받으세요
          </p>
          
          {/* Minimal Progress Indicator */}
          <div className="mb-12 max-w-md mx-auto">
            <div className="flex justify-center items-center mb-3">
              <span className="text-sm font-medium text-trend-gray-500">
                {formProgress.currentStep + 1} / {formProgress.totalSteps}
              </span>
            </div>
            <div className="modern-progress-bar">
              <div 
                className="modern-progress-bar-fill"
                style={{ 
                  width: `${((formProgress.currentStep + 1) / formProgress.totalSteps) * 100}%` 
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Centered Form Content with generous whitespace */}
      <div className="max-w-3xl mx-auto px-8 pb-24">
        <div className="modern-card-elevated">
          <div className="text-center py-20 px-8">
            <div className="inline-block p-8 bg-trend-orange-50 rounded-modern mb-8">
              <Sparkles className="h-16 w-16 text-trend-orange-500 mx-auto" />
            </div>
            <h3 className="modern-title mb-6">
              지금 준비 중이에요
            </h3>
            <p className="modern-subtitle mb-12 max-w-lg mx-auto">
              5단계 질문이 곧 준비될 예정입니다
            </p>
          </div>
        </div>
        
        {/* Centered Navigation */}
        <div className="flex justify-center items-center space-x-8 mt-12">
          <button 
            className={`modern-button-primary ${
              formProgress.currentStep === 0 
                ? 'opacity-50 cursor-not-allowed' 
                : ''
            }`}
            onClick={() => setCurrentStep(Math.max(0, formProgress.currentStep - 1))}
            disabled={formProgress.currentStep === 0}
          >
            ← 이전
          </button>
          
          <div className="text-center px-6">
            <div className="text-sm text-trend-gray-500">준비 중...</div>
          </div>
          
          <button 
            className={`modern-button-primary ${
              formProgress.currentStep === formProgress.totalSteps - 1 
                ? 'opacity-50 cursor-not-allowed' 
                : ''
            }`}
            onClick={() => setCurrentStep(Math.min(formProgress.totalSteps - 1, formProgress.currentStep + 1))}
            disabled={formProgress.currentStep === formProgress.totalSteps - 1}
          >
            다음 →
          </button>
        </div>
      </div>
    </div>
  )
}