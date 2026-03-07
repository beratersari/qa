import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { ProfileDetails } from '@/components/organisms';
import { useGetMyProfileQuery } from '@/services/user-api';
import { useGetMySubscriptionQuery } from '@/services/subscription-api';
import { Spacing } from '@/constants/theme';

export default function ProfileScreen() {
  const router = useRouter();
  const { data: profile, isLoading: profileLoading } = useGetMyProfileQuery();
  const { data: subscription } = useGetMySubscriptionQuery();

  const handleEditProfile = () => {
    router.push('/profile/edit');
  };

  const handleSubscriptionPress = () => {
    router.push('/profile/subscription');
  };

  if (profileLoading || !profile) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading profile...</ThemedText>
        </SafeAreaView>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ThemedText type="small" themeColor="primary">Back</ThemedText>
          </TouchableOpacity>
          <ThemedText type="smallBold">Profile</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <ProfileDetails
            profile={profile}
            subscription={subscription}
            onEditProfile={handleEditProfile}
            onSubscriptionPress={handleSubscriptionPress}
          />
        </ScrollView>
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
    paddingVertical: Spacing.two,
  },
  backButton: {
    paddingHorizontal: Spacing.two,
    paddingVertical: Spacing.one,
  },
  backButtonPlaceholder: {
    width: 50,
  },
  scrollContent: {
    paddingVertical: Spacing.three,
    gap: Spacing.three,
  },
});