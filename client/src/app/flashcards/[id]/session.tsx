import React, { useMemo, useState } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/atoms';
import { useGetFlashcardQuery } from '@/services/flashcard-api';
import { Spacing } from '@/constants/theme';

export default function FlashcardSessionScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id: string }>();
  const flashcardId = Number(params.id);
  const { data, isLoading } = useGetFlashcardQuery(flashcardId, {
    skip: Number.isNaN(flashcardId),
  });
  const [showBack, setShowBack] = useState(false);
  const [knownCount, setKnownCount] = useState(0);
  const [unknownCount, setUnknownCount] = useState(0);

  const card = useMemo(() => data, [data]);

  const handleKnown = () => {
    const nextKnown = knownCount + 1;
    setKnownCount(nextKnown);
    router.replace(`/flashcards/${flashcardId}/results?known=${nextKnown}&unknown=${unknownCount}`);
  };

  const handleUnknown = () => {
    const nextUnknown = unknownCount + 1;
    setUnknownCount(nextUnknown);
    router.replace(`/flashcards/${flashcardId}/results?known=${knownCount}&unknown=${nextUnknown}`);
  };

  if (isLoading || !card) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading session...</ThemedText>
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
          <ThemedText type="smallBold">Session</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <TouchableOpacity style={styles.card} onPress={() => setShowBack(!showBack)}>
          <ThemedText type="small" themeColor="textSecondary">
            {showBack ? 'Back' : 'Front'}
          </ThemedText>
          <ThemedText type="subtitle">{showBack ? card.word_back : card.word_front}</ThemedText>
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
