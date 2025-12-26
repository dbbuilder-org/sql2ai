# SQL2.AI Security Architecture

## Executive Summary

SQL2.AI is a multi-tenant SaaS platform that handles highly sensitive data including database credentials, connection strings, and customer schema information. This document describes our security architecture designed to protect customer data while enabling the platform's AI-powered database development features.

---

## Core Security Principles

### 1. Zero Trust by Default
- No component trusts another without verification
- All API requests require authentication
- Internal services use mutual TLS
- Every action is logged for audit

### 2. Tenant Isolation
- Complete data isolation between tenants
- Database-level Row Level Security (RLS)
- Tenant-scoped encryption keys
- No cross-tenant data leakage possible

### 3. Defense in Depth
- Multiple layers of security controls
- Encryption at rest AND in transit
- Access controls at every layer
- Regular security audits and penetration testing

---

## Credential Protection: Envelope Encryption

### The Problem
Customers store database credentials in SQL2.AI to enable schema analysis, query execution, and migrations. These credentials are "keys to the kingdom" - if compromised, attackers could access customer databases directly.

### Our Solution: Envelope Encryption

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENVELOPE ENCRYPTION FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Customer Credential (e.g., database password)                  │
│              │                                                   │
│              ▼                                                   │
│   ┌─────────────────────┐                                       │
│   │   Data Encryption    │  ◀── Unique per-tenant               │
│   │    Key (DEK)        │      Generated fresh for each         │
│   └─────────────────────┘      encryption operation             │
│              │                                                   │
│              ▼                                                   │
│   ┌─────────────────────┐                                       │
│   │  ENCRYPTED CREDENTIAL│  Stored in database                  │
│   └─────────────────────┘                                       │
│                                                                  │
│   DEK itself is encrypted:                                       │
│              │                                                   │
│              ▼                                                   │
│   ┌─────────────────────┐                                       │
│   │   Key Encryption     │  ◀── Stored in Azure Key Vault       │
│   │    Key (KEK)        │      or AWS KMS (HSM-backed)          │
│   └─────────────────────┘                                       │
│              │                                                   │
│              ▼                                                   │
│   ┌─────────────────────┐                                       │
│   │   ENCRYPTED DEK     │  Stored alongside credential          │
│   └─────────────────────┘                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Data Encryption Key (DEK)
- **What**: 256-bit AES symmetric key
- **Scope**: Unique per-tenant
- **Lifetime**: Generated for each encryption, cached briefly (5 min)
- **Storage**: Never stored in plaintext; always encrypted by KEK

#### 2. Key Encryption Key (KEK)
- **What**: RSA-2048 or AES-256 key in HSM
- **Scope**: One per tenant, stored in KMS
- **Lifetime**: Rotated annually (configurable)
- **Storage**: Azure Key Vault or AWS KMS (never leaves HSM)

### Why This Approach?

| Threat | Mitigation |
|--------|------------|
| Database breach | Credentials are encrypted; DEKs are also encrypted |
| Stolen DEK | DEK is useless without KEK from KMS |
| Compromised API server | KEK is in HSM; requires KMS authentication |
| Insider threat | All decryption logged; requires active session |
| Key compromise | Tenant keys are isolated; rotation supported |

---

## Session-Bound Decryption

Credentials are ONLY decrypted when:

1. **User is authenticated** - Valid JWT from Clerk
2. **User belongs to tenant** - Verified against organization membership
3. **Request is active** - Happens in request context, not background
4. **Operation is authorized** - User has required permissions

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECRYPTION AUTHORIZATION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. User Request → Verify JWT Token                            │
│              │                                                   │
│              ▼                                                   │
│   2. Check tenant membership (user.org_id == credential.tenant) │
│              │                                                   │
│              ▼                                                   │
│   3. Check permissions (connections:read or higher)             │
│              │                                                   │
│              ▼                                                   │
│   4. Request KEK from KMS (using managed identity)              │
│              │                                                   │
│              ▼                                                   │
│   5. Decrypt DEK → Decrypt credential → Use immediately         │
│              │                                                   │
│              ▼                                                   │
│   6. Log access for audit trail                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Managed Identity for KMS Access

In production, the API server uses a managed identity (Azure AD or AWS IAM Role) to access KMS. This means:

- No secrets stored on the server
- Credentials rotate automatically
- Access is tied to the infrastructure identity
- Easy to revoke if server is compromised

---

## Multi-Tenant Data Isolation

### Row-Level Security (RLS)

Every database table with tenant data has RLS policies:

```sql
-- Example: Connections table
CREATE POLICY tenant_isolation ON connections
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The API sets the tenant context on every request:
```python
async def set_tenant_context(db: AsyncSession, tenant_id: str):
    await db.execute(text(f"SET app.tenant_id = '{tenant_id}'"))
