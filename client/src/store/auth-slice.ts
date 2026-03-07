import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { AuthResponse, AuthTokens, UserProfile } from '@/types/auth';

export type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  tokenType: string | null;
  user: UserProfile | null;
  themeOverrides: UserProfile['themeOverrides'];
};

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  tokenType: null,
  user: null,
  themeOverrides: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuth: (state, action: PayloadAction<AuthResponse>) => {
      state.accessToken = action.payload.access_token;
      state.refreshToken = action.payload.refresh_token;
      state.tokenType = action.payload.token_type;
      state.user = action.payload.user;
      state.themeOverrides = action.payload.user.themeOverrides ?? null;
    },
    setTokens: (state, action: PayloadAction<AuthTokens>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.tokenType = action.payload.tokenType;
    },
    setUser: (state, action: PayloadAction<UserProfile | null>) => {
      state.user = action.payload;
      state.themeOverrides = action.payload?.themeOverrides ?? null;
    },
    setThemeOverrides: (state, action: PayloadAction<UserProfile['themeOverrides']>) => {
      state.themeOverrides = action.payload ?? null;
    },
    clearAuth: (state) => {
      state.accessToken = null;
      state.refreshToken = null;
      state.tokenType = null;
      state.user = null;
      state.themeOverrides = null;
    },
  },
});

export const { setAuth, setTokens, setUser, setThemeOverrides, clearAuth } = authSlice.actions;

export default authSlice.reducer;