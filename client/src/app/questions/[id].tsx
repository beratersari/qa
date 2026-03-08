import React, { useState } from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import {
  useGetQuestionSetQuery,
  useGetQuestionsInSetQuery,
  useGetQuestionAnswerQuery,
} from '@/services/question-api';
import { QuestionInSetResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';

export default function QuestionSetDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const setId = parseInt(id, 10);

  const [selectedQuestion, setSelectedQuestion] = useState<QuestionInSetResponse | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);

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

  const { data: answerData } = useGetQuestionAnswerQuery(
    selectedQuestion?.question_id ?? 0,
    { skip: !selectedQuestion || !showAnswer }
  );

  const isLoading = isLoadingSet || isLoadingQuestions;
  const isError = isErrorSet || isErrorQuestions;

  const handleQuestionPress = (question: QuestionInSetResponse) => {
    setSelectedQuestion(question);
    setShowAnswer(false);
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const handleCloseQuestion = () => {
    setSelectedQuestion(null);
    setShowAnswer(false);
  };

  const handleStartQuiz = () => {
    router.push(`/questions/${setId}/session`);
  };

  if (selectedQuestion) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.header}>
            <TouchableOpacity onPress={handleCloseQuestion} style={styles.backButton}>
              <ThemedText type="small" themeColor="primary">Back</ThemedText>
            </TouchableOpacity>
            <ThemedText type="smallBold">Question</ThemedText>
            <View style={styles.backButtonPlaceholder} />
          </View>

          <ScrollView contentContainerStyle={styles.scrollContent}>
            <View style={styles.questionCard}>
              <ThemedText type="defaultSemiBold">{selectedQuestion.prompt}</ThemedText>
              <View style={styles.choicesContainer}>
                {selectedQuestion.choices.map((choice, index) => (
                  <View key={index} style={styles.choiceItem}>
                    <ThemedText type="smallBold">{choice.letter}.</ThemedText>
                    <ThemedText type="small">{choice.text}</ThemedText>
                  </View>
                ))}
              </View>
            </View>

            {!showAnswer && (
              <Button
                title="Show Answer"
                onPress={handleShowAnswer}
              />
            )}

            {showAnswer && answerData && (
              <View style={styles.answerCard}>
                <ThemedText type="smallBold" themeColor="primary">
                  Correct Answer: {answerData.answer_letter}
                </ThemedText>
                <ThemedText type="small">{answerData.answer_text}</ThemedText>
              </View>
            )}
          </ScrollView>
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
          <ThemedText type="smallBold">{questionSet?.name ?? 'Question Set'}</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        {isError && (
          <ServerError message="Unable to load questions. Please try again." />
        )}

        <ScrollView contentContainerStyle={styles.scrollContent}>
          {questionSet?.description && (
            <ThemedText type="small" themeColor="textSecondary" style={styles.description}>
              {questionSet.description}
            </ThemedText>
          )}

          <Button title="Start Quiz" onPress={handleStartQuiz} />

          <View style={styles.sectionHeader}>
            <ThemedText type="smallBold">
              Questions ({questions?.length ?? 0})
            </ThemedText>
          </View>

          {!isLoading && questions?.length === 0 && (
            <View style={styles.emptyState}>
              <ThemedText type="small">No questions in this set yet.</ThemedText>
            </View>
          )}

          <View style={styles.list}>
            {questions?.map((question, index) => (
              <TouchableOpacity
                key={question.id}
                style={styles.questionCard}
                onPress={() => handleQuestionPress(question)}
              >
                <ThemedText type="smallBold">Question {index + 1}</ThemedText>
                <ThemedText type="small" numberOfLines={2}>
                  {question.prompt}
                </ThemedText>
                <ThemedText type="small" themeColor="textSecondary">
                  Difficulty: {question.difficulty_level}/10
                </ThemedText>
              </TouchableOpacity>
            ))}
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
  },
  description: {
    marginBottom: Spacing.three,
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
  questionCard: {
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.two,
  },
  choicesContainer: {
    gap: Spacing.two,
    marginTop: Spacing.two,
  },
  choiceItem: {
    flexDirection: 'row',
    gap: Spacing.two,
    alignItems: 'flex-start',
  },
  answerCard: {
    padding: Spacing.three,
    backgroundColor: '#D4EDDA',
    borderRadius: 8,
    marginTop: Spacing.three,
    gap: Spacing.one,
  },
  emptyState: {
    padding: Spacing.four,
    alignItems: 'center',
  },
});
