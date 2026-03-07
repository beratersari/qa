import React, { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'expo-router';

import { RegisterTemplate } from '@/components/templates';
import { RegistrationFormData } from '@/validation';
import { useRegisterMutation } from '@/services/auth-api';
import { useAppSelector } from '@/store';

export default function RegisterScreen() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [serverError, setServerError] = useState<string | null>(null);
  const [register, { isLoading }] = useRegisterMutation();

  useEffect(() => {
    if (user) {
      router.replace('/');
    }
  }, [user, router]);

  const handleRegister = useCallback(
    async (data: RegistrationFormData) => {
      setServerError(null);

      try {
        await register({
          email: data.email,
          username: data.username,
          password: data.password,
          full_name: data.fullName || null,
        }).unwrap();

        router.replace('/login');
      } catch (error) {
        if (error instanceof Error) {
          setServerError(error.message || 'Unable to register. Please try again.');
        } else {
          setServerError('Unable to register. Please try again.');
        }
      }
    },
    [register, router]
  );

  const handleSignIn = useCallback(() => {
    router.replace('/login');
  }, [router]);

  return (
    <RegisterTemplate
      onSubmit={handleRegister}
      onSignIn={handleSignIn}
      isLoading={isLoading}
      serverError={serverError}
      title="Create Account"
      subtitle="Start your language learning journey today"
    />
  );
}