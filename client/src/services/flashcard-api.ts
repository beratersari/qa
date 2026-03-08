import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import {
  FlashcardResponse,
  FlashcardCreateRequest,
  FlashcardSetResponse,
  FlashcardSetCreateRequest,
  FlashcardInSetResponse,
  FlashcardSessionResponse,
  FlashcardProgressRequest,
  FlashcardProgressResponse,
} from '@/types/server-types';

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
    deleteFlashcard: builder.mutation<void, number>({
      query: (flashcardId) => ({
        url: `/flashcards/${flashcardId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Flashcards'],
    }),
    getFlashcardSets: builder.query<FlashcardSetResponse[], { scope: 'all' | 'mine' }>({
      query: ({ scope }) => ({
        url: scope === 'mine' ? '/flashcards/sets/me/created' : '/flashcards/sets',
        method: 'GET',
      }),
      providesTags: ['Flashcards'],
    }),
    getFlashcardSet: builder.query<FlashcardSetResponse, number>({
      query: (setId) => ({
        url: `/flashcards/sets/${setId}`,
        method: 'GET',
      }),
      providesTags: ['Flashcards'],
    }),
    createFlashcardSet: builder.mutation<FlashcardSetResponse, FlashcardSetCreateRequest>({
      query: (body) => ({
        url: '/flashcards/sets',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Flashcards'],
    }),
    deleteFlashcardSet: builder.mutation<void, number>({
      query: (setId) => ({
        url: `/flashcards/sets/${setId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Flashcards'],
    }),
    getFlashcardsInSet: builder.query<FlashcardInSetResponse[], number>({
      query: (setId) => ({
        url: `/flashcards/sets/${setId}/flashcards`,
        method: 'GET',
      }),
      providesTags: ['Flashcards'],
    }),
    addFlashcardToSet: builder.mutation<{ message: string }, { setId: number; flashcardId: number }>({
      query: ({ setId, flashcardId }) => ({
        url: `/flashcards/sets/${setId}/flashcards`,
        method: 'POST',
        body: { flashcard_id: flashcardId },
      }),
      invalidatesTags: ['Flashcards'],
    }),
    removeFlashcardFromSet: builder.mutation<void, { setId: number; flashcardId: number }>({
      query: ({ setId, flashcardId }) => ({
        url: `/flashcards/sets/${setId}/flashcards/${flashcardId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Flashcards'],
    }),
    deleteFlashcardFromSet: builder.mutation<void, { setId: number; flashcardId: number }>({
      query: ({ setId, flashcardId }) => ({
        url: `/flashcards/sets/${setId}/flashcards/${flashcardId}/delete`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Flashcards'],
    }),
    startFlashcardSession: builder.mutation<FlashcardSessionResponse, number>({
      query: (setId) => ({
        url: `/flashcards/sets/${setId}/sessions`,
        method: 'POST',
      }),
      invalidatesTags: ['Flashcards'],
    }),
    updateFlashcardProgress: builder.mutation<FlashcardProgressResponse, { setId: number; payload: FlashcardProgressRequest }>({
      query: ({ setId, payload }) => ({
        url: `/flashcards/sets/${setId}/progress`,
        method: 'POST',
        body: payload,
      }),
      invalidatesTags: ['Flashcards'],
    }),
    getFlashcardProgress: builder.query<FlashcardProgressResponse[], number>({
      query: (setId) => ({
        url: `/flashcards/sets/${setId}/progress`,
        method: 'GET',
      }),
      providesTags: ['Flashcards'],
    }),
  }),
});

export const {
  useGetFlashcardsQuery,
  useGetFlashcardQuery,
  useCreateFlashcardMutation,
  useDeleteFlashcardMutation,
  useGetFlashcardSetsQuery,
  useGetFlashcardSetQuery,
  useCreateFlashcardSetMutation,
  useDeleteFlashcardSetMutation,
  useGetFlashcardsInSetQuery,
  useAddFlashcardToSetMutation,
  useRemoveFlashcardFromSetMutation,
  useDeleteFlashcardFromSetMutation,
  useStartFlashcardSessionMutation,
  useUpdateFlashcardProgressMutation,
  useGetFlashcardProgressQuery,
} = flashcardApi;