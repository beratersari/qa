import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import { XpLeaderboardResponse } from '@/types/server-types';

export const leaderboardApi = createApi({
  reducerPath: 'leaderboardApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Leaderboard'],
  endpoints: (builder) => ({
    getXpLeaderboard: builder.query<XpLeaderboardResponse, void>({
      query: () => ({
        url: '/leaderboard/xp',
        method: 'GET',
      }),
      providesTags: ['Leaderboard'],
    }),
  }),
});

export const { useGetXpLeaderboardQuery } = leaderboardApi;
