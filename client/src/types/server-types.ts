export type SubscriptionType = 'free' | 'premium';

export type ProfileVisibility = 'public' | 'private';

export type BadgeResponse = {
  id: number;
  name: string;
  description: string;
  icon_path?: string | null;
  conditions: Record<string, unknown>[];
  created_at: string;
  updated_at: string;
};

export type UserBadgeResponse = {
  id: number;
  user_id: number;
  badge: BadgeResponse;
  current_progress: number;
  is_completed: boolean;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type SubscriptionStatus = 'active' | 'cancelled' | 'expired' | 'pending';

export type SubscriptionPlan = 'monthly' | 'yearly';

export type SubscriptionResponse = {
  id: number;
  user_id: number;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  start_date: string;
  end_date: string;
  auto_renew: boolean;
  created_at: string;
  cancelled_at?: string | null;
};

export type SubscriptionPlanResponse = {
  name: SubscriptionPlan;
  label: string;
  description: string;
  price_cents: number;
  interval: string;
};

export type FlashcardResponse = {
  id: number;
  word_front: string;
  word_back: string;
  example_sentences: string[];
  created_by?: number | null;
  created_at: string;
  updated_at: string;
};

export type FlashcardCreateRequest = {
  word_front: string;
  word_back: string;
  example_sentences?: string[];
};
