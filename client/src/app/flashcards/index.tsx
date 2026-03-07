import React, { useState } from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FlatList, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { useGetFlashcardsQuery } from '@/services/flashcard-api';
import { FlashcardResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';

const FILTERS = [
  { key: 'mine', label: 'My Flashcards' },
  { key: 'all', label: 'All Flashcards' },
] as const;

export default function FlashcardListScreen() {
  const router = useRouter();
  const [scope, setScope] = useState<'all' | 'mine'>('mine');
  const { data, isLoading, isError } = useGetFlashcardsQuery({ scope });

  const flashcards = data ?? [];

  const handleCreate = () => {
    router.push('/flashcards/create');
  };

  const renderItem = ({ item }: { item: FlashcardResponse }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/flashcards/${item.id}`)}
    >
      <ThemedText type="smallBold">{item.word_front}</ThemedText>
      <ThemedText type="small" themeColor="textSecondary">
        {item.word_back}
      </ThemedText>
      {item.example_sentences.length > 0 && (
        <ThemedText type="small" themeColor="textSecondary">
          {item.example_sentences[0]}
        </ThemedText>
      )}
    </TouchableOpacity>
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Flashcards</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <View style={styles.switcher}>
          {FILTERS.map((filter) => (
            <Button
              key={filter.key}
              title={filter.label}
              size="small"
              variant={scope === filter.key ? 'primary' : 'outline'}
              onPress={() => setScope(filter.key)}
              style={styles.switcherButton}
            />
          ))}
        </View>

        {isError && (
          <ServerError message="Unable to load flashcards. Please try again." />
        )}

        {!isLoading && !isError && flashcards.length === 0 && (
          <View style={styles.emptyState}>
            <ThemedText type="smallBold">No flashcards yet</ThemedText>
            <ThemedText type="small" themeColor="textSecondary">
              {scope === 'mine'
                ? 'Create your first flashcard to start studying.'
                : 'No flashcards available right now.'}
            </ThemedText>
          </View>
        )}

        <FlatList
          data={flashcards}
          keyExtractor={(item) => `${item.id}`}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          ListFooterComponent={
            <View style={styles.footer}>
              <Button title="Create Flashcard" onPress={handleCreate} />
            </View>
          }
          refreshing={isLoading}
          onRefresh={() => setScope((prev) => prev)}
        />
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
  switcher: {
    flexDirection: 'row',
    gap: Spacing.two,
    paddingVertical: Spacing.two,
  },
  switcherButton: {
    flex: 1,
  },
  listContent: {
    gap: Spacing.two,
    paddingBottom: Spacing.four,
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
    gap: Spacing.one,
    marginBottom: Spacing.three,
  },
  footer: {
    marginTop: Spacing.three,
  },
});
