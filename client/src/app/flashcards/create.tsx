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
import { useCreateFlashcardMutation } from '@/services/flashcard-api';
import { Spacing } from '@/constants/theme';

const flashcardSchema = z.object({
  wordFront: z.string().min(1, 'Front text is required').max(200),
  wordBack: z.string().min(1, 'Back text is required').max(200),
  example: z.string().max(200).optional(),
});

type FlashcardFormData = z.infer<typeof flashcardSchema>;

export default function FlashcardCreateScreen() {
  const router = useRouter();
  const [createFlashcard, { isLoading }] = useCreateFlashcardMutation();
  const [serverError, setServerError] = useState<string | null>(null);

  const { control, handleSubmit } = useForm<FlashcardFormData>({
    resolver: zodResolver(flashcardSchema),
    mode: 'onChange',
    defaultValues: {
      wordFront: '',
      wordBack: '',
      example: '',
    },
  });

  const handleCreate = handleSubmit(async (data) => {
    setServerError(null);
    try {
      await createFlashcard({
        word_front: data.wordFront,
        word_back: data.wordBack,
        example_sentences: data.example ? [data.example] : [],
      }).unwrap();
      router.back();
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to create flashcard.');
      } else {
        setServerError('Unable to create flashcard.');
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
          <ThemedText type="smallBold">Create Flashcard</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <ServerError message={serverError} />

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

          <Button title="Create" onPress={handleCreate} loading={isLoading} fullWidth />
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
    width: 90,
  },
  scrollContent: {
    paddingVertical: Spacing.three,
    gap: Spacing.two,
  },
});
