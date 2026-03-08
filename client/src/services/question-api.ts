import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import {
  QuestionSetResponse,
  QuestionInSetResponse,
  QuestionAnswerResponse,
} from '@/types/server-types';

export const questionApi = createApi({
  reducerPath: 'questionApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Questions'],
  endpoints: (builder) => ({
    getQuestionSets: builder.query<QuestionSetResponse[], void>({
      query: () => ({
        url: '/question-sets',
        method: 'GET',
      }),
      providesTags: ['Questions'],
    }),
    getQuestionSet: builder.query<QuestionSetResponse, number>({
      query: (setId) => ({
        url: `/question-sets/${setId}`,
        method: 'GET',
      }),
      providesTags: ['Questions'],
    }),
    getQuestionsInSet: builder.query<QuestionInSetResponse[], number>({
      query: (setId) => ({
        url: `/question-sets/${setId}/questions`,
        method: 'GET',
      }),
      providesTags: ['Questions'],
    }),
    getQuestionAnswer: builder.query<QuestionAnswerResponse, number>({
      query: (questionId) => ({
        url: `/questions/${questionId}/answer`,
        method: 'GET',
      }),
    }),
  }),
});

export const {
  useGetQuestionSetsQuery,
  useGetQuestionSetQuery,
  useGetQuestionsInSetQuery,
  useGetQuestionAnswerQuery,
  useLazyGetQuestionAnswerQuery,
} = questionApi;
