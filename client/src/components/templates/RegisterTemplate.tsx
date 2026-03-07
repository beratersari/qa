import React from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { RegisterForm } from '@/components/organisms';
import { RegistrationFormData } from '@/validation';
import { Spacing, MaxContentWidth } from '@/constants/theme';

export type RegisterTemplateProps = {
  onSubmit: (data: RegistrationFormData) => Promise<void> | void;
  onSignIn?: () => void;
  isLoading?: boolean;
  serverError?: string | null;
  title?: string;
  subtitle?: string;
};

export function RegisterTemplate({
  onSubmit,
  onSignIn,
  isLoading = false,
  serverError,
  title = 'Create Account',
  subtitle = 'Start your language learning journey today',
}: RegisterTemplateProps) {
  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardAvoid}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.header}>
              <ThemedText type="title" style={styles.title}>
                {title}
              </ThemedText>
              <ThemedText type="default" style={styles.subtitle}>
                {subtitle}
              </ThemedText>
            </View>

            <View style={styles.formContainer}>
              <RegisterForm
                onSubmit={onSubmit}
                onSignIn={onSignIn}
                isLoading={isLoading}
                serverError={serverError}
              />
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
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
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: Spacing.four,
    paddingVertical: Spacing.four,
    maxWidth: MaxContentWidth,
    width: '100%',
    alignSelf: 'center',
  },
  header: {
    marginBottom: Spacing.five,
    alignItems: 'center',
  },
  title: {
    textAlign: 'center',
    marginBottom: Spacing.two,
  },
  subtitle: {
    textAlign: 'center',
    opacity: 0.7,
  },
  formContainer: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
});