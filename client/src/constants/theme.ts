/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

import '@/global.css';

import { Platform } from 'react-native';

export const DefaultTheme = {
  text: '#4C5C2D',
  background: '#FFFBF1',
  backgroundElement: '#FFF2D0',
  backgroundSelected: '#FFB2B2',
  textSecondary: '#6A7E3F',
  inputBackground: '#FBF6F6',
  inputBorder: '#FFB2B2',
  inputBorderFocused: '#D96868',
  inputBorderError: '#E36A6A',
  inputPlaceholder: '#6A7E3F',
  error: '#E36A6A',
  primary: '#D96868',
  primaryHover: '#E36A6A',
  buttonDisabled: '#FFB2B2',
} as const;

export type ThemeColors = typeof DefaultTheme;

export const Colors = {
  light: DefaultTheme,
  dark: {
    ...DefaultTheme,
    text: '#FFFBF1',
    background: '#4C5C2D',
    backgroundElement: '#6A7E3F',
    backgroundSelected: '#D96868',
    textSecondary: '#FFF2D0',
    inputBackground: '#4C5C2D',
    inputBorder: '#6A7E3F',
    inputBorderFocused: '#FFB2B2',
    inputBorderError: '#E36A6A',
    inputPlaceholder: '#FFF2D0',
    buttonDisabled: '#6A7E3F',
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 800;
