import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

import { useTheme } from '@/hooks/use-theme';

export type AvatarProps = {
  monogram: string;
  size?: number;
  style?: ViewStyle;
};

export function Avatar({ monogram, size = 40, style }: AvatarProps) {
  const theme = useTheme();

  return (
    <View
      style={[
        styles.container,
        {
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: theme.backgroundElement,
        },
        style,
      ]}
    >
      <Text style={[styles.text, { color: theme.text }]}>{monogram}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontSize: 14,
    fontWeight: '700',
  },
});