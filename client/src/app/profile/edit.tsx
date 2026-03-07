import React, { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, StyleSheet, Switch, View } from 'react-native';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { ControlledInput } from '@/components/molecules';
import { Button, ServerError } from '@/components/atoms';
import { useGetMyProfileQuery, useUpdateMyProfileMutation } from '@/services/user-api';
import { ProfileVisibility } from '@/types/server-types';
import { Spacing } from '@/constants/theme';

const profileSchema = z.object({
  fullName: z
    .string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'Full name can only include letters, spaces, apostrophes, and hyphens'),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  contactInfo: z.string().max(200, 'Contact info must be less than 200 characters').optional(),
  profileVisibility: z.enum(['public', 'private']),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export default function EditProfileScreen() {
  const router = useRouter();
  const { data: profile, isLoading } = useGetMyProfileQuery();
  const [updateProfile, { isLoading: isSaving }] = useUpdateMyProfileMutation();
  const [serverError, setServerError] = useState<string | null>(null);

  const { control, handleSubmit, reset, watch } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    mode: 'onChange',
    defaultValues: {
      fullName: '',
      bio: '',
      contactInfo: '',
      profileVisibility: 'private',
    },
  });

  useEffect(() => {
    if (profile) {
      reset({
        fullName: profile.full_name ?? '',
        bio: profile.bio ?? '',
        contactInfo: profile.contact_info ?? '',
        profileVisibility: profile.profile_visibility ?? 'private',
      });
    }
  }, [profile, reset]);

  const handleSave = handleSubmit(async (data) => {
    setServerError(null);

    try {
      await updateProfile({
        full_name: data.fullName,
        bio: data.bio || null,
        contact_info: data.contactInfo || null,
        profile_visibility: data.profileVisibility as ProfileVisibility,
      }).unwrap();

      router.back();
    } catch (error) {
      if (error instanceof Error) {
        setServerError(error.message || 'Unable to update profile.');
      } else {
        setServerError('Unable to update profile.');
      }
    }
  });

  if (isLoading || !profile) {
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
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <ThemedText type="subtitle">Edit Profile</ThemedText>
          <ServerError message={serverError} />

          <ControlledInput
            control={control}
            name="fullName"
            fieldType="fullName"
            label="Full Name"
          />
          <ControlledInput
            control={control}
            name="bio"
            fieldType="profileBio"
          />
          <ControlledInput
            control={control}
            name="contactInfo"
            fieldType="profileContact"
          />

          <View style={styles.toggleRow}>
            <View>
              <ThemedText type="smallBold">Profile Visibility</ThemedText>
              <ThemedText type="small">{watch('profileVisibility') === 'public' ? 'Public profile' : 'Private profile'}</ThemedText>
            </View>
            <Controller
              control={control}
              name="profileVisibility"
              render={({ field: { value, onChange } }) => (
                <Switch
                  value={value === 'public'}
                  onValueChange={(nextValue) => onChange(nextValue ? 'public' : 'private')}
                />
              )}
            />
          </View>

          <Button
            title="Save Changes"
            onPress={handleSave}
            loading={isSaving}
            fullWidth
          />
          <Button
            title="Cancel"
            onPress={() => router.back()}
            variant="outline"
            fullWidth
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
  scrollContent: {
    paddingVertical: Spacing.three,
    gap: Spacing.two,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.two,
    borderRadius: Spacing.two,
    backgroundColor: 'rgba(255, 178, 178, 0.2)',
  },
});