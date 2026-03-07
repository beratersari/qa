import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Button, ServerError } from '@/components/atoms';
import { ControlledInput } from '@/components/molecules';
import { createRegistrationSchema, RegistrationFormData } from '@/validation';
import { Spacing } from '@/constants/theme';

export type RegisterFormProps = {
  onSubmit: (data: RegistrationFormData) => Promise<void> | void;
  onSignIn?: () => void;
  isLoading?: boolean;
  serverError?: string | null;
};

export function RegisterForm({
  onSubmit,
  onSignIn,
  isLoading = false,
  serverError,
}: RegisterFormProps) {
  const {
    control,
    handleSubmit,
    formState: { isValid, isSubmitting },
  } = useForm<RegistrationFormData>({
    resolver: zodResolver(createRegistrationSchema()),
    mode: 'onChange',
    defaultValues: {
      email: '',
      username: '',
      fullName: '',
      password: '',
      confirmPassword: '',
    },
  });

  const handleFormSubmit = handleSubmit(async (data) => {
    await onSubmit(data);
  });

  const isDisabled = !isValid || isLoading || isSubmitting;

  return (
    <View style={styles.container}>
      <ServerError message={serverError} />

      <ControlledInput<RegistrationFormData, 'username'>
        control={control}
        name="username"
        fieldType="username"
        label="Username"
      />

      <ControlledInput<RegistrationFormData, 'email'>
        control={control}
        name="email"
        fieldType="email"
        label="Email"
      />

      <ControlledInput<RegistrationFormData, 'fullName'>
        control={control}
        name="fullName"
        fieldType="fullName"
        label="Full Name"
      />

      <ControlledInput<RegistrationFormData, 'password'>
        control={control}
        name="password"
        fieldType="password"
        label="Password"
        showPasswordToggle
      />

      <ControlledInput<RegistrationFormData, 'confirmPassword'>
        control={control}
        name="confirmPassword"
        fieldType="confirmPassword"
        label="Confirm Password"
        showPasswordToggle
      />

      <View style={styles.actions}>
        <Button
          title="Create Account"
          onPress={handleFormSubmit}
          disabled={isDisabled}
          loading={isLoading || isSubmitting}
          fullWidth
          size="large"
        />

        {onSignIn && (
          <Button
            title="Already have an account? Sign in"
            onPress={onSignIn}
            variant="secondary"
            size="small"
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