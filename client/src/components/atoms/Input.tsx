import React, { forwardRef } from 'react';
import {
  TextInput,
  StyleSheet,
  TextInputProps,
  View,
  ViewStyle,
  TextStyle,
} from 'react-native';

import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type InputProps = TextInputProps & {
  hasError?: boolean;
  isFocused?: boolean;
  containerStyle?: ViewStyle;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
};

export const Input = forwardRef<TextInput, InputProps>(
  (
    {
      hasError = false,
      isFocused = false,
      containerStyle,
      leftIcon,
      rightIcon,
      style,
      ...props
    },
    ref
  ) => {
    const theme = useTheme();

    const getBorderColor = () => {
      if (hasError) {
        return theme.inputBorderError;
      }
      if (isFocused) {
        return theme.inputBorderFocused;
      }
      return theme.inputBorder;
    };

    const inputStyles: TextStyle[] = [
      styles.input,
      { color: theme.text },
    ];
    
    if (leftIcon) {
      inputStyles.push(styles.inputWithLeftIcon);
    }
    if (rightIcon) {
      inputStyles.push(styles.inputWithRightIcon);
    }
    if (style) {
      inputStyles.push(style as TextStyle);
    }

    return (
      <View
        style={[
          styles.container,
          { backgroundColor: theme.inputBackground, borderColor: getBorderColor() },
          containerStyle,
        ]}
      >
        {leftIcon && <View style={styles.iconContainer}>{leftIcon}</View>}
        <TextInput
          ref={ref}
          style={inputStyles}
          placeholderTextColor={theme.inputPlaceholder}
          {...props}
        />
        {rightIcon && <View style={styles.iconContainer}>{rightIcon}</View>}
      </View>
    );
  }
);

Input.displayName = 'Input';

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: Spacing.two,
    paddingHorizontal: Spacing.two,
    minHeight: 48,
  },
  input: {
    flex: 1,
    fontSize: 16,
    paddingVertical: Spacing.two,
  },
  inputWithLeftIcon: {
    marginLeft: Spacing.one,
  },
  inputWithRightIcon: {
    marginRight: Spacing.one,
  },
  iconContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
});