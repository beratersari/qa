import AsyncStorage from '@react-native-async-storage/async-storage';

import { AuthTokens, UserProfile } from '@/types/auth';

const ACCESS_TOKEN_KEY = 'auth.accessToken';
const REFRESH_TOKEN_KEY = 'auth.refreshToken';
const TOKEN_TYPE_KEY = 'auth.tokenType';
const USER_PROFILE_KEY = 'auth.userProfile';

export async function saveTokens(tokens: AuthTokens) {
  await AsyncStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
  await AsyncStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
  await AsyncStorage.setItem(TOKEN_TYPE_KEY, tokens.tokenType);
}

export async function getTokens(): Promise<AuthTokens | null> {
  const accessToken = await AsyncStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
  const tokenType = await AsyncStorage.getItem(TOKEN_TYPE_KEY);

  if (!accessToken || !refreshToken || !tokenType) {
    return null;
  }

  return {
    accessToken,
    refreshToken,
    tokenType,
  };
}

export async function clearTokens() {
  await AsyncStorage.removeItem(ACCESS_TOKEN_KEY);
  await AsyncStorage.removeItem(REFRESH_TOKEN_KEY);
  await AsyncStorage.removeItem(TOKEN_TYPE_KEY);
}

export async function saveUserProfile(user: UserProfile) {
  await AsyncStorage.setItem(USER_PROFILE_KEY, JSON.stringify(user));
}

export async function getUserProfile(): Promise<UserProfile | null> {
  const value = await AsyncStorage.getItem(USER_PROFILE_KEY);
  if (!value) {
    return null;
  }
  return JSON.parse(value) as UserProfile;
}

export async function clearUserProfile() {
  await AsyncStorage.removeItem(USER_PROFILE_KEY);
}

export async function clearAuthStorage() {
  await Promise.all([clearTokens(), clearUserProfile()]);
}
