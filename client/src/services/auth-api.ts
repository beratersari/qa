import { createApi } from '@reduxjs/toolkit/query/react';

import { AuthResponse, LoginRequest, RegisterRequest, UserProfile } from '@/types/auth';
import { baseQueryWithReauth } from './base-query';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (body) => ({
        url: '/auth/login',
        method: 'POST',
        body: new URLSearchParams({
          username: body.username,
          password: body.password,
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
    }),
    register: builder.mutation<UserProfile, RegisterRequest>({
      query: (body) => ({
        url: '/auth/register',
        method: 'POST',
        body,
      }),
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
    }),
  }),
});

export const { useLoginMutation, useRegisterMutation, useLogoutMutation } = authApi;