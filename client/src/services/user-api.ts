import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import { UserProfileResponse, UserProfileUpdateRequest } from '@/types/profile';

export const userApi = createApi({
  reducerPath: 'userApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Profile'],
  endpoints: (builder) => ({
    getMyProfile: builder.query<UserProfileResponse, void>({
      query: () => ({
        url: '/users/me',
        method: 'GET',
      }),
      providesTags: ['Profile'],
    }),
    getUserById: builder.query<UserProfileResponse, number>({
      query: (id) => ({
        url: `/users/${id}`,
        method: 'GET',
      }),
    }),
    updateMyProfile: builder.mutation<UserProfileResponse, UserProfileUpdateRequest>({
      query: (body) => ({
        url: '/users/me/profile',
        method: 'PUT',
        body,
      }),
      invalidatesTags: ['Profile'],
    }),
  }),
});

export const {
  useGetMyProfileQuery,
  useGetUserByIdQuery,
  useUpdateMyProfileMutation,
} = userApi;