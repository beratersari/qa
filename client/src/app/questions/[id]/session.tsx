import React, { useMemo, useState } from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button, ServerError } from '@/components/atoms';
import {
  useGetQuestionsInSetQuery,
  useLazyGetQuestionAnswerQuery,
} from '@/services/question-api';
import { QuestionInSetResponse } from '@/types/server-types';
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

export default function QuestionSessionScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const setId = parseInt(id, 10);

  const { data: questions, isLoading, isError } = useGetQuestionsInSetQuery(setId);
  const [fetchAnswer] = useLazyGetQuestionAnswerQuery();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);

  const totalQuestions = questions?.length ?? 0;
  const currentQuestion = questions?.[currentIndex];

  const progressText = useMemo(() => {
    if (!currentQuestion) return 'Question';
    return `Question ${currentIndex + 1} of ${totalQuestions}`;
  }, [currentIndex, currentQuestion, totalQuestions]);

  const handleSelectChoice = (choice: QuestionInSetResponse['choices'][number]) => {
    setSelectedChoice(choice.letter);
  };

  const handleNext = async () => {
    if (!currentQuestion || !selectedChoice) {
      return;
    }

    try {
      const answerData = await fetchAnswer(currentQuestion.question_id).unwrap();
      const selected = currentQuestion.choices.find((choice) => choice.letter === selectedChoice);
      const isCorrect = answerData.answer_letter === selectedChoice;

      const nextAnswer: QuizAnswer = {
        questionId: currentQuestion.question_id,
        prompt: currentQuestion.prompt,
        selectedLetter: selectedChoice,
        selectedText: selected?.text ?? '',
        correctLetter: answerData.answer_letter,
        correctText: answerData.answer_text,
        isCorrect,
      };

      const updatedAnswers = [...answers, nextAnswer];
      setAnswers(updatedAnswers);
      setSelectedChoice(null);

      if (currentIndex + 1 >= totalQuestions) {
        const score = updatedAnswers.filter((answer) => answer.isCorrect).length;
        router.replace({
          pathname: `/questions/${setId}/results`,
          params: {
            score: score.toString(),
            total: totalQuestions.toString(),
            results: JSON.stringify(updatedAnswers),
          },
        });
        return;
      }

      setCurrentIndex((prev) => prev + 1);
    } catch (error) {
      // Fallback: treat as incorrect if answer fetch fails
      const selected = currentQuestion.choices.find((choice) => choice.letter === selectedChoice);
      const nextAnswer: QuizAnswer = {
        questionId: currentQuestion.question_id,
        prompt: currentQuestion.prompt,
        selectedLetter: selectedChoice,
        selectedText: selected?.text ?? '',
        correctLetter: '?',
        correctText: 'Unavailable',
        isCorrect: false,
      };

      const updatedAnswers = [...answers, nextAnswer];
      setAnswers(updatedAnswers);
      setSelectedChoice(null);

      if (currentIndex + 1 >= totalQuestions) {
        const score = updatedAnswers.filter((answer) => answer.isCorrect).length;
        router.replace({
          pathname: `/questions/${setId}/results`,
          params: {
            score: score.toString(),
            total: totalQuestions.toString(),
            results: JSON.stringify(updatedAnswers),
          },
        });
        return;
      }

      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handleExit = () => {
    router.replace(`/questions/${setId}/start`);
  };

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading quiz...</ThemedText>
        </SafeAreaView>
      </ThemedView>
    );
  }

  if (isError || !currentQuestion) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ServerError message="Unable to load quiz questions." />
        </SafeAreaView>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleExit} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Exit</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">{progressText}</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.questionCard}>
            <ThemedText type="defaultSemiBold">{currentQuestion.prompt}</ThemedText>
          </View>

          <View style={styles.choicesContainer}>
            {currentQuestion.choices.map((choice) => {
              const isSelected = selectedChoice === choice.letter;
              return (
                <TouchableOpacity
                  key={choice.letter}
                  style={[styles.choiceItem, isSelected && styles.choiceItemSelected]}
                  onPress={() => handleSelectChoice(choice)}
                >
                  <ThemedText type="smallBold">{choice.letter}.</ThemedText>
                  <ThemedText type="small">{choice.text}</ThemedText>
                </TouchableOpacity>
              );
            })}
          </View>

          <Button
            title={currentIndex + 1 === totalQuestions ? 'Finish Quiz' : 'Next'}
            onPress={handleNext}
            disabled={!selectedChoice}
          />
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
  questionCard: {
    padding: Spacing.four,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  choicesContainer: {
    gap: Spacing.two,
  },
  choiceItem: {
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    flexDirection: 'row',
    gap: Spacing.two,
    alignItems: 'center',
  },
  choiceItemSelected: {
    backgroundColor: '#DCEBFF',
    borderWidth: 1,
    borderColor: '#6EA8FE',
  },
});
