# Agora/Playbook--WebDev__PROD@v2.0.0

**Owner**: The_Bridge (Naivasha / Number_1)  
**Risk Gate**: Aegis:T1 (compliance + security checks before deploy)  
**SLA**: Every PR → must follow this rulebook

## 1. Naming & Structure

Use Pascal_Snake for system objects, kebab-case for files, SCREAMING_SNAKE for envs.

Respect division folders: The_Bridge, Agora, Forge, Oracle, Pantheon, Atlas, Aegis, Meridian, Ledger, Archive.

**Example:**
- `Agora/Site--GreenStemGlobal__PROD@v2.0.0`
- Env var: `NEXT_PUBLIC_MAPBOX_TOKEN`

## 2. Environment

`.env.template` is mandatory → updated with every new var.

`.env.local` → used only in dev, never committed.

Use `continuum_config.yaml` for C_O → C_N mappings.

**Branches:**
- `main` = PROD
- `stage` = STAGE  
- `dev` = active build
- Features = `lab/<feature>`

## 3. Deployment Workflow

Deploy via `deploy_to_nexus.sh`.

Run `verify_setup.sh` before merge.

Never push directly via AWS console unless a WO allows.

## 4. Frontend Rules

**Stack**: Next.js 14, TypeScript, Tailwind, shadcn/ui.

Use atomic components: `components/ui/`, `components/core/`.

**Approved pages**: `/`, `/buyers`, `/investors`, `/about`, `/contact`.

No mock data unless cleared by The_Bridge.

## 5. Backend Rules

**Language**: TypeScript (Node.js).

**API**: REST (+ GraphQL optional).

**Storage**: DynamoDB + S3.

**Logs**: CloudWatch, no `console.log` in production.

**Validation**: Zod schema required for all payloads.

**Secrets**: AWS Secrets Manager only.

## 6. Git Rules

**Commit format**: `[Division/Capability] — <summary>`

**Example**: `[Agora/Site] — Added buyers traceability mock`

**PR must include:**
- Setup verification logs
- Updated docs if new service added

`.gitignore` must include `/node_modules`, `.next/`, `.env.local`, build artifacts.

## 7. Quality Gates

**Tests required:**
- Frontend: Jest + React Testing Library
- Backend: Jest + Supertest

**CI/CD pipeline** = Lint → Test → Verify → Deploy.

**Aegis veto** = no deploy without tests/docs.

## 8. Documentation

Each new service = `README.md` with:

```php
# <Division>/<Capability>--<Role>__<Qualifier>@vX.Y.Z
Purpose → Context → Inputs → Outputs → Guardrails → Ownership
```

Deployment notes must go in `The_Bridge/Playbooks/`.

## 9. Golden Rules

1. Do not break naming grammar.
2. Never deploy without verification.
3. Placeholders only, no mocks unless approved.
4. Document or it didn't happen.
5. Security > Speed (Aegis always wins).

---

**Document Version**: v2.0.0  
**Last Updated**: 2025-09-10  
**Governance**: The_Bridge oversight, Aegis security gate