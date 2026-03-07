import { fetchBaseQuery, BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';

import type { RootState, AppDispatch } from '@/store';
import { persistAuth, logoutUser } from '@/store';
import { AuthResponse } from '@/types/auth';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;
    if (state.auth.accessToken) {
      headers.set('authorization', `Bearer ${state.auth.accessToken}`);
    }
    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  const normalizedArgs: typeof args =
    typeof args === 'string'
      ? `${API_PREFIX}${args}`
      : args.url.startsWith(API_PREFIX)
        ? args
        : { ...args, url: `${API_PREFIX}${args.url}` };

  let result = await rawBaseQuery(normalizedArgs, api, extraOptions);

  if (result.error && result.error.status === 401) {
    await logoutUser(api.dispatch as AppDispatch);
  }

  return result;
};
