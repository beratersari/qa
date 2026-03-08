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

export type FlashcardSetResponse = {
  id: number;
  name: string;
  description?: string | null;
  flashcard_count: number;
  created_by?: number | null;
  created_at: string;
  updated_at: string;
};

export type FlashcardSetCreateRequest = {
  name: string;
  description?: string | null;
};

export type FlashcardInSetResponse = {
  id: number;
  word_front: string;
  word_back: string;
  example_sentences: string[];
  set_id: number;
  created_by?: number | null;
  created_at: string;
  updated_at: string;
};

export type FlashcardSessionResponse = {
  id: number;
  user_id: number;
  set_id: number;
  started_at: string;
};

export type FlashcardProgressRequest = {
  flashcard_id: number;
  status: 'known' | 'unknown';
};

export type FlashcardProgressResponse = {
  id: number;
  user_id: number;
  set_id: number;
  flashcard_id: number;
  status: 'known' | 'unknown';
  updated_at: string;
};

// Question Set Types
export type QuestionSetType = 'normal' | 'premium';

export type QuestionSetResponse = {
  id: number;
  name: string;
  description?: string | null;
  set_type: QuestionSetType;
  question_count: number;
  created_by?: number | null;
  created_at: string;
  updated_at: string;
};

export type QuestionChoice = {
  letter: string;
  text: string;
};

export type QuestionInSetResponse = {
  id: number;
  prompt: string;
  choices: QuestionChoice[];
  difficulty_level: number;
  set_id: number;
  question_id: number;
};

export type QuestionAnswerResponse = {
  id: number;
  answer_letter: string;
  answer_text: string;
};

export type XpLeaderboardEntry = {
  rank: number;
  display_name: string;
  total_xp: number;
  challenge_streak: number;
  user_id?: number | null;
};

export type XpLeaderboardResponse = {
  entries: XpLeaderboardEntry[];
  current_user_rank?: number | null;
};
