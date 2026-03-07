import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacityProps,
} from 'react-native';

import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type ButtonProps = TouchableOpacityProps & {
  title: string;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  fullWidth?: boolean;
};

export function Button({
  title,
  variant = 'primary',
  size = 'medium',
  loading = false,
  fullWidth = false,
  style,
  disabled,
  ...props
}: ButtonProps) {
  const theme = useTheme();

  const getBackgroundColor = () => {
    if (disabled || loading) {
      return theme.buttonDisabled;
    }
    switch (variant) {
      case 'primary':
        return theme.primary;
      case 'secondary':
        return theme.backgroundElement;
      case 'outline':
        return 'transparent';
    }
  };

  const getTextColor = () => {
    if (disabled || loading) {
      return theme.textSecondary;
    }
    switch (variant) {
      case 'primary':
        return '#ffffff';
      case 'secondary':
        return theme.text;
      case 'outline':
        return theme.primary;
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.button,
        styles[`${size}Button`],
        { backgroundColor: getBackgroundColor() },
        variant === 'outline' && styles.outlineButton,
        variant === 'outline' && { borderColor: theme.primary },
        fullWidth && styles.fullWidth,
        style,
      ]}
      disabled={disabled || loading}
      activeOpacity={0.7}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} size="small" />
      ) : (
        <Text
          style={[
            styles.text,
            styles[`${size}Text`],
            { color: getTextColor() },
            variant === 'primary' && styles.primaryText,
          ]}
        >
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: Spacing.two,
    minWidth: 100,
  },
  smallButton: {
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.two,
    minHeight: 32,
  },
  mediumButton: {
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    minHeight: 44,
  },
  largeButton: {
    paddingVertical: Spacing.three,
    paddingHorizontal: Spacing.four,
    minHeight: 52,
  },
  text: {
    fontWeight: '600',
  },
  smallText: {
    fontSize: 14,
  },
  mediumText: {
    fontSize: 16,
  },
  largeText: {
    fontSize: 18,
  },
  primaryText: {
    fontWeight: '700',
  },
  outlineButton: {
    borderWidth: 1.5,
  },
  fullWidth: {
    width: '100%',
  },
});