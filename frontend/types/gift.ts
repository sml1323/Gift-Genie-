// Gift Genie Frontend Types
// Based on the backend AI recommendation engine structure

export interface GiftRequest {
  recipient_age: number
  recipient_gender: string
  relationship: string // 'friend', 'family', 'colleague', 'partner'
  budget_min: number
  budget_max: number
  currency: 'USD' | 'KRW'
  interests: string[]
  occasion: string // 'birthday', 'christmas', 'anniversary', etc.
  personal_style?: string
  restrictions?: string[] // allergies, preferences, etc.
}

export interface GiftRecommendation {
  title: string
  description: string
  category: string
  estimated_price: number
  currency?: 'USD' | 'KRW'
  price_display?: string
  reasoning: string
  purchase_link?: string
  image_url?: string
  confidence_score: number
}

export interface ProductSearchResult {
  title: string
  url: string
  description: string
  domain: string
  price?: number
  image_url?: string
  rating?: number
  review_count?: number
}

export interface MCPPipelineMetrics {
  ai_generation_time: number
  search_execution_time: number
  scraping_execution_time: number
  integration_time: number
  total_time: number
  search_results_count: number
  product_details_count: number
  cache_simulation: boolean
}

export interface EnhancedRecommendationResponse {
  request_id: string
  recommendations: GiftRecommendation[]
  search_results: ProductSearchResult[]
  pipeline_metrics: MCPPipelineMetrics
  total_processing_time: number
  created_at: string
  success: boolean
  mcp_enabled: boolean
  simulation_mode: boolean
  error_message?: string
}

// Frontend-specific types
export interface FormSteps {
  recipient: {
    age: number
    gender: string
    relationship: string
  }
  preferences: {
    interests: string[]
    personal_style: string
  }
  occasion: {
    event: string
    date?: Date
  }
  budget: {
    min: number
    max: number
    currency: 'USD' | 'KRW'
  }
  restrictions: {
    items: string[]
    notes?: string
  }
}

export interface FormProgress {
  currentStep: number
  totalSteps: number
  completedSteps: boolean[]
  isValid: boolean
}

export interface LoadingState {
  isLoading: boolean
  stage: 'idle' | 'analyzing' | 'searching' | 'scraping' | 'integrating' | 'complete'
  progress: number
  message: string
}

export interface ApiError {
  message: string
  code?: string
  details?: unknown
}

// Constants
export const RELATIONSHIP_OPTIONS = [
  { value: 'partner', label: '연인/배우자' },
  { value: 'family', label: '가족' },
  { value: 'friend', label: '친구' },
  { value: 'colleague', label: '동료' },
  { value: 'acquaintance', label: '지인' },
] as const

export const GENDER_OPTIONS = [
  { value: '남성', label: '남성' },
  { value: '여성', label: '여성' },
  { value: '기타', label: '기타' },
] as const

export const OCCASION_OPTIONS = [
  { value: '생일', label: '생일' },
  { value: '크리스마스', label: '크리스마스' },
  { value: '기념일', label: '기념일' },
  { value: '졸업', label: '졸업' },
  { value: '승진', label: '승진' },
  { value: '결혼', label: '결혼' },
  { value: '출산', label: '출산' },
  { value: '새집', label: '새집 이사' },
  { value: '기타', label: '기타' },
] as const

export const INTEREST_OPTIONS = [
  { value: '독서', label: '독서' },
  { value: '커피', label: '커피' },
  { value: '여행', label: '여행' },
  { value: '사진', label: '사진' },
  { value: '음악', label: '음악' },
  { value: '운동', label: '운동' },
  { value: '요리', label: '요리' },
  { value: '게임', label: '게임' },
  { value: '패션', label: '패션' },
  { value: '미술', label: '미술' },
  { value: '기술', label: '기술' },
  { value: '영화', label: '영화' },
  { value: '반려동물', label: '반려동물' },
  { value: '원예', label: '원예' },
  { value: '수공예', label: '수공예' },
] as const

export const PERSONAL_STYLE_OPTIONS = [
  { value: '미니멀리스트', label: '미니멀리스트' },
  { value: '클래식', label: '클래식' },
  { value: '모던', label: '모던' },
  { value: '빈티지', label: '빈티지' },
  { value: '보헤미안', label: '보헤미안' },
  { value: '스포티', label: '스포티' },
  { value: '럭셔리', label: '럭셔리' },
  { value: '캐주얼', label: '캐주얼' },
] as const