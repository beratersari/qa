import { AppDispatch } from './store';
import { clearAuth, setAuth, setTokens, setUser, setThemeOverrides } from './auth-slice';

import { authApi } from '@/services/auth-api';
import { AuthResponse, AuthTokens, UserProfile } from '@/types/auth';
import {
  clearAuthStorage,
  getTokens,
  getUserProfile,
  saveTokens,
  saveUserProfile,
} from '@/utils/token-storage';

export async function initializeAuth(dispatch: AppDispatch) {
  const [tokens, user] = await Promise.all([getTokens(), getUserProfile()]);

  if (tokens && user) {
    dispatch(setTokens(tokens));
    dispatch(setUser(user));
    dispatch(setThemeOverrides(user.themeOverrides ?? null));
  }
}

export async function persistAuth(dispatch: AppDispatch, auth: AuthResponse) {
  const tokens: AuthTokens = {
    accessToken: auth.access_token,
    refreshToken: auth.refresh_token,
    tokenType: auth.token_type,
  };

  dispatch(setAuth(auth));
  dispatch(setThemeOverrides(auth.user.themeOverrides ?? null));
  await Promise.all([saveTokens(tokens), saveUserProfile(auth.user)]);
}

export async function persistTokens(dispatch: AppDispatch, tokens: AuthTokens) {
  dispatch(setTokens(tokens));
  await saveTokens(tokens);
}

export async function logoutUser(dispatch: AppDispatch) {
  dispatch(clearAuth());
  dispatch(authApi.util.resetApiState());
  await clearAuthStorage();
}
