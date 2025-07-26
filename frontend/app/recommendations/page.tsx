import { Metadata } from 'next'
import { GiftRecommendationForm } from '@/components/forms/gift-recommendation-form'

export const metadata: Metadata = {
  title: '선물 추천 받기 - Gift Genie',
  description: '몇 가지 간단한 질문에 답하고 완벽한 선물 추천을 받아보세요.',
}

export default function RecommendationsPage() {
  return (
    <GiftRecommendationForm />
  )
}