"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { giftGenieAPI } from '@/lib/api'
import { Sparkles, Heart, Gift, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import type { GiftRequest, LoadingState } from '@/types/gift'
import { RELATIONSHIP_OPTIONS, GENDER_OPTIONS, OCCASION_OPTIONS, INTEREST_OPTIONS, PERSONAL_STYLE_OPTIONS } from '@/types/gift'

export function GiftRecommendationForm() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<Partial<GiftRequest>>({
    recipient_age: 25,
    recipient_gender: '여성',
    relationship: '친구',
    budget_min: 50,
    budget_max: 150,
    interests: [],
    occasion: '생일',
    personal_style: '미니멀리스트',
    restrictions: []
  })
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: false,
    stage: 'idle',
    progress: 0,
    message: ''
  })

  const totalSteps = 5

  const updateFormData = (updates: Partial<GiftRequest>) => {
    setFormData(prev => ({ ...prev, ...updates }))
  }

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.recipient_age || !formData.recipient_gender || !formData.relationship || 
        !formData.budget_min || !formData.budget_max || !formData.interests?.length || !formData.occasion) {
      alert('모든 필수 정보를 입력해주세요.')
      return
    }

    const request: GiftRequest = {
      recipient_age: formData.recipient_age!,
      recipient_gender: formData.recipient_gender!,
      relationship: formData.relationship!,
      budget_min: formData.budget_min!,
      budget_max: formData.budget_max!,
      interests: formData.interests!,
      occasion: formData.occasion!,
      personal_style: formData.personal_style,
      restrictions: formData.restrictions
    }

    setLoadingState({
      isLoading: true,
      stage: 'analyzing',
      progress: 0,
      message: 'AI가 선물을 분석하고 있어요...'
    })

    try {
      const response = await giftGenieAPI.getRecommendations(request, (stage, progress) => {
        const stageMessages: Record<string, string> = {
          'analyzing': 'AI가 선물을 분석하고 있어요...',
          'searching': '네이버쇼핑에서 상품을 검색하고 있어요...',
          'integrating': '최적의 추천을 준비하고 있어요...',
          'complete': '완료!'
        }

        setLoadingState({
          isLoading: true,
          stage: stage as any,
          progress,
          message: stageMessages[stage] || '처리 중...'
        })
      })

      // Store results and navigate to results page
      sessionStorage.setItem('giftRecommendations', JSON.stringify(response))
      router.push('/result')
    } catch (error) {
      console.error('추천 생성 실패:', error)
      setLoadingState({
        isLoading: false,
        stage: 'idle',
        progress: 0,
        message: ''
      })
      alert('추천 생성에 실패했습니다. 다시 시도해주세요.')
    }
  }

  // Loading screen
  if (loadingState.isLoading) {
    return (
      <div className="modern-bg min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-8">
          <div className="mb-8">
            <Loader2 className="h-16 w-16 text-trend-orange-500 mx-auto animate-spin" />
          </div>
          <h2 className="modern-title mb-4">선물을 찾고 있어요</h2>
          <p className="modern-subtitle mb-8">{loadingState.message}</p>
          
          <div className="w-full bg-trend-gray-200 rounded-full h-3 mb-4">
            <div 
              className="bg-trend-orange-500 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${loadingState.progress}%` }}
            />
          </div>
          <div className="text-sm text-trend-gray-500">{loadingState.progress}%</div>
        </div>
      </div>
    )
  }

  return (
    <div className="modern-bg min-h-screen">
      {/* Header */}
      <div className="relative pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <h1 className="modern-display mb-6">
            맞춤형 선물을<br/>
            <span className="text-trend-orange-500">찾아드릴게요</span>
          </h1>
          <p className="modern-subtitle mb-12 max-w-2xl mx-auto">
            단 5가지 질문으로 완벽한 선물을 추천받으세요
          </p>
          
          {/* Progress Indicator */}
          <div className="mb-12 max-w-md mx-auto">
            <div className="flex justify-center items-center mb-3">
              <span className="text-sm font-medium text-trend-gray-500">
                {currentStep + 1} / {totalSteps}
              </span>
            </div>
            <div className="modern-progress-bar">
              <div 
                className="modern-progress-bar-fill transition-all duration-300"
                style={{ 
                  width: `${((currentStep + 1) / totalSteps) * 100}%` 
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="max-w-3xl mx-auto px-8 pb-24">
        <div className="modern-card-elevated">
          {renderStep()}
        </div>
        
        {/* Navigation */}
        <div className="flex justify-center items-center space-x-8 mt-12">
          <button 
            className={`modern-button-primary ${
              currentStep === 0 
                ? 'opacity-50 cursor-not-allowed' 
                : ''
            }`}
            onClick={handlePrev}
            disabled={currentStep === 0}
          >
            ← 이전
          </button>
          
          <div className="text-center px-6">
            <div className="text-sm text-trend-gray-500">
              {currentStep === totalSteps - 1 ? '선물 찾기 준비 완료!' : `단계 ${currentStep + 1}/${totalSteps}`}
            </div>
          </div>
          
          {currentStep === totalSteps - 1 ? (
            <button 
              className="modern-button-primary bg-trend-orange-500 hover:bg-trend-orange-600"
              onClick={handleSubmit}
            >
              <Gift className="w-4 h-4 mr-2" />
              선물 찾기
            </button>
          ) : (
            <button 
              className="modern-button-primary"
              onClick={handleNext}
            >
              다음 →
            </button>
          )}
        </div>
      </div>
    </div>
  )

  function renderStep() {
    switch (currentStep) {
      case 0:
        return (
          <div className="p-8">
            <div className="text-center mb-8">
              <Heart className="h-12 w-12 text-trend-orange-500 mx-auto mb-4" />
              <h3 className="modern-title mb-2">선물받을 분은 어떤 분인가요?</h3>
              <p className="modern-subtitle">받는 분의 기본 정보를 알려주세요</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">나이</label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={formData.recipient_age || ''}
                  onChange={(e) => updateFormData({ recipient_age: parseInt(e.target.value) || 25 })}
                  className="w-full px-4 py-3 border border-trend-gray-300 rounded-lg focus:ring-2 focus:ring-trend-orange-500 focus:border-transparent"
                  placeholder="나이를 입력하세요"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">성별</label>
                <div className="grid grid-cols-3 gap-3">
                  {GENDER_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`p-3 rounded-lg border-2 transition-all ${
                        formData.recipient_gender === option.value
                          ? 'border-trend-orange-500 bg-trend-orange-50 text-trend-orange-700'
                          : 'border-trend-gray-300 hover:border-trend-orange-300'
                      }`}
                      onClick={() => updateFormData({ recipient_gender: option.value })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">관계</label>
                <div className="grid grid-cols-2 gap-3">
                  {RELATIONSHIP_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`p-3 rounded-lg border-2 transition-all ${
                        formData.relationship === option.value
                          ? 'border-trend-orange-500 bg-trend-orange-50 text-trend-orange-700'
                          : 'border-trend-gray-300 hover:border-trend-orange-300'
                      }`}
                      onClick={() => updateFormData({ relationship: option.value })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )
        
      case 1:
        return (
          <div className="p-8">
            <div className="text-center mb-8">
              <Sparkles className="h-12 w-12 text-trend-orange-500 mx-auto mb-4" />
              <h3 className="modern-title mb-2">어떤 관심사를 가지고 계신가요?</h3>
              <p className="modern-subtitle">최대 5개까지 선택해주세요</p>
            </div>
            
            <div className="grid grid-cols-3 gap-3">
              {INTEREST_OPTIONS.map((option) => {
                const isSelected = formData.interests?.includes(option.value) || false
                return (
                  <button
                    key={option.value}
                    type="button"
                    className={`p-3 rounded-lg border-2 transition-all text-sm ${
                      isSelected
                        ? 'border-trend-orange-500 bg-trend-orange-50 text-trend-orange-700'
                        : 'border-trend-gray-300 hover:border-trend-orange-300'
                    }`}
                    onClick={() => {
                      const currentInterests = formData.interests || []
                      if (isSelected) {
                        updateFormData({ 
                          interests: currentInterests.filter(i => i !== option.value) 
                        })
                      } else if (currentInterests.length < 5) {
                        updateFormData({ 
                          interests: [...currentInterests, option.value] 
                        })
                      }
                    }}
                  >
                    {option.label}
                  </button>
                )
              })}
            </div>
            
            <div className="text-center mt-4 text-sm text-trend-gray-500">
              선택된 관심사: {formData.interests?.length || 0}/5
            </div>
          </div>
        )
        
      case 2:
        return (
          <div className="p-8">
            <div className="text-center mb-8">
              <Gift className="h-12 w-12 text-trend-orange-500 mx-auto mb-4" />
              <h3 className="modern-title mb-2">어떤 행사를 위한 선물인가요?</h3>
              <p className="modern-subtitle">행사에 맞는 선물을 추천해드릴게요</p>
            </div>
            
            <div className="grid grid-cols-3 gap-3">
              {OCCASION_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.occasion === option.value
                      ? 'border-trend-orange-500 bg-trend-orange-50 text-trend-orange-700'
                      : 'border-trend-gray-300 hover:border-trend-orange-300'
                  }`}
                  onClick={() => updateFormData({ occasion: option.value })}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )
        
      case 3:
        return (
          <div className="p-8">
            <div className="text-center mb-8">
              <span className="text-4xl mb-4 block">💰</span>
              <h3 className="modern-title mb-2">예산은 어느 정도 생각하고 계신가요?</h3>
              <p className="modern-subtitle">USD 기준으로 입력해주세요</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">
                  최소 예산: ${formData.budget_min || 0}
                </label>
                <input
                  type="range"
                  min="10"
                  max="500"
                  step="10"
                  value={formData.budget_min || 50}
                  onChange={(e) => updateFormData({ budget_min: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">
                  최대 예산: ${formData.budget_max || 0}
                </label>
                <input
                  type="range"
                  min={formData.budget_min || 50}
                  max="1000"
                  step="10"
                  value={formData.budget_max || 150}
                  onChange={(e) => updateFormData({ budget_max: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div className="text-center p-4 bg-trend-gray-50 rounded-lg">
                <div className="text-lg font-semibold text-trend-gray-800">
                  ${formData.budget_min || 0} - ${formData.budget_max || 0}
                </div>
                <div className="text-sm text-trend-gray-600 mt-1">
                  대략 {((formData.budget_min || 0) * 1300).toLocaleString()}원 - {((formData.budget_max || 0) * 1300).toLocaleString()}원
                </div>
              </div>
            </div>
          </div>
        )
        
      case 4:
        return (
          <div className="p-8">
            <div className="text-center mb-8">
              <span className="text-4xl mb-4 block">✨</span>
              <h3 className="modern-title mb-2">마지막으로, 추가 정보가 있나요?</h3>
              <p className="modern-subtitle">더 정확한 추천을 위한 선택사항입니다</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">선호하는 스타일</label>
                <div className="grid grid-cols-2 gap-3">
                  {PERSONAL_STYLE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`p-3 rounded-lg border-2 transition-all ${
                        formData.personal_style === option.value
                          ? 'border-trend-orange-500 bg-trend-orange-50 text-trend-orange-700'
                          : 'border-trend-gray-300 hover:border-trend-orange-300'
                      }`}
                      onClick={() => updateFormData({ personal_style: option.value })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-trend-gray-700 mb-2">피하고 싶은 것들 (선택사항)</label>
                <textarea
                  value={formData.restrictions?.join(', ') || ''}
                  onChange={(e) => {
                    const restrictions = e.target.value.split(',').map(r => r.trim()).filter(r => r)
                    updateFormData({ restrictions })
                  }}
                  className="w-full px-4 py-3 border border-trend-gray-300 rounded-lg focus:ring-2 focus:ring-trend-orange-500 focus:border-transparent"
                  placeholder="예: 향수, 쥬얼리, 전자제품 (쉼표로 구분)"
                  rows={3}
                />
              </div>
              
              {/* Summary */}
              <div className="bg-trend-orange-50 p-6 rounded-lg">
                <h4 className="font-semibold text-trend-orange-800 mb-3">입력 정보 요약</h4>
                <div className="text-sm text-trend-orange-700 space-y-1">
                  <div>👤 {formData.recipient_age}세 {formData.recipient_gender} ({formData.relationship})</div>
                  <div>🎯 관심사: {formData.interests?.join(', ') || '없음'}</div>
                  <div>🎉 행사: {formData.occasion}</div>
                  <div>💰 예산: ${formData.budget_min}-{formData.budget_max}</div>
                  <div>✨ 스타일: {formData.personal_style || '지정 안함'}</div>
                </div>
              </div>
            </div>
          </div>
        )
        
      default:
        return null
    }
  }
}