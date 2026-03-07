import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import React, { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { Provider } from 'react-redux';

import { store } from '@/store';
import { initializeAuth } from '@/store';

export default function RootLayout() {
  const colorScheme = useColorScheme();

  useEffect(() => {
    initializeAuth(store.dispatch);
  }, []);

  return (
    <Provider store={store}>
      <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="login" />
          <Stack.Screen name="register" />
          <Stack.Screen name="index" />
          <Stack.Screen name="profile" />
          <Stack.Screen name="profile/edit" />
          <Stack.Screen name="profile/subscription" />
          <Stack.Screen name="flashcards/index" />
          <Stack.Screen name="flashcards/create" />
          <Stack.Screen name="flashcards/[id]" />
          <Stack.Screen name="flashcards/[id]/session" />
          <Stack.Screen name="flashcards/[id]/results" />
        </Stack>
      </ThemeProvider>
    </Provider>
  );
}
