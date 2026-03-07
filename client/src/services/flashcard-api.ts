import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import { FlashcardResponse, FlashcardCreateRequest } from '@/types/server-types';

export const flashcardApi = createApi({
  reducerPath: 'flashcardApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Flashcards'],
  endpoints: (builder) => ({
    getFlashcards: builder.query<FlashcardResponse[], { scope: 'all' | 'mine' }>({
      query: ({ scope }) => ({
        url: scope === 'mine' ? '/flashcards/me/created' : '/flashcards',
        method: 'GET',
      }),
      providesTags: ['Flashcards'],
    }),
    getFlashcard: builder.query<FlashcardResponse, number>({
      query: (flashcardId) => ({
        url: `/flashcards/${flashcardId}`,
        method: 'GET',
      }),
    }),
    createFlashcard: builder.mutation<FlashcardResponse, FlashcardCreateRequest>({
      query: (body) => ({
        url: '/flashcards',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Flashcards'],
    }),
  }),
});

export const {
  useGetFlashcardsQuery,
  useGetFlashcardQuery,
  useCreateFlashcardMutation,
} = flashcardApi;