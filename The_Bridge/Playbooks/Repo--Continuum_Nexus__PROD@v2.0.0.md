# Repository Playbook: Continuum_Nexus
## Version: 2.0.0 | Classification: PROD

### Branch Strategy
- `main` → PROD (production)
- `stage` → STAGE (staging)  
- `dev` → DEV (development)
- `feature/*` → feature branches

### Deployment Flow
```
C_O (local) → GitHub → C_N (AWS)
           ↓
    OIDC Auth (no keys!)
           ↓
    Environment Gates
           ↓
    Path-filtered Deploys
```

### CI/CD Rules
1. **Infrastructure**: Changes to The_Bridge/Oracle/Forge/Atlas/Aegis trigger `infra.yml`
2. **Web**: Changes to Agora/ handled by Amplify auto-build
3. **Docs**: Changes to *.md don't trigger deploys

### Environment Protection
- `prod`: Requires manual approval
- `stage`: Auto-deploys after tests
- `dev`: Instant deploy, no gates

### OIDC Configuration
- Role: `arn:aws:iam::086143043656:role/C_N-GitHubDeployRole`
- No static AWS keys in secrets
- Token-based authentication only

### Required Reviews
- Production: 1 approval required
- Infrastructure changes: The_Bridge team review
- Security changes: Aegis team review