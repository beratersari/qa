import React, { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'expo-router';

import { LoginTemplate } from '@/components/templates';
import { LoginFormData } from '@/validation';
import { useLoginMutation } from '@/services/auth-api';
import { useAppDispatch, useAppSelector, persistAuth } from '@/store';

export default function LoginScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);
  const [serverError, setServerError] = useState<string | null>(null);
  const [login, { isLoading }] = useLoginMutation();

  useEffect(() => {
    if (user) {
      router.replace('/');
    }
  }, [user, router]);

  const handleLogin = useCallback(
    async (data: LoginFormData) => {
      setServerError(null);

      try {
        const response = await login({ username: data.username, password: data.password }).unwrap();
        await persistAuth(dispatch, response);
        router.replace('/');
      } catch (error) {
        if (error instanceof Error) {
          setServerError(error.message || 'Invalid username or password. Please try again.');
        } else {
          setServerError('Invalid username or password. Please try again.');
        }
      }
    },
    [dispatch, login, router]
  );

  const handleRegister = useCallback(() => {
    router.replace('/register');
  }, [router]);

  return (
    <LoginTemplate
      onSubmit={handleLogin}
      onSignUp={handleRegister}
      isLoading={isLoading}
      serverError={serverError}
      title="Welcome Back"
      subtitle="Sign in to continue your language learning journey"
    />
  );
}