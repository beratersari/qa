import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { ServerError } from '@/components/atoms';
import { useGetXpLeaderboardQuery } from '@/services/leaderboard-api';
import { Spacing } from '@/constants/theme';

export default function LeaderboardScreen() {
  const router = useRouter();
  const { data, isLoading, isError } = useGetXpLeaderboardQuery();

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <View style={styles.backButtonPlaceholder} />
          <ThemedText type="smallBold">Leaderboard</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>

        {isError && (
          <ServerError message="Unable to load leaderboard." />
        )}

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.summaryCard}>
            <ThemedText type="subtitle">Top XP Earners</ThemedText>
            <ThemedText type="small" themeColor="textSecondary">
              Earn XP by daily streaks, questions, and flashcard sets.
            </ThemedText>
          </View>

          {isLoading && (
            <ThemedText type="small">Loading leaderboard...</ThemedText>
          )}

          <View style={styles.list}>
            {data?.entries.map((entry) => (
              <View key={`${entry.rank}-${entry.display_name}`} style={styles.card}>
                <View style={styles.rankBadge}>
                  <ThemedText type="smallBold">#{entry.rank}</ThemedText>
                </View>
                <View style={styles.userInfo}>
                  <ThemedText type="smallBold">{entry.display_name}</ThemedText>
                  <ThemedText type="small" themeColor="textSecondary">
                    Streak: {entry.challenge_streak} days
                  </ThemedText>
                </View>
                <View style={styles.xpInfo}>
                  <ThemedText type="smallBold">{entry.total_xp} XP</ThemedText>
                </View>
              </View>
            ))}
          </View>

          {data?.current_user_rank && (
            <View style={styles.currentUserCard}>
              <ThemedText type="smallBold">
                Your Rank: #{data.current_user_rank}
              </ThemedText>
            </View>
          )}
        </ScrollView>

        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/')}
          >
            <ThemedText type="small">Dashboard</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/leaderboard')}>
            <ThemedText type="smallBold" themeColor="primary">Leaderboard</ThemedText>
          </TouchableOpacity>
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
  backButton: {
    minWidth: 50,
  },
  backButtonPlaceholder: {
    minWidth: 50,
  },
  scrollContent: {
    paddingBottom: Spacing.four,
    gap: Spacing.three,
  },
  summaryCard: {
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.one,
  },
  list: {
    gap: Spacing.two,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.three,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    gap: Spacing.two,
  },
  rankBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#DCEBFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  userInfo: {
    flex: 1,
  },
  xpInfo: {
    alignItems: 'flex-end',
  },
  currentUserCard: {
    padding: Spacing.three,
    backgroundColor: '#FFF3CD',
    borderRadius: 8,
    alignItems: 'center',
  },
  bottomNav: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
    paddingVertical: Spacing.two,
    justifyContent: 'space-around',
  },
  navItem: {
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.four,
  }
});
