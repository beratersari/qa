import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, View, StyleSheet, TouchableOpacity } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Button, Avatar, ServerError } from '@/components/atoms';
import { useGetFlashcardSetsQuery } from '@/services/flashcard-api';
import { FlashcardSetResponse } from '@/types/server-types';
import { useAppDispatch, useAppSelector, logoutUser } from '@/store';
import { Spacing } from '@/constants/theme';

function getMonogram(name: string) {
  const parts = name.split(' ').filter(Boolean);
  if (parts.length === 0) return '';
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export default function DashboardScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  if (!user) {
    router.replace('/login');
    return null;
  }

  const displayName = user.username || user.email;
  const { data: flashcardSets = [], isError } = useGetFlashcardSetsQuery({ scope: 'all' });

  const handleLogout = async () => {
    await logoutUser(dispatch);
    router.replace('/login');
  };

  const renderSet = (set: FlashcardSetResponse) => (
    <TouchableOpacity
      key={set.id}
      style={styles.card}
      onPress={() => router.push(`/flashcards/${set.id}`)}
    >
      <ThemedText type="smallBold">{set.name}</ThemedText>
      {set.description && (
        <ThemedText type="small" themeColor="textSecondary">
          {set.description}
        </ThemedText>
      )}
      <ThemedText type="small" themeColor="textSecondary">
        {set.flashcard_count} cards
      </ThemedText>
    </TouchableOpacity>
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.push('/profile')}>
            <Avatar monogram={getMonogram(displayName)} />
          </TouchableOpacity>
          <Button title="Logout" variant="outline" size="small" onPress={handleLogout} />
        </View>

        <ScrollView contentContainerStyle={styles.content}>
          <ThemedText type="subtitle">Hello {displayName}</ThemedText>
          <Button title="View Profile" onPress={() => router.push('/profile')} />
          <Button title="Flashcards" onPress={() => router.push('/flashcards')} />
          <Button title="Questions" onPress={() => router.push('/questions')} />

          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">Flashcard Sets</ThemedText>
          </View>
          {isError && (
            <ServerError message="Unable to load flashcard sets." />
          )}
          <View style={styles.list}>
            {flashcardSets.map(renderSet)}
          </View>
        </ScrollView>

        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/')}
          >
            <ThemedText type="smallBold" themeColor="primary">Dashboard</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/leaderboard')}>
            <ThemedText type="small">Leaderboard</ThemedText>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: Spacing.four,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: Spacing.three,
  },
  content: {
    flexGrow: 1,
    gap: Spacing.three,
    paddingVertical: Spacing.three,
  },
  sectionHeader: {
    marginTop: Spacing.two,
  },
  list: {
    gap: Spacing.two,
  },
  bottomNav: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
    paddingVertical: Spacing.two,
    justifyContent: 'space-around',
  },
  navItem: {
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.four,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.one,
  },
});
