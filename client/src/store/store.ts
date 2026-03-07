import { configureStore } from '@reduxjs/toolkit';

import authReducer from './auth-slice';
import { authApi } from '@/services/auth-api';
import { userApi } from '@/services/user-api';
import { subscriptionApi } from '@/services/subscription-api';
import { flashcardApi } from '@/services/flashcard-api';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [authApi.reducerPath]: authApi.reducer,
    [userApi.reducerPath]: userApi.reducer,
    [subscriptionApi.reducerPath]: subscriptionApi.reducer,
    [flashcardApi.reducerPath]: flashcardApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }).concat(
      authApi.middleware,
      userApi.middleware,
      subscriptionApi.middleware,
      flashcardApi.middleware
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;