import { SubscriptionType, ProfileVisibility, UserBadgeResponse } from './server-types';

export type UserProfileResponse = {
  id: number;
  email: string;
  username: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
  subscription_type: SubscriptionType;
  total_xp: number;
  level: number;
  challenge_streak: number;
  longest_challenge_streak: number;
  profile_image_path?: string | null;
  bio?: string | null;
  contact_info?: string | null;
  profile_visibility: ProfileVisibility;
  badges: UserBadgeResponse[];
  created_at: string;
  last_login?: string | null;
};

export type UserProfileUpdateRequest = {
  full_name?: string | null;
  profile_image_path?: string | null;
  bio?: string | null;
  contact_info?: string | null;
  profile_visibility?: ProfileVisibility | null;
};