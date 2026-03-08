import React from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { ControlledInput } from '@/components/molecules';
import {
  useGetFlashcardSetQuery,
  useGetFlashcardsInSetQuery,
  useGetFlashcardProgressQuery,
  useDeleteFlashcardSetMutation,
  useDeleteFlashcardFromSetMutation,
  useCreateFlashcardMutation,
  useAddFlashcardToSetMutation,
} from '@/services/flashcard-api';
import { FlashcardInSetResponse, FlashcardProgressResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';
import { useAppSelector } from '@/store';

const flashcardSchema = z.object({
  wordFront: z.string().min(1, 'Front text is required').max(200),
  wordBack: z.string().min(1, 'Back text is required').max(200),
  example: z.string().max(200).optional(),
});

type FlashcardFormData = z.infer<typeof flashcardSchema>;

export default function FlashcardDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id: string }>();
  const setId = Number(params.id);
  const { data, isLoading, isError } = useGetFlashcardSetQuery(setId, {
    skip: Number.isNaN(setId),
  });
  const { data: flashcards = [] } = useGetFlashcardsInSetQuery(setId, {
    skip: Number.isNaN(setId),
  });
  const { data: progress = [] } = useGetFlashcardProgressQuery(setId, {
    skip: Number.isNaN(setId),
  });
  const [deleteFlashcardSet] = useDeleteFlashcardSetMutation();
  const [deleteFlashcardFromSet] = useDeleteFlashcardFromSetMutation();
  const [createFlashcard] = useCreateFlashcardMutation();
  const [addFlashcardToSet] = useAddFlashcardToSetMutation();
  const currentUserId = useAppSelector((state) => state.auth.user?.id);

  const { control, handleSubmit, reset } = useForm<FlashcardFormData>({
    resolver: zodResolver(flashcardSchema),
    mode: 'onChange',
    defaultValues: {
      wordFront: '',
      wordBack: '',
      example: '',
    },
  });

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading flashcard set...</ThemedText>
        </SafeAreaView>
      </ThemedView>
    );
  }

  if (isError || !data) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ServerError message="Unable to load this flashcard set." />
          <Button title="Back" onPress={() => router.back()} variant="outline" />
        </SafeAreaView>
      </ThemedView>
    );
  }

  const progressMap = progress.reduce<Record<number, FlashcardProgressResponse>>((acc, item) => {
    acc[item.flashcard_id] = item;
    return acc;
  }, {});
  const isOwner = Boolean(data.created_by && data.created_by === currentUserId);

  const handleDeleteSet = async () => {
    await deleteFlashcardSet(data.id).unwrap();
    router.replace('/flashcards');
  };

  const handleDeleteFlashcard = async (flashcard: FlashcardInSetResponse) => {
    await deleteFlashcardFromSet({ setId: data.id, flashcardId: flashcard.id }).unwrap();
  };

  const handleCreateFlashcard = handleSubmit(async (formData) => {
    const created = await createFlashcard({
      word_front: formData.wordFront,
      word_back: formData.wordBack,
      example_sentences: formData.example ? [formData.example] : [],
    }).unwrap();
    await addFlashcardToSet({ setId: data.id, flashcardId: created.id }).unwrap();
    reset();
  });

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">{data.name}</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {data.description && (
            <View style={styles.card}>
              <ThemedText type="small" themeColor="textSecondary">Description</ThemedText>
              <ThemedText type="small">{data.description}</ThemedText>
            </View>
          )}
          <View style={styles.card}>
            <ThemedText type="small" themeColor="textSecondary">Cards</ThemedText>
            <ThemedText type="subtitle">{data.flashcard_count}</ThemedText>
          </View>

          <View style={styles.actions}>
            <Button title="Start Session" onPress={() => router.replace(`/flashcards/${data.id}/session`)} />
            {isOwner && (
              <Button title="Delete Set" variant="outline" onPress={handleDeleteSet} />
            )}
          </View>

          {isOwner && (
            <>
              <View style={styles.sectionHeader}>
                <ThemedText type="smallBold">Add a flashcard</ThemedText>
              </View>
              <View style={styles.card}>
                <ControlledInput
                  control={control}
                  name="wordFront"
                  fieldType="text"
                  label="Front"
                />
                <ControlledInput
                  control={control}
                  name="wordBack"
                  fieldType="text"
                  label="Back"
                />
                <ControlledInput
                  control={control}
                  name="example"
                  fieldType="text"
                  label="Example Sentence"
                />
                <Button title="Add Card" onPress={handleCreateFlashcard} />
              </View>
            </>
          )}

          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">Cards in this set</ThemedText>
          </View>
          {flashcards.length === 0 && (
            <View style={styles.emptyState}>
              <ThemedText type="small">No cards in this set yet.</ThemedText>
            </View>
          )}
          {flashcards.map((card) => (
            <TouchableOpacity
              key={card.id}
              style={styles.card}
              onPress={() => router.push(`/flashcards/${data.id}/session?card=${card.id}`)}
            >
              <ThemedText type="smallBold">{card.word_front}</ThemedText>
              <ThemedText type="small" themeColor="textSecondary">{card.word_back}</ThemedText>
              {progressMap[card.id] && (
                <ThemedText type="small" themeColor="textSecondary">
                  {progressMap[card.id].status === 'known' ? 'Known' : 'Keep Practicing'}
                </ThemedText>
              )}
              {isOwner && (
                <View style={styles.cardActions}>
                  <Button
                    title="Delete"
                    size="small"
                    variant="outline"
                    onPress={() => handleDeleteFlashcard(card)}
                  />
                </View>
              )}
            </TouchableOpacity>
          ))}
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
  actions: {
    gap: Spacing.two,
  },
  sectionHeader: {
    marginTop: Spacing.two,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.one,
  },
  cardActions: {
    marginTop: Spacing.one,
  },
  emptyState: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
  },
});
