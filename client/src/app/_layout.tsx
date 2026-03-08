import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import React, { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { Provider } from 'react-redux';

import { store } from '@/store';
import { initializeAuth } from '@/store';

function RootLayoutInner() {
  const colorScheme = useColorScheme();

  useEffect(() => {
    initializeAuth(store.dispatch);
  }, []);

  return (
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
        <Stack.Screen name="questions/index" />
        <Stack.Screen name="questions/[id]/start" />
        <Stack.Screen name="questions/[id]" />
        <Stack.Screen name="questions/[id]/session" />
        <Stack.Screen name="questions/[id]/results" />
        <Stack.Screen name="leaderboard" />
      </Stack>
    </ThemeProvider>
  );
}

export default function RootLayout() {
  return (
    <Provider store={store}>
      <RootLayoutInner />
    </Provider>
  );
}
