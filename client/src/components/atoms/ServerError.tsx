import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

import { useTheme } from '@/hooks/use-theme';
import { Spacing } from '@/constants/theme';

export type ServerErrorProps = {
  message?: string | null;
  containerStyle?: ViewStyle;
};

export function ServerError({ message, containerStyle }: ServerErrorProps) {
  const theme = useTheme();

  if (!message) {
    return null;
  }

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: theme.inputBorderError + '15' },
        containerStyle,
      ]}
    >
      <Text style={[styles.text, { color: theme.error }]}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginBottom: Spacing.two,
  },
  text: {
    fontSize: 14,
    textAlign: 'center',
  },
});