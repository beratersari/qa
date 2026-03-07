import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Avatar, Button } from '@/components/atoms';
import { UserProfileResponse } from '@/types/profile';
import { SubscriptionResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type ProfileDetailsProps = {
  profile: UserProfileResponse;
  subscription?: SubscriptionResponse | null;
  onEditProfile: () => void;
  onSubscriptionPress: () => void;
};

function getMonogram(name: string) {
  const parts = name.split(' ').filter(Boolean);
  if (parts.length === 0) return '';
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export function ProfileDetails({
  profile,
  subscription,
  onEditProfile,
  onSubscriptionPress,
}: ProfileDetailsProps) {
  const theme = useTheme();
  const displayName = profile.full_name || profile.username;
  const hasBio = Boolean(profile.bio);
  const hasContact = Boolean(profile.contact_info);
  const xpValue = profile.total_xp?.toLocaleString() ?? '0';

  return (
    <ThemedView style={styles.container}>
      <View style={[styles.headerCard, { backgroundColor: theme.backgroundElement }]}>
        <View style={styles.headerTop}>
          <Avatar monogram={getMonogram(displayName)} size={72} />
          <View style={styles.headerText}>
            <ThemedText type="subtitle">{displayName}</ThemedText>
            <ThemedText type="small" themeColor="textSecondary">{profile.email}</ThemedText>
          </View>
        </View>
        <View style={styles.statRow}>
          <View style={styles.statItem}>
            <ThemedText type="small" themeColor="textSecondary">Total XP</ThemedText>
            <ThemedText type="smallBold">{xpValue}</ThemedText>
          </View>
          <View style={styles.statItem}>
            <ThemedText type="small" themeColor="textSecondary">Level</ThemedText>
            <ThemedText type="smallBold">{profile.level}</ThemedText>
          </View>
          <View style={styles.statItem}>
            <ThemedText type="small" themeColor="textSecondary">Streak</ThemedText>
            <ThemedText type="smallBold">{profile.challenge_streak}</ThemedText>
          </View>
        </View>
      </View>

      <View style={styles.sectionCard}>
        <ThemedText type="smallBold">About</ThemedText>
        <View style={styles.fieldRow}>
          <ThemedText type="small" themeColor="textSecondary">Bio</ThemedText>
          <ThemedText type="small">{hasBio ? profile.bio : 'Add a bio in your profile settings.'}</ThemedText>
        </View>
        <View style={styles.fieldRow}>
          <ThemedText type="small" themeColor="textSecondary">Contact</ThemedText>
          <ThemedText type="small">{hasContact ? profile.contact_info : 'No contact info added.'}</ThemedText>
        </View>
        <View style={styles.fieldRow}>
          <ThemedText type="small" themeColor="textSecondary">Visibility</ThemedText>
          <ThemedText type="small">{profile.profile_visibility === 'public' ? 'Public profile' : 'Private profile'}</ThemedText>
        </View>
      </View>

      <TouchableOpacity onPress={onSubscriptionPress} style={[styles.subscriptionCard, { borderColor: theme.inputBorder }]}>
        <View style={styles.subscriptionHeader}>
          <ThemedText type="smallBold">Subscription</ThemedText>
          <ThemedText type="small" themeColor="textSecondary">Manage</ThemedText>
        </View>
        {subscription ? (
          <>
            <ThemedText type="small">Plan: {subscription.plan}</ThemedText>
            <ThemedText type="small">Status: {subscription.status}</ThemedText>
            <ThemedText type="small">
              Auto-renew: {subscription.auto_renew ? 'On' : 'Off'}
            </ThemedText>
          </>
        ) : (
          <ThemedText type="small">No active subscription</ThemedText>
        )}
      </TouchableOpacity>

      <Button title="Edit Profile" onPress={onEditProfile} fullWidth />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: Spacing.three,
  },
  headerCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    gap: Spacing.three,
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.three,
  },
  headerText: {
    flex: 1,
    gap: Spacing.one,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: Spacing.two,
  },
  statItem: {
    flex: 1,
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.two,
    borderRadius: Spacing.two,
    backgroundColor: 'rgba(255, 178, 178, 0.2)',
    gap: Spacing.half,
  },
  sectionCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    gap: Spacing.two,
    borderWidth: 1,
    borderColor: 'rgba(255, 178, 178, 0.4)',
  },
  fieldRow: {
    gap: Spacing.one,
  },
  subscriptionCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    gap: Spacing.one,
  },
  subscriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
});