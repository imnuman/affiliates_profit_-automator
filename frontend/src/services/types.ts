// User types
export interface User {
  id: string
  email: string
  full_name?: string
  tier: 'starter' | 'professional' | 'agency'
  status: 'trial' | 'active' | 'suspended' | 'canceled'
  is_email_verified: boolean
  created_at: string
  trial_ends_at?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserUsage {
  content_generated: number
  content_limit: number
  campaigns_active: number
  campaigns_limit: number
  storage_used_gb: number
  storage_limit_gb: number
}

// Product types
export interface Product {
  id: string
  clickbank_id: string
  title: string
  vendor: string
  category?: string
  description?: string
  commission_rate?: number
  commission_amount?: number
  initial_sale_amount?: number
  gravity?: number
  refund_rate?: number
  rebill: boolean
  popularity_rank?: number
  last_updated?: string
  created_at: string
}

export interface ProductSearchParams {
  query?: string
  category?: string
  min_gravity?: number
  max_refund_rate?: number
  min_commission?: number
  has_rebill?: boolean
  limit?: number
  offset?: number
}

// Campaign types
export interface Campaign {
  id: string
  user_id: string
  product_id?: string
  name: string
  status: 'active' | 'paused' | 'completed' | 'draft'
  funnel_type?: string
  affiliate_link?: string
  tracking_id?: string
  settings?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface CreateCampaignData {
  name: string
  product_id?: string
  funnel_type?: string
  affiliate_link?: string
  settings?: Record<string, any>
}

// Content types
export interface Content {
  id: string
  user_id: string
  campaign_id?: string
  type: 'blog_post' | 'email' | 'social_post' | 'video_script' | 'ad_copy'
  title?: string
  body: string
  metadata?: Record<string, any>
  status: 'draft' | 'published' | 'scheduled' | 'archived'
  published_at?: string
  scheduled_for?: string
  created_at: string
  updated_at: string
}

export interface GenerateContentRequest {
  product_id: string
  content_type: string
  tone?: string
  length?: string
  additional_context?: string
}

// Analytics types
export interface DashboardMetrics {
  total_clicks: number
  total_conversions: number
  total_revenue: number
  conversion_rate: number
  average_commission: number
  active_campaigns: number
}

export interface CampaignAnalytics {
  campaign_id: string
  campaign_name: string
  clicks: number
  conversions: number
  revenue: number
  conversion_rate: number
  epc: number
}

// Workflow types
export interface Workflow {
  id: string
  user_id: string
  name: string
  trigger_type: string
  trigger_config?: Record<string, any>
  actions: Array<Record<string, any>>
  conditions?: Record<string, any>
  status: 'active' | 'paused' | 'draft'
  last_run_at?: string
  next_run_at?: string
  created_at: string
  updated_at: string
}

// API Error
export interface ApiError {
  detail: string
}
