import React, { useMemo, useState } from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { SubscriptionPlans } from '@/components/organisms';
import {
  useGetMySubscriptionQuery,
  useGetSubscriptionPlansQuery,
  useSubscribeMutation,
  useCancelSubscriptionMutation,
  useRenewSubscriptionMutation,
} from '@/services/subscription-api';
import { ServerError } from '@/components/atoms';
import { Spacing } from '@/constants/theme';
import { SubscriptionPlanResponse } from '@/types/server-types';

export default function SubscriptionManagementScreen() {
  const router = useRouter();
  const { data: plans = [], isLoading: plansLoading } = useGetSubscriptionPlansQuery();
  const { data: subscription, isLoading: subscriptionLoading } = useGetMySubscriptionQuery();
  const [subscribe, { isLoading: subscribing }] = useSubscribeMutation();
  const [cancel, { isLoading: canceling }] = useCancelSubscriptionMutation();
  const [renew, { isLoading: renewing }] = useRenewSubscriptionMutation();
  const [serverError, setServerError] = useState<string | null>(null);

  const loadingPlan = useMemo(() => {
    if (subscribing) return 'subscribe';
    if (canceling) return 'cancel';
    if (renewing) return 'renew';
    return null;
  }, [subscribing, canceling, renewing]);

  const handleSubscribe = async (plan: SubscriptionPlanResponse) => {
    setServerError(null);
    try {
      await subscribe(plan.name).unwrap();
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to subscribe to plan.');
      } else {
        setServerError('Unable to subscribe to plan.');
      }
    }
  };

  const handleCancel = async (subscriptionId: number) => {
    setServerError(null);
    try {
      await cancel(subscriptionId).unwrap();
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to cancel subscription.');
      } else {
        setServerError('Unable to cancel subscription.');
      }
    }
  };

  const handleRenew = async (subscriptionId: number) => {
    setServerError(null);
    try {
      await renew(subscriptionId).unwrap();
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to renew subscription.');
      } else {
        setServerError('Unable to renew subscription.');
      }
    }
  };

  if (plansLoading || subscriptionLoading) {
    return (
      <ThemedView style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <ThemedText type="small">Loading subscriptions...</ThemedText>
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
          <ThemedText type="smallBold">Subscription</ThemedText>
          <View style={styles.backButtonPlaceholder} />
        </View>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <ServerError message={serverError} />

          <SubscriptionPlans
            plans={plans}
            activeSubscription={subscription}
            onSubscribe={handleSubscribe}
            onCancel={handleCancel}
            onRenew={handleRenew}
            loadingPlan={loadingPlan}
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