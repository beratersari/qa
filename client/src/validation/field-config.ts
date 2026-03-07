import { z } from 'zod';

/**
 * Field types supported by the form system
 */
export type FieldType =
  | 'email'
  | 'password'
  | 'text'
  | 'confirmPassword'
  | 'username'
  | 'fullName'
  | 'profileBio'
  | 'profileContact';

/**
 * Configuration for each field type
 */
export interface FieldConfig {
  name: string;
  label: string;
  placeholder: string;
  autoCapitalize: 'none' | 'sentences' | 'words' | 'characters';
  autoCorrect: boolean;
  keyboardType: 'default' | 'email-address' | 'visible-password' | 'ascii-capable';
  secureTextEntry: boolean;
  validation: z.ZodString;
}

/**
 * Email validation configuration
 */
const emailConfig: FieldConfig = {
  name: 'email',
  label: 'Email',
  placeholder: 'Enter your email',
  autoCapitalize: 'none',
  autoCorrect: false,
  keyboardType: 'email-address',
  secureTextEntry: false,
  validation: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address')
    .max(255, 'Email must be less than 255 characters')
    .refine(
      (email) => !email.includes('..'),
      'Email cannot contain consecutive dots'
    )
    .refine(
      (email) => !email.startsWith('.') && !email.endsWith('.'),
      'Email cannot start or end with a dot'
    ),
};

/**
 * Password validation configuration
 */
const passwordConfig: FieldConfig = {
  name: 'password',
  label: 'Password',
  placeholder: 'Enter your password',
  autoCapitalize: 'none',
  autoCorrect: false,
  keyboardType: 'default',
  secureTextEntry: true,
  validation: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be less than 128 characters')
    .refine(
      (password) => /[a-z]/.test(password),
      'Password must contain at least one lowercase letter'
    )
    .refine(
      (password) => /[A-Z]/.test(password),
      'Password must contain at least one uppercase letter'
    )
    .refine(
      (password) => /[0-9]/.test(password),
      'Password must contain at least one number'
    )
    .refine(
      (password) => /[!@#$%^&*(),.?":{}|<>]/.test(password),
      'Password must contain at least one special character'
    ),
};

/**
 * Confirm password validation configuration
 * Note: This requires access to the password field value for comparison
 */
const confirmPasswordConfig: Omit<FieldConfig, 'validation'> & { validation: (passwordRef: string) => z.ZodString } = {
  name: 'confirmPassword',
  label: 'Confirm Password',
  placeholder: 'Confirm your password',
  autoCapitalize: 'none',
  autoCorrect: false,
  keyboardType: 'default',
  secureTextEntry: true,
  validation: (passwordRef: string) =>
    z
      .string()
      .min(1, 'Please confirm your password')
      .refine(
        (confirmPassword) => confirmPassword === passwordRef,
        'Passwords do not match'
      ),
};

/**
 * Text field validation configuration (for general text inputs)
 */
const textConfig: FieldConfig = {
  name: 'text',
  label: 'Text',
  placeholder: 'Enter text',
  autoCapitalize: 'sentences',
  autoCorrect: true,
  keyboardType: 'default',
  secureTextEntry: false,
  validation: z.string().min(1, 'This field is required'),
};

/**
 * Username validation configuration
 */
const usernameConfig: FieldConfig = {
  name: 'username',
  label: 'Username',
  placeholder: 'Enter your username',
  autoCapitalize: 'none',
  autoCorrect: false,
  keyboardType: 'default',
  secureTextEntry: false,
  validation: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters')
    .regex(/^[a-zA-Z0-9._-]+$/, 'Username can contain letters, numbers, dots, underscores, and dashes'),
};

/**
 * Full name validation configuration
 */
const fullNameConfig: FieldConfig = {
  name: 'fullName',
  label: 'Full Name',
  placeholder: 'Enter your full name',
  autoCapitalize: 'words',
  autoCorrect: false,
  keyboardType: 'default',
  secureTextEntry: false,
  validation: z
    .string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'Full name can only include letters, spaces, apostrophes, and hyphens'),
};

const profileBioConfig: FieldConfig = {
  name: 'profileBio',
  label: 'Bio',
  placeholder: 'Tell us about yourself',
  autoCapitalize: 'sentences',
  autoCorrect: true,
  keyboardType: 'default',
  secureTextEntry: false,
  validation: z.string().max(500, 'Bio must be less than 500 characters').optional().or(z.literal('')),
};

const profileContactConfig: FieldConfig = {
  name: 'profileContact',
  label: 'Contact Info',
  placeholder: 'Add your contact details',
  autoCapitalize: 'sentences',
  autoCorrect: true,
  keyboardType: 'default',
  secureTextEntry: false,
  validation: z
    .string()
    .max(200, 'Contact info must be less than 200 characters')
    .optional()
    .or(z.literal('')),
};

/**
 * Map of field types to their configurations
 */
export const fieldConfigs: Record<FieldType, FieldConfig> = {
  email: emailConfig,
  password: passwordConfig,
  confirmPassword: passwordConfig as FieldConfig, // Will be overridden when used
  text: textConfig,
  username: usernameConfig,
  fullName: fullNameConfig,
  profileBio: profileBioConfig,
  profileContact: profileContactConfig,
};

/**
 * Get field configuration by type
 */
export function getFieldConfig(type: FieldType, passwordValue?: string): FieldConfig {
  if (type === 'confirmPassword' && passwordValue !== undefined) {
    return {
      ...confirmPasswordConfig,
      validation: confirmPasswordConfig.validation(passwordValue),
    } as FieldConfig;
  }
  return fieldConfigs[type];
}

/**
 * Create Zod schema for login form
 */
export function createLoginSchema() {
  return z.object({
    username: usernameConfig.validation,
    password: z.string().min(1, 'Password is required'),
  });
}

/**
 * Create Zod schema for registration form
 */
export function createRegistrationSchema() {
  return z
    .object({
      email: emailConfig.validation,
      username: usernameConfig.validation,
      fullName: fullNameConfig.validation.optional(),
      password: passwordConfig.validation,
      confirmPassword: z.string().min(1, 'Please confirm your password'),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: 'Passwords do not match',
      path: ['confirmPassword'],
    });
}

/**
 * Login form type derived from schema
 */
export type LoginFormData = z.infer<ReturnType<typeof createLoginSchema>>;

/**
 * Registration form type derived from schema
 */
export type RegistrationFormData = z.infer<ReturnType<typeof createRegistrationSchema>>;

/**
 * Generic form field names type
 */
export type FieldName = string;