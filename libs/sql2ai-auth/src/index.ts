/**
 * SQL2AI Auth Library
 *
 * Authentication and authorization
 * with JWT, OAuth, and RBAC support.
 */

// Authentication interfaces
export interface AuthResult {
  success: boolean;
  user?: User;
  token?: string;
  refreshToken?: string;
  expiresAt?: Date;
  error?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  roles: string[];
  tenantId?: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

export interface TokenPayload {
  sub: string;
  email: string;
  roles: string[];
  tenantId?: string;
  iat: number;
  exp: number;
}

export interface IAuthProvider {
  authenticate(credentials: Credentials): Promise<AuthResult>;
  validateToken(token: string): Promise<TokenPayload | null>;
  refreshToken(refreshToken: string): Promise<AuthResult>;
  revokeToken(token: string): Promise<void>;
}

export type Credentials =
  | { type: 'password'; email: string; password: string }
  | { type: 'oauth'; provider: string; code: string }
  | { type: 'apikey'; key: string };

// Authorization interfaces
export interface Permission {
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete' | 'execute' | '*';
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: Permission[];
}

export interface IAuthorizationService {
  isAuthorized(userId: string, resource: string, action: string): Promise<boolean>;
  getUserRoles(userId: string): Promise<Role[]>;
  getUserPermissions(userId: string): Promise<Permission[]>;
  hasPermission(user: User, permission: Permission): boolean;
}

// Multi-tenancy interfaces
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  settings: Record<string, unknown>;
  status: 'active' | 'suspended' | 'deleted';
  createdAt: Date;
}

export interface ITenantService {
  getCurrentTenant(): Tenant | undefined;
  setCurrentTenant(tenant: Tenant): void;
  getTenantById(id: string): Promise<Tenant | null>;
  getTenantBySlug(slug: string): Promise<Tenant | null>;
  getUserTenants(userId: string): Promise<Tenant[]>;
}

// Session interfaces
export interface Session {
  id: string;
  userId: string;
  tenantId?: string;
  token: string;
  userAgent?: string;
  ipAddress?: string;
  expiresAt: Date;
  createdAt: Date;
}

export interface ISessionService {
  create(userId: string, options?: SessionOptions): Promise<Session>;
  get(sessionId: string): Promise<Session | null>;
  validate(token: string): Promise<Session | null>;
  revoke(sessionId: string): Promise<void>;
  revokeAll(userId: string): Promise<void>;
}

export interface SessionOptions {
  tenantId?: string;
  expiresInSeconds?: number;
  userAgent?: string;
  ipAddress?: string;
}

// API Key interfaces
export interface ApiKey {
  id: string;
  userId: string;
  name: string;
  keyHash: string;
  prefix: string;
  scopes: string[];
  expiresAt?: Date;
  lastUsedAt?: Date;
  createdAt: Date;
}

export interface IApiKeyService {
  create(userId: string, name: string, scopes: string[]): Promise<{ apiKey: ApiKey; key: string }>;
  validate(key: string): Promise<ApiKey | null>;
  revoke(keyId: string): Promise<void>;
  list(userId: string): Promise<ApiKey[]>;
}

// Re-export implementations (to be added)
// export { JwtAuthProvider } from './providers/JwtAuthProvider';
// export { OAuthProvider } from './providers/OAuthProvider';
// export { RoleBasedAuthorizationService } from './services/RoleBasedAuthorizationService';
// export { TenantService } from './services/TenantService';
// export { SessionService } from './services/SessionService';
// export { ApiKeyService } from './services/ApiKeyService';
