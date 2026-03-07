import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Button, ServerError } from '@/components/atoms';
import { ControlledInput } from '@/components/molecules';
import { createLoginSchema, LoginFormData } from '@/validation';
import { Spacing } from '@/constants/theme';

export type LoginFormProps = {
  onSubmit: (data: LoginFormData) => Promise<void> | void;
  onForgotPassword?: () => void;
  onSignUp?: () => void;
  isLoading?: boolean;
  serverError?: string | null;
};

export function LoginForm({
  onSubmit,
  onForgotPassword,
  onSignUp,
  isLoading = false,
  serverError,
}: LoginFormProps) {
  const {
    control,
    handleSubmit,
    formState: { isValid, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(createLoginSchema()),
    mode: 'onChange',
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const handleFormSubmit = handleSubmit(async (data) => {
    try {
      await onSubmit(data);
    } catch (error) {
      // Error handling is done by the parent component via serverError prop
    }
  });

  const isDisabled = !isValid || isLoading || isSubmitting;

  return (
    <View style={styles.container}>
      <ServerError message={serverError} />

      <ControlledInput<LoginFormData, 'username'>
        control={control}
        name="username"
        fieldType="username"
        label="Username"
      />

      <ControlledInput<LoginFormData, 'password'>
        control={control}
        name="password"
        fieldType="password"
        label="Password"
        showPasswordToggle
      />

      <View style={styles.actions}>
        <Button
          title="Sign In"
          onPress={handleFormSubmit}
          disabled={isDisabled}
          loading={isLoading || isSubmitting}
          fullWidth
          size="large"
        />

        {onForgotPassword && (
          <Button
            title="Forgot Password?"
            onPress={onForgotPassword}
            variant="outline"
            size="small"
            disabled={isLoading}
          />
        )}

        {onSignUp && (
          <Button
            title="Create Account"
            onPress={onSignUp}
            variant="secondary"
            size="medium"
            disabled={isLoading}
          />
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  actions: {
    gap: Spacing.two,
    marginTop: Spacing.two,
  },
});