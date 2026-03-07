import React from 'react';
import { Text, StyleSheet, TextProps } from 'react-native';

import { useTheme } from '@/hooks/use-theme';

export type LabelProps = TextProps & {
  text: string;
  required?: boolean;
};

export function Label({ text, required = false, style, ...props }: LabelProps) {
  const theme = useTheme();

  return (
    <Text style={[styles.label, { color: theme.text }, style]} {...props}>
      {text}
      {required && <Text style={{ color: theme.error }}> *</Text>}
    </Text>
  );
}

const styles = StyleSheet.create({
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 6,
  },
});