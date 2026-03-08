import React from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import { useGetQuestionSetQuery, useGetQuestionsInSetQuery } from '@/services/question-api';
import { useGetMySubscriptionQuery } from '@/services/subscription-api';
import { Spacing } from '@/constants/theme';

export default function QuestionStartScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const setId = parseInt(id, 10);

  const { data: subscription } = useGetMySubscriptionQuery();
  const isPremium = subscription?.status === 'active';

  const {
    data: questionSet,
    isLoading: isLoadingSet,
    isError: isErrorSet,
  } = useGetQuestionSetQuery(setId);

  const {
    data: questions,
    isLoading: isLoadingQuestions,
    isError: isErrorQuestions,
  } = useGetQuestionsInSetQuery(setId);

  const isLoading = isLoadingSet || isLoadingQuestions;
  const isError = isErrorSet || isErrorQuestions;

  const handleStart = () => {
    if (questionSet?.set_type === 'premium' && !isPremium) {
      router.push('/profile/subscription');
      return;
    }
    router.push(`/questions/${setId}/session`);
  };

  const handlePreview = () => {
    router.push(`/questions/${setId}`);
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Start Quiz</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        {isError && (
          <ServerError message="Unable to load question set. Please try again." />
        )}

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.card}>
            <ThemedText type="subtitle">{questionSet?.name ?? 'Question Set'}</ThemedText>
            {questionSet?.description && (
              <ThemedText type="small" themeColor="textSecondary">
                {questionSet.description}
              </ThemedText>
            )}
            <ThemedText type="small" themeColor="textSecondary">
              {questions?.length ?? 0} questions
            </ThemedText>
            {questionSet?.set_type === 'premium' && (
              <ThemedText type="small" themeColor="primary">
                {isPremium ? 'Premium access unlocked' : 'Premium set - subscription required'}
              </ThemedText>
            )}
          </View>

          <View style={styles.buttonGroup}>
            <Button
              title="Start Quiz"
              onPress={handleStart}
              disabled={isLoading}
            />
            <Button
              title="Preview Questions"
              variant="outline"
              onPress={handlePreview}
              disabled={isLoading}
            />
          </View>
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
    gap: Spacing.four,
  },
  card: {
    padding: Spacing.four,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.two,
  },
  buttonGroup: {
    gap: Spacing.two,
  },
});
