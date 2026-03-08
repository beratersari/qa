import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { useGetFlashcardSetsQuery } from '@/services/flashcard-api';
import { FlashcardSetResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';

export default function FlashcardListScreen() {
  const router = useRouter();
  const {
    data: mySets,
    isLoading: isLoadingMine,
    isError: isErrorMine,
  } = useGetFlashcardSetsQuery({ scope: 'mine' });
  const {
    data: allSets,
    isLoading: isLoadingAll,
    isError: isErrorAll,
  } = useGetFlashcardSetsQuery({ scope: 'all' });

  const myFlashcards = mySets ?? [];
  const availableSets = allSets ?? [];
  const isLoading = isLoadingMine || isLoadingAll;
  const isError = isErrorMine || isErrorAll;

  const handleCreateSet = () => {
    router.push('/flashcards/create');
  };

  const renderSet = (item: FlashcardSetResponse) => (
    <TouchableOpacity
      key={item.id}
      style={styles.card}
      onPress={() => router.push(`/flashcards/${item.id}`)}
    >
      <ThemedText type="smallBold">{item.name}</ThemedText>
      {item.description && (
        <ThemedText type="small" themeColor="textSecondary">
          {item.description}
        </ThemedText>
      )}
      <ThemedText type="small" themeColor="textSecondary">
        {item.flashcard_count} cards
      </ThemedText>
    </TouchableOpacity>
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Flashcard Sets</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        {isError && (
          <ServerError message="Unable to load flashcard sets. Please try again." />
        )}

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">My Flashcards</ThemedText>
            <Button title="Create Set" size="small" onPress={handleCreateSet} />
          </View>
          {!isLoading && myFlashcards.length === 0 && (
            <View style={styles.emptyState}>
              <ThemedText type="small">Create your first flashcard set.</ThemedText>
            </View>
          )}
          <View style={styles.list}>{myFlashcards.map(renderSet)}</View>

          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">All Flashcard Sets</ThemedText>
          </View>
          {!isLoading && availableSets.length === 0 && (
            <View style={styles.emptyState}>
              <ThemedText type="small">No flashcard sets available yet.</ThemedText>
            </View>
          )}
          <View style={styles.list}>{availableSets.map(renderSet)}</View>
        </ScrollView>
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
    paddingVertical: Spacing.two,
  },
  backButton: {
    paddingHorizontal: Spacing.two,
    paddingVertical: Spacing.one,
  },
  backButtonPlaceholder: {
    width: 70,
  },
  scrollContent: {
    gap: Spacing.three,
    paddingBottom: Spacing.four,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  list: {
    gap: Spacing.two,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.one,
  },
  emptyState: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
  },
});
