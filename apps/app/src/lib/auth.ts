/**
 * Authentication utilities for SQL2.AI
 *
 * Uses Clerk for authentication and authorization
 */

import { auth, currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

/**
 * Get the current authenticated user or redirect to sign-in
 */
export async function requireAuth() {
  const { userId } = auth();

  if (!userId) {
    redirect('/sign-in');
  }

  return userId;
}

/**
 * Get the current user with full profile data
 */
export async function getUser() {
  const user = await currentUser();

  if (!user) {
    return null;
  }

  return {
    id: user.id,
    email: user.emailAddresses[0]?.emailAddress,
    firstName: user.firstName,
    lastName: user.lastName,
    fullName: `${user.firstName || ''} ${user.lastName || ''}`.trim(),
    imageUrl: user.imageUrl,
    createdAt: user.createdAt,
  };
}

/**
 * Get organization info for the current user
 */
export async function getOrganization() {
  const { orgId, orgRole, orgSlug } = auth();

  if (!orgId) {
    return null;
  }

  return {
    id: orgId,
    role: orgRole,
    slug: orgSlug,
  };
}

/**
 * Check if user has a specific role
 */
export function hasRole(role: string) {
  const { orgRole } = auth();
  return orgRole === role;
}

/**
 * Check if user is an admin
 */
export function isAdmin() {
  return hasRole('admin') || hasRole('owner');
}
