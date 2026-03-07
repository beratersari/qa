import React from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { useGetFlashcardQuery } from '@/services/flashcard-api';
import { Spacing } from '@/constants/theme';

export default function FlashcardDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id: string }>();
  const flashcardId = Number(params.id);
  const { data, isLoading, isError } = useGetFlashcardQuery(flashcardId, {
    skip: Number.isNaN(flashcardId),
  });

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading flashcard...</ThemedText>
        </SafeAreaView>
      </ThemedView>
    );
  }

  if (isError || !data) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ServerError message="Unable to load this flashcard." />
          <Button title="Back" onPress={() => router.back()} variant="outline" />
        </SafeAreaView>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Flashcard</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.card}>
            <ThemedText type="small" themeColor="textSecondary">Front</ThemedText>
            <ThemedText type="subtitle">{data.word_front}</ThemedText>
          </View>
          <View style={styles.card}>
            <ThemedText type="small" themeColor="textSecondary">Back</ThemedText>
            <ThemedText type="subtitle">{data.word_back}</ThemedText>
          </View>
          {data.example_sentences.length > 0 && (
            <View style={styles.card}>
              <ThemedText type="small" themeColor="textSecondary">Example</ThemedText>
              <ThemedText type="small">{data.example_sentences.join('\n')}</ThemedText>
            </View>
          )}
          <Button title="Start Flashcards" onPress={() => router.push(`/flashcards/${data.id}/session`)} />
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
    paddingVertical: Spacing.three,
    gap: Spacing.three,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.one,
  },
});
