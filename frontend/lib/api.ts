import type { GiftRequest } from '@/types/gift'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface ProgressCallback {
  (stage: string, progress: number): void
}

export interface APIResponse {
  request_id: string
  recommendations: Array<{
    title: string
    reason: string
    estimated_price: number
    naver_product?: {
      title: string
      price: number
      image: string
      link: string
      rating?: number
      category?: string
    }
  }>
  search_results: Array<any>
  pipeline_metrics: {
    total_time: number
    ai_time: number
    search_time: number
    matching_time: number
  }
}

class GiftGenieAPI {
  async getRecommendations(request: GiftRequest, onProgress?: ProgressCallback): Promise<APIResponse> {
    try {
      // Simulate progress stages
      if (onProgress) {
        onProgress('analyzing', 20)
        
        // Small delay to show analyzing stage
        await new Promise(resolve => setTimeout(resolve, 500))
        onProgress('searching', 50)
        
        await new Promise(resolve => setTimeout(resolve, 500))
        onProgress('integrating', 80)
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/retry`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (onProgress) {
        onProgress('complete', 100)
      }

      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  async checkHealth(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`)
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Health check error:', error)
      throw error
    }
  }
}

export const giftGenieAPI = new GiftGenieAPI()