export type AuthTokens = {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
};

export type ThemeOverrides = Partial<{
  text: string;
  background: string;
  backgroundElement: string;
  backgroundSelected: string;
  textSecondary: string;
  inputBackground: string;
  inputBorder: string;
  inputBorderFocused: string;
  inputBorderError: string;
  inputPlaceholder: string;
  error: string;
  primary: string;
  primaryHover: string;
  buttonDisabled: string;
}>;

export type UserProfile = {
  id: number;
  email: string;
  username: string;
  role: string;
  themeOverrides?: ThemeOverrides | null;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserProfile;
};

export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  username: string;
  password: string;
  full_name?: string | null;
};
