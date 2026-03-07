import React from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { LoginForm } from '@/components/organisms';
import { LoginFormData } from '@/validation';
import { Spacing, MaxContentWidth } from '@/constants/theme';

export type LoginTemplateProps = {
  onSubmit: (data: LoginFormData) => Promise<void> | void;
  onForgotPassword?: () => void;
  onSignUp?: () => void;
  isLoading?: boolean;
  serverError?: string | null;
  title?: string;
  subtitle?: string;
};

export function LoginTemplate({
  onSubmit,
  onForgotPassword,
  onSignUp,
  isLoading = false,
  serverError,
  title = 'Welcome Back',
  subtitle = 'Sign in to continue learning',
}: LoginTemplateProps) {
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
              <LoginForm
                onSubmit={onSubmit}
                onForgotPassword={onForgotPassword}
                onSignUp={onSignUp}
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