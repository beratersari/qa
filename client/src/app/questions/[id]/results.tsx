import React, { useMemo } from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/atoms';
import { Spacing } from '@/constants/theme';

type QuizAnswer = {
  questionId: number;
  prompt: string;
  selectedLetter: string;
  selectedText: string;
  correctLetter: string;
  correctText: string;
  isCorrect: boolean;
};

export default function QuestionResultsScreen() {
  const router = useRouter();
  const { id, score, total, results } = useLocalSearchParams<{
    id: string;
    score?: string;
    total?: string;
    results?: string;
  }>();

  const setId = parseInt(id, 10);

  const parsedResults = useMemo(() => {
    if (!results) return [] as QuizAnswer[];
    try {
      return JSON.parse(results) as QuizAnswer[];
    } catch (error) {
      return [] as QuizAnswer[];
    }
  }, [results]);

  const numericScore = Number(score ?? 0);
  const numericTotal = Number(total ?? parsedResults.length);
  const percentage = numericTotal > 0 ? Math.round((numericScore / numericTotal) * 100) : 0;

  const handleRetry = () => {
    router.replace(`/questions/${setId}/session`);
  };

  const handleBackToStart = () => {
    router.replace(`/questions/${setId}/start`);
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBackToStart} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Quiz Results</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.scoreCard}>
            <ThemedText type="subtitle">Score</ThemedText>
            <ThemedText type="large">{numericScore}/{numericTotal}</ThemedText>
            <ThemedText type="small" themeColor="textSecondary">
              {percentage}% correct
            </ThemedText>
          </View>

          <View style={styles.buttonGroup}>
            <Button title="Retry Quiz" onPress={handleRetry} />
            <Button title="Back to Start" variant="outline" onPress={handleBackToStart} />
          </View>

          {parsedResults.length > 0 && (
            <View style={styles.resultsList}>
              {parsedResults.map((answer, index) => (
                <View key={`${answer.questionId}-${index}`} style={styles.resultCard}>
                  <ThemedText type="smallBold">
                    {answer.isCorrect ? '✅' : '❌'} Question {index + 1}
                  </ThemedText>
                  <ThemedText type="small">{answer.prompt}</ThemedText>
                  <ThemedText type="small" themeColor="textSecondary">
                    Your Answer: {answer.selectedLetter} - {answer.selectedText}
                  </ThemedText>
                  <ThemedText type="small" themeColor="textSecondary">
                    Correct Answer: {answer.correctLetter} - {answer.correctText}
                  </ThemedText>
                </View>
              ))}
            </View>
          )}
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
    gap: Spacing.three,
  },
  scoreCard: {
    padding: Spacing.four,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    alignItems: 'center',
    gap: Spacing.one,
  },
  buttonGroup: {
    gap: Spacing.two,
  },
  resultsList: {
    gap: Spacing.two,
  },
  resultCard: {
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.one,
  },
});