```

### Tenant Verification Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EVERY API REQUEST                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Auth Middleware extracts JWT                               │
│              │                                                   │
│              ▼                                                   │
│   2. Verify JWT signature with Clerk JWKS                       │
│              │                                                   │
│              ▼                                                   │
│   3. Extract user_id and org_id (tenant)                        │
│              │                                                   │
│              ▼                                                   │
│   4. Set request.state.tenant_id                                │
│              │                                                   │
│              ▼                                                   │
│   5. Database session uses RLS with tenant context              │
│              │                                                   │
│              ▼                                                   │
│   6. User can ONLY see their tenant's data                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Role-Based Access Control (RBAC)

### Roles Hierarchy

| Role | Level | Description |
|------|-------|-------------|
| Owner | 5 | Full access, billing, can delete org |
| Admin | 4 | User management, settings, all features |
| DBA | 3 | Full database access, migrations, compliance |
| Developer | 2 | Read connections, execute queries, AI features |
| Viewer | 1 | Read-only access to connections and schema |

### Permissions Matrix

| Permission | Owner | Admin | DBA | Dev | Viewer |
|------------|-------|-------|-----|-----|--------|
| connections:read | ✓ | ✓ | ✓ | ✓ | ✓ |
| connections:write | ✓ | ✓ | ✓ | - | - |
| connections:delete | ✓ | ✓ | ✓ | - | - |
| queries:execute | ✓ | ✓ | ✓ | ✓ | ✓ |
| queries:execute_ddl | ✓ | ✓ | ✓ | - | - |
| queries:execute_dml | ✓ | ✓ | ✓ | ✓ | - |
| schema:read | ✓ | ✓ | ✓ | ✓ | ✓ |
| migrations:execute | ✓ | ✓ | ✓ | - | - |
| admin:users | ✓ | ✓ | - | - | - |
| admin:billing | ✓ | - | - | - | - |

---

## Compliance Considerations

### SOC 2 Type II

Our encryption architecture supports SOC 2 requirements:

- **CC6.1**: Encryption of data at rest (AES-256)
- **CC6.6**: Encryption in transit (TLS 1.3)
- **CC6.7**: Access logging and audit trails
- **CC7.1**: Activity monitoring

### HIPAA

For healthcare customers handling PHI:

- **164.312(a)(1)**: Access controls via RBAC
- **164.312(a)(2)(iv)**: Encryption mechanisms
- **164.312(b)**: Audit controls
- **164.312(e)(1)**: Transmission security

### GDPR

For EU customers:

- **Article 32**: Appropriate technical measures (encryption)
- **Article 33**: Breach notification (audit logging enables detection)
- Data residency options (tenant-specific regions)

---

## Key Rotation

### Automatic Rotation

KEKs are automatically rotated annually:

```
┌─────────────────────────────────────────────────────────────────┐
│                      KEY ROTATION                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Year 1: KEK v1 encrypts all DEKs                              │
│              │                                                   │
│              ▼                                                   │
│   Year 2: KEK v2 created, new encryptions use v2                │
│           Old credentials still decrypt with v1                  │
│              │                                                   │
│              ▼                                                   │
│   Background job re-encrypts old credentials with v2            │
│              │                                                   │
│              ▼                                                   │
│   KEK v1 retired after all credentials migrated                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Manual Rotation

Admins can trigger immediate rotation:

```bash
# CLI command for emergency rotation
sql2ai admin rotate-keys --tenant <tenant-id> --reason "security incident"
```

---

## Incident Response

### If a Credential is Potentially Compromised

1. **Rotate tenant KEK** - Invalidates cached DEKs
2. **Re-encrypt all credentials** - Uses new KEK
3. **Customer notification** - Via Clerk + email
4. **Audit review** - Check all access logs

### If API Server is Compromised

1. **Revoke managed identity** - Cuts off KMS access
2. **Rotate all KEKs** - Even though they weren't exposed
3. **Deploy new infrastructure** - Fresh managed identity
4. **Forensic analysis** - Determine exposure scope

---

## Implementation Files

| File | Purpose |
|------|---------|
| `apps/api/src/security/encryption.py` | Encryption service, envelope encryption |
| `apps/api/src/middleware/auth.py` | JWT verification, session management |
| `apps/api/src/dependencies/auth.py` | RBAC, permissions |
| `apps/api/src/routers/webhooks/clerk.py` | User/org lifecycle events |

---

## Questions for PMs

### When discussing with customers:

1. **"How do you protect my database credentials?"**
   - Envelope encryption with HSM-backed keys
   - Each tenant has isolated encryption keys
   - Credentials never stored in plaintext

2. **"What if your database is breached?"**
   - Credentials are encrypted with tenant-specific keys
   - Those keys are also encrypted in cloud HSM
   - Attacker would need to compromise both + KMS access

3. **"Can your employees see my credentials?"**
   - No. Decryption requires tenant context
   - All access is logged and audited
   - Emergency access requires documented approval

4. **"Are you compliant with X?"**
   - SOC 2 Type II: Yes (or in progress)
   - HIPAA: Available for Business Associate Agreement
   - GDPR: Compliant with EU data residency options

---

## Future Enhancements

1. **Customer-Managed Keys (CMK)** - Let enterprises bring their own KMS keys
2. **Hardware Security Modules (HSM)** - On-premise HSM integration for regulated industries
3. **Zero-Knowledge Encryption** - Client-side encryption where we never see plaintext
4. **Credential Access Policies** - Time-based, IP-based restrictions

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Author: SQL2.AI Engineering*
