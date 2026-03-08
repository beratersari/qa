import React, { useMemo, useState } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/atoms';
import {
  useGetFlashcardsInSetQuery,
  useStartFlashcardSessionMutation,
  useUpdateFlashcardProgressMutation,
} from '@/services/flashcard-api';
import { Spacing } from '@/constants/theme';

export default function FlashcardSessionScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id: string; card?: string }>();
  const setId = Number(params.id);
  const initialCardId = params.card ? Number(params.card) : undefined;
  const { data: flashcards = [], isLoading } = useGetFlashcardsInSetQuery(setId, {
    skip: Number.isNaN(setId),
  });
  const [startSession] = useStartFlashcardSessionMutation();
  const [updateProgress] = useUpdateFlashcardProgressMutation();
  const [showBack, setShowBack] = useState(false);
  const [knownCount, setKnownCount] = useState(0);
  const [unknownCount, setUnknownCount] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);

  const cards = useMemo(() => flashcards, [flashcards]);

  React.useEffect(() => {
    if (!Number.isNaN(setId)) {
      startSession(setId);
    }
  }, [setId, startSession]);

  React.useEffect(() => {
    if (initialCardId && cards.length > 0) {
      const index = cards.findIndex((card) => card.id === initialCardId);
      if (index >= 0) {
        setCurrentIndex(index);
      }
    }
  }, [initialCardId, cards]);

  const currentCard = cards[currentIndex];

  const handleAnswer = async (status: 'known' | 'unknown') => {
    if (!currentCard) return;
    await updateProgress({
      setId,
      payload: {
        flashcard_id: currentCard.id,
        status,
      },
    }).unwrap();

    if (status === 'known') {
      setKnownCount((prev) => prev + 1);
    } else {
      setUnknownCount((prev) => prev + 1);
    }

    const nextIndex = currentIndex + 1;
    if (nextIndex < cards.length) {
      setCurrentIndex(nextIndex);
      setShowBack(false);
    } else {
      router.replace(`/flashcards/${setId}/results?known=${knownCount + (status === 'known' ? 1 : 0)}&unknown=${unknownCount + (status === 'unknown' ? 1 : 0)}`);
    }
  };

  const handleKnown = () => handleAnswer('known');
  const handleUnknown = () => handleAnswer('unknown');

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading session...</ThemedText>
        </SafeAreaView>
      </ThemedView>
    );
  }

  if (!currentCard) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">No flashcards available.</ThemedText>
          <Button title="Back" variant="outline" onPress={() => router.back()} />
        </SafeAreaView>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.replace(`/flashcards/${setId}`)} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Session</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <TouchableOpacity style={styles.card} onPress={() => setShowBack(!showBack)}>
          <ThemedText type="small" themeColor="textSecondary">
            {showBack ? 'Back' : 'Front'}
          </ThemedText>
          <ThemedText type="subtitle">{showBack ? currentCard.word_back : currentCard.word_front}</ThemedText>
        </TouchableOpacity>

        <View style={styles.actions}>
          <Button title="Known" onPress={handleKnown} />
          <Button title="Keep Practicing" variant="outline" onPress={handleUnknown} />
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
    paddingVertical: Spacing.two,
  },
  backButton: {
    paddingHorizontal: Spacing.two,
    paddingVertical: Spacing.one,
  },
  backButtonPlaceholder: {
    width: 70,
  },
  card: {
    marginTop: Spacing.three,
    padding: Spacing.four,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.two,
    alignItems: 'center',
  },
  actions: {
    marginTop: Spacing.three,
    gap: Spacing.two,
  },
});
