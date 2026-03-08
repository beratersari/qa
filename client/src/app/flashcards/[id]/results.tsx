import React from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/atoms';
import { Spacing } from '@/constants/theme';

export default function FlashcardResultsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ known?: string; unknown?: string; id?: string }>();
  const setId = params.id;
  const known = Number(params.known ?? 0);
  const unknown = Number(params.unknown ?? 0);

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.replace(setId ? `/flashcards/${setId}` : '/flashcards')} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back to Set</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Session Results</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <View style={styles.card}>
          <ThemedText type="small" themeColor="textSecondary">Known</ThemedText>
          <ThemedText type="subtitle">{known}</ThemedText>
        </View>
        <View style={styles.card}>
          <ThemedText type="small" themeColor="textSecondary">Keep Practicing</ThemedText>
          <ThemedText type="subtitle">{unknown}</ThemedText>
        </View>

        <Button title="Back to Set" onPress={() => router.replace(setId ? `/flashcards/${setId}` : '/flashcards')} />
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
    width: 110,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
    gap: Spacing.one,
    marginTop: Spacing.three,
  },
});
