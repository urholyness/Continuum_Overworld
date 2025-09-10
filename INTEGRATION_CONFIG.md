# Integration Configuration - Helios+Site v1.1.0

## Lead Engineer Review Gate - APPROVED ✅

### Infrastructure Configuration

* **✅ Tenant model**: Single tenant `org-main` for all environments
* **✅ Region**: `us-east-1` (consistent with existing Amplify apps)
* **✅ Root domain**: `greenstemglobal.com` (confirmed from existing GSG site)

### Domains Mapping

* **APIs**:
  * DEV: `cn-dev-api.greenstemglobal.com`
  * STAGE: `cn-stage-api.greenstemglobal.com`
  * PROD: `cn-api.greenstemglobal.com`

* **Helios Console**:
  * DEV: `cn-dev-helios.greenstemglobal.com`
  * STAGE: `cn-stage-helios.greenstemglobal.com`
  * PROD: `cn-helios.greenstemglobal.com`

* **Website**:
  * STAGE: `stage.greenstemglobal.com`
  * PROD: `www.greenstemglobal.com`

### Security & Compliance

* **✅ IAM boundary policy**: `Aegis/IAM/boundary-policy.json`
* **✅ Data retention**: Metrics 90d, Events 30d, PITR enabled
* **✅ Cost alarms**: $90/month account budget threshold
* **✅ Cognito callbacks**: Helios Console only (no marketing site callbacks)

### Callback URLs Configuration

* **Helios Console**:
  * `http://localhost:3000/api/auth/callback` (dev)
  * `https://cn-dev-helios.greenstemglobal.com/api/auth/callback`
  * `https://cn-stage-helios.greenstemglobal.com/api/auth/callback`
  * `https://cn-helios.greenstemglobal.com/api/auth/callback`

* **Website**: No callbacks (public trace highlights only)

## Validated Architecture

### API Endpoints
- **Composer API**: `/composer/ops/metrics`, `/composer/trace/events`
- **Admin API**: `/admin/farms`, `/admin/farms:batch`, `/admin/agents`
- **Public API**: `/public/trace/highlights` (anonymized, delayed)

### DynamoDB Tables
- `C_N-Metrics-Operational` (operational KPIs)
- `C_N-Events-Trace` (audit trail events)
- `C_N-Registry-Farms` (farm configurations)
- `C_N-Pantheon-Registry` (agent status - read-only)

### Authentication
- **Cognito User Pool** with groups: `admin`, `ops`, `trace`
- **JWT Authorizer** for API Gateway
- **Role-based access control** enforced at route level

---

**Configuration Status**: ✅ APPROVED FOR IMPLEMENTATION  
**Next Phase**: Begin infrastructure deployment