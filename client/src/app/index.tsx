import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { View, StyleSheet, TouchableOpacity } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Button, Avatar } from '@/components/atoms';
import { useAppDispatch, useAppSelector, logoutUser } from '@/store';
import { Spacing } from '@/constants/theme';

function getMonogram(name: string) {
  const parts = name.split(' ').filter(Boolean);
  if (parts.length === 0) return '';
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export default function DashboardScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  if (!user) {
    router.replace('/login');
    return null;
  }

  const displayName = user.username || user.email;

  const handleLogout = async () => {
    await logoutUser(dispatch);
    router.replace('/login');
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.push('/profile')}>
            <Avatar monogram={getMonogram(displayName)} />
          </TouchableOpacity>
          <Button title="Logout" variant="outline" size="small" onPress={handleLogout} />
        </View>

        <View style={styles.content}>
          <ThemedText type="subtitle">Hello {displayName}</ThemedText>
          <Button title="View Profile" onPress={() => router.push('/profile')} />
          <Button title="Flashcards" onPress={() => router.push('/flashcards')} />
        </View>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: Spacing.four,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: Spacing.three,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
