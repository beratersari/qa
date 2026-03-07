import React from 'react';
import { Text, StyleSheet, TextProps } from 'react-native';

import { useTheme } from '@/hooks/use-theme';

export type ErrorTextProps = TextProps & {
  message?: string;
};

export function ErrorText({ message, style, ...props }: ErrorTextProps) {
  const theme = useTheme();

  if (!message) {
    return null;
  }

  return (
    <Text style={[styles.errorText, { color: theme.error }, style]} {...props}>
      {message}
    </Text>
  );
}

const styles = StyleSheet.create({
  errorText: {
    fontSize: 12,
    lineHeight: 16,
    marginTop: 4,
  },
});