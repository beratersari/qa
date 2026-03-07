import React, { useState, useCallback } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { Controller, ControllerProps, FieldPath, FieldValues } from 'react-hook-form';

import { Input, ErrorText } from '@/components/atoms';
import { Label } from './Label';
import { FieldConfig, getFieldConfig } from '@/validation';
import { useTheme } from '@/hooks/use-theme';
import { Spacing } from '@/constants/theme';

export type ControlledInputProps<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = Omit<ControllerProps<TFieldValues, TName>, 'render'> & {
  fieldType:
    | 'email'
    | 'password'
    | 'text'
    | 'confirmPassword'
    | 'username'
    | 'fullName'
    | 'profileBio'
    | 'profileContact';
  label?: string;
  showLabel?: boolean;
  showPasswordToggle?: boolean;
  passwordValue?: string;
  showErrorMessage?: boolean;
};

function PasswordToggle({ visible, onPress }: { visible: boolean; onPress: () => void }) {
  const theme = useTheme();
  
  return (
    <TouchableOpacity onPress={onPress} style={styles.toggleButton}>
      <Text style={[styles.toggleText, { color: theme.textSecondary }]}>
        {visible ? 'Hide' : 'Show'}
      </Text>
    </TouchableOpacity>
  );
}

export function ControlledInput<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>({
  fieldType,
  label,
  showLabel = true,
  showPasswordToggle = true,
  passwordValue,
  showErrorMessage = true,
  control,
  name,
  rules,
  ...controllerProps
}: ControlledInputProps<TFieldValues, TName>) {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Get the field configuration based on the field type
  const config: FieldConfig =
    passwordValue && fieldType === 'confirmPassword'
      ? getFieldConfig(fieldType, passwordValue)
      : getFieldConfig(fieldType);

  const displayLabel = label || config.label;
  const isPasswordField = config.secureTextEntry;

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  const togglePasswordVisibility = useCallback(() => {
    setShowPassword((prev) => !prev);
  }, []);

  return (
    <Controller
      control={control}
      name={name}
      rules={rules}
      {...controllerProps}
      render={({ field: { onChange, onBlur, value, ref }, fieldState: { error } }) => (
        <View style={styles.container}>
          {showLabel && <Label text={displayLabel} required />}
          <Input
            ref={ref}
            value={value}
            onChangeText={onChange}
            onFocus={handleFocus}
            onBlur={() => {
              onBlur();
              handleBlur();
            }}
            placeholder={config.placeholder}
            autoCapitalize={config.autoCapitalize}
            autoCorrect={config.autoCorrect}
            keyboardType={config.keyboardType}
            secureTextEntry={isPasswordField ? !showPassword : false}
            hasError={!!error}
            isFocused={isFocused}
            accessibilityLabel={displayLabel}
            accessibilityHint={config.placeholder}
            accessibilityRole="text"
            rightIcon={
              isPasswordField && showPasswordToggle ? (
                <PasswordToggle visible={showPassword} onPress={togglePasswordVisibility} />
              ) : undefined
            }
          />
          {showErrorMessage && error?.message && (
            <ErrorText message={error.message} />
          )}
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.three,
  },
  toggleButton: {
    padding: Spacing.one,
  },
  toggleText: {
    fontSize: 14,
    fontWeight: '500',
  },
});