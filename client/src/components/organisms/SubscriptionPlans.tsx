import React from 'react';
import { View, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/atoms';
import { SubscriptionPlanResponse, SubscriptionResponse } from '@/types/server-types';
import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type SubscriptionPlansProps = {
  plans: SubscriptionPlanResponse[];
  activeSubscription?: SubscriptionResponse | null;
  onSubscribe: (plan: SubscriptionPlanResponse) => void;
  onCancel: (subscriptionId: number) => void;
  onRenew: (subscriptionId: number) => void;
  loadingPlan?: string | null;
};

const DEFAULT_PLANS: SubscriptionPlanResponse[] = [
  {
    name: 'monthly',
    label: 'Monthly',
    description: 'Monthly subscription with full access to all premium features',
    price_cents: 999,
    interval: 'month',
  },
  {
    name: 'yearly',
    label: 'Yearly',
    description: 'Yearly subscription with full access and 2 months free',
    price_cents: 9999,
    interval: 'year',
  },
];

export function SubscriptionPlans({
  plans,
  activeSubscription,
  onSubscribe,
  onCancel,
  onRenew,
  loadingPlan,
}: SubscriptionPlansProps) {
  const theme = useTheme();
  const displayPlans = plans.length > 0 ? plans : DEFAULT_PLANS;

  // Check if subscription is truly active (status === 'active')
  const isSubscriptionActive = activeSubscription?.status === 'active';

  return (
    <View style={styles.container}>
      {displayPlans.map((plan) => {
        const isActive = isSubscriptionActive && activeSubscription?.plan === plan.name;
        const isLoading = loadingPlan === plan.name || loadingPlan === 'subscribe';
        return (
          <View
            key={plan.name}
            style={[
              styles.planCard,
              isActive && styles.activePlanCard,
              isActive && { borderColor: theme.primary },
            ]}
          >
            <View style={styles.planHeader}>
              <ThemedText type="smallBold">{plan.label}</ThemedText>
              {isActive && (
                <View style={[styles.activeBadge, { backgroundColor: theme.primary }]}>
                  <ThemedText type="small" style={{ color: '#fff' }}>Active</ThemedText>
                </View>
              )}
            </View>
            <ThemedText type="small" themeColor="textSecondary">{plan.description}</ThemedText>
            <ThemedText type="smallBold">${(plan.price_cents / 100).toFixed(2)} / {plan.interval}</ThemedText>

            {isActive ? (
              <View style={styles.actions}>
                <Button
                  title="Cancel"
                  variant="outline"
                  size="small"
                  onPress={() => activeSubscription && onCancel(activeSubscription.id)}
                  disabled={isLoading}
                />
                <Button
                  title="Renew"
                  variant="secondary"
                  size="small"
                  onPress={() => activeSubscription && onRenew(activeSubscription.id)}
                  disabled={isLoading}
                />
              </View>
            ) : (
              <Button
                title={activeSubscription ? 'Switch Plan' : 'Choose Plan'}
                size="small"
                onPress={() => onSubscribe(plan)}
                disabled={isLoading}
              />
            )}
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: Spacing.three,
  },
  planCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
    gap: Spacing.two,
  },
  activePlanCard: {
    borderWidth: 2,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  activeBadge: {
    paddingHorizontal: Spacing.two,
    paddingVertical: Spacing.one,
    borderRadius: Spacing.two,
  },
  actions: {
    flexDirection: 'row',
    gap: Spacing.two,
    marginTop: Spacing.one,
  },
});