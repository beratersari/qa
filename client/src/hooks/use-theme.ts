/**
 * Learn more about light and dark modes:
 * https://docs.expo.dev/guides/color-schemes/
 */

import { Colors, ThemeColors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAppSelector } from '@/store';

export function useTheme(): ThemeColors {
  const scheme = useColorScheme();
  const theme = scheme === 'unspecified' ? 'light' : scheme;
  const customTheme = useAppSelector((state) => state.auth.themeOverrides);

  return customTheme ? { ...Colors[theme], ...customTheme } : Colors[theme];
}
