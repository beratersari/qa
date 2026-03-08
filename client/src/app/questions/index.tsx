import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { useGetQuestionSetsQuery } from '@/services/question-api';
import { useGetMySubscriptionQuery } from '@/services/subscription-api';
import { QuestionSetResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';

export default function QuestionSetsScreen() {
  const router = useRouter();
  const { data: subscription } = useGetMySubscriptionQuery();
  const isPremium = subscription?.status === 'active';

  const { data: questionSets, isLoading, isError } = useGetQuestionSetsQuery();

  const handleViewSet = (set: QuestionSetResponse) => {
    if (set.set_type === 'premium' && !isPremium) {
      // Show premium lock - navigate to subscription
      router.push('/profile/subscription');
      return;
    }
    router.push(`/questions/${set.id}/start`);
  };

  const renderSet = (item: QuestionSetResponse) => {
    const isLocked = item.set_type === 'premium' && !isPremium;

    return (
      <TouchableOpacity
        key={item.id}
        style={[styles.card, isLocked && styles.lockedCard]}
        onPress={() => handleViewSet(item)}
      >
        <View style={styles.cardHeader}>
          <ThemedText type="smallBold">{item.name}</ThemedText>
          {item.set_type === 'premium' && (
            <View style={styles.premiumBadge}>
              <ThemedText type="small" style={styles.premiumText}>
                {isLocked ? '🔒 PREMIUM' : '✓ PREMIUM'}
              </ThemedText>
            </View>
          )}
        </View>
        {item.description && (
          <ThemedText type="small" themeColor="textSecondary">
            {item.description}
          </ThemedText>
        )}
        <ThemedText type="small" themeColor="textSecondary">
          {item.question_count} questions
        </ThemedText>
      </TouchableOpacity>
    );
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Question Sets</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        {isError && (
          <ServerError message="Unable to load question sets. Please try again." />
        )}

        <ScrollView contentContainerStyle={styles.scrollContent}>
          {!isPremium && (
            <View style={styles.premiumBanner}>
              <ThemedText type="small">
                🔒 Premium sets are locked. Subscribe to access all content!
              </ThemedText>
              <Button
                title="Upgrade to Premium"
                size="small"
                onPress={() => router.push('/profile/subscription')}
              />
            </View>
          )}

          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">All Question Sets</ThemedText>
          </View>

          {!isLoading && questionSets?.length === 0 && (
            <View style={styles.emptyState}>
              <ThemedText type="small">No question sets available yet.</ThemedText>
            </View>
          )}

          <View style={styles.list}>{questionSets?.map(renderSet)}</View>
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
    paddingVertical: Spacing.three,
  },
  backButton: {
    minWidth: 50,
  },
  backButtonPlaceholder: {
    minWidth: 50,
  },
  scrollContent: {
    paddingBottom: Spacing.four,
  },
  premiumBanner: {
    backgroundColor: '#FFF3CD',
    padding: Spacing.three,
    borderRadius: 8,
    marginBottom: Spacing.four,
    gap: Spacing.two,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.two,
  },
  list: {
    gap: Spacing.two,
  },
  card: {
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.one,
  },
  lockedCard: {
    opacity: 0.7,
    backgroundColor: '#e0e0e0',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  premiumBadge: {
    backgroundColor: '#FFD700',
    paddingHorizontal: Spacing.two,
    paddingVertical: 4,
    borderRadius: 4,
  },
  premiumText: {
    color: '#000',
    fontWeight: '600',
  },
  emptyState: {
    padding: Spacing.four,
    alignItems: 'center',
  },
});
