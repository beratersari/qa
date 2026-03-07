import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@/services/base-query';
import {
  SubscriptionResponse,
  SubscriptionPlan,
  SubscriptionPlanResponse,
} from '@/types/server-types';

export const subscriptionApi = createApi({
  reducerPath: 'subscriptionApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Subscription', 'Plans'],
  endpoints: (builder) => ({
    getMySubscription: builder.query<SubscriptionResponse, void>({
      query: () => ({
        url: '/subscriptions/my-subscription',
        method: 'GET',
      }),
      providesTags: ['Subscription'],
    }),
    getActiveSubscriptions: builder.query<SubscriptionResponse[], void>({
      query: () => ({
        url: '/subscriptions/status/active',
        method: 'GET',
      }),
      providesTags: ['Subscription'],
    }),
    getSubscriptionPlans: builder.query<SubscriptionPlanResponse[], void>({
      query: () => ({
        url: '/subscriptions/plans',
        method: 'GET',
      }),
      providesTags: ['Plans'],
    }),
    subscribe: builder.mutation<SubscriptionResponse, SubscriptionPlan>({
      query: (plan) => ({
        url: '/subscriptions/subscribe',
        method: 'POST',
        params: { plan },
      }),
      invalidatesTags: ['Subscription'],
    }),
    cancelSubscription: builder.mutation<SubscriptionResponse, number>({
      query: (subscriptionId) => ({
        url: `/subscriptions/${subscriptionId}/cancel`,
        method: 'POST',
      }),
      invalidatesTags: ['Subscription'],
    }),
    renewSubscription: builder.mutation<SubscriptionResponse, number>({
      query: (subscriptionId) => ({
        url: `/subscriptions/${subscriptionId}/renew`,
        method: 'POST',
      }),
      invalidatesTags: ['Subscription'],
    }),
  }),
});

export const {
  useGetMySubscriptionQuery,
  useGetActiveSubscriptionsQuery,
  useGetSubscriptionPlansQuery,
  useSubscribeMutation,
  useCancelSubscriptionMutation,
  useRenewSubscriptionMutation,
} = subscriptionApi;