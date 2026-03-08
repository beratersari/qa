import React, { useState } from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { ControlledInput } from '@/components/molecules';
import { Button, ServerError } from '@/components/atoms';
import { useCreateFlashcardSetMutation } from '@/services/flashcard-api';
import { Spacing } from '@/constants/theme';

const flashcardSetSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200),
  description: z.string().max(1000).optional(),
});

type FlashcardSetFormData = z.infer<typeof flashcardSetSchema>;

export default function FlashcardCreateScreen() {
  const router = useRouter();
  const [createFlashcardSet, { isLoading }] = useCreateFlashcardSetMutation();
  const [serverError, setServerError] = useState<string | null>(null);

  const { control, handleSubmit } = useForm<FlashcardSetFormData>({
    resolver: zodResolver(flashcardSetSchema),
    mode: 'onChange',
    defaultValues: {
      name: '',
      description: '',
    },
  });

  const handleCreate = handleSubmit(async (data) => {
    setServerError(null);
    try {
      const result = await createFlashcardSet({
        name: data.name,
        description: data.description,
      }).unwrap();
      router.replace(`/flashcards/${result.id}`);
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to create flashcard set.');
      } else {
        setServerError('Unable to create flashcard set.');
      }
    }
  });

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Create Flashcard Set</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <ServerError message={serverError} />

          <ControlledInput
            control={control}
            name="name"
            fieldType="text"
            label="Set Name"
          />
          <ControlledInput
            control={control}
            name="description"
            fieldType="text"
            label="Description"
          />

          <Button title="Create Set" onPress={handleCreate} loading={isLoading} fullWidth />
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
    width: 140,
  },
  scrollContent: {
    paddingVertical: Spacing.three,
    gap: Spacing.two,
  },
});
