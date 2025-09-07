# Row-Level Security (RLS) Policy

## Overview
All multi-tenant tables in the `core` schema enforce Row-Level Security (RLS) to ensure complete tenant isolation.

## Implementation

### 1. Tenant Context Setting
Applications MUST set the tenant context before any operations:
```sql
SELECT set_config('app.tenant_id', 'GSG', true);
SELECT set_config('app.user_id', 'user@example.com', true);
```

### 2. RLS Rules

#### Core Tables
- **Tenant Isolation**: Records are only visible if `tenant_id = current_setting('app.tenant_id')`
- **Insert Protection**: New records must have `tenant_id = current_setting('app.tenant_id')`
- **No Cross-Tenant Access**: Even with direct SQL, users cannot see other tenants' data

#### Memory Tables
- **Tenant + Global Access**: Records visible if `tenant_id = current_tenant` OR `scope = 'global'`
- **Scoped Access**: Additional filtering by `scope` (global, project:*, agent:*)
- **Write Protection**: Can only insert/update own tenant's data

#### Reference Tables
- **Read-Only**: All users can read, no one can modify
- **No RLS**: Reference data is shared across all tenants

## Enforcement

### Database Level
```sql
ALTER TABLE core.{table} ENABLE ROW LEVEL SECURITY;
CREATE POLICY {table}_tenant_isolation ON core.{table}
    USING (tenant_id = core.current_tenant_id());
```

### Application Level
- Connection pools must set tenant context
- API middleware validates and sets tenant from JWT
- Background jobs explicitly set tenant context

## Testing

### Verification Steps
1. Create test data for multiple tenants
2. Connect as different tenant roles
3. Verify isolation with SELECT queries
4. Test INSERT/UPDATE/DELETE operations
5. Confirm cross-tenant operations fail

### Test Queries
```sql
-- As app_gsg
SELECT set_config('app.tenant_id', 'GSG', true);
SELECT COUNT(*) FROM core.document; -- Only GSG documents

-- As app_demo  
SELECT set_config('app.tenant_id', 'DEMO', true);
SELECT COUNT(*) FROM core.document; -- Only DEMO documents

-- Attempt cross-tenant insert (should fail)
INSERT INTO core.document (tenant_id, doc_id, doc_type)
VALUES ('OTHER', 'test', 'test'); -- ERROR
```

## Exceptions

### System Operations
- Migration scripts run as superuser (bypass RLS)
- DataHub metadata collection uses read-only service account
- Backup/restore operations bypass RLS

### Global Data
- Memory KV/docs with `scope = 'global'` are visible to all
- Reference data has no RLS (shared across tenants)
- Bridge control tables use service accounts

## Monitoring

### Audit Queries
```sql
-- Check for RLS violations (should return 0)
SELECT COUNT(*) FROM core.document 
WHERE tenant_id != current_setting('app.tenant_id', true);

-- Monitor tenant activity
SELECT tenant_id, COUNT(*), MAX(created_at)
FROM bridge.event_registry
GROUP BY tenant_id
ORDER BY MAX(created_at) DESC;
```

## Compliance
- **GDPR**: Tenant isolation ensures data minimization
- **SOC2**: RLS provides logical access controls
- **ISO27001**: Enforces data classification boundaries