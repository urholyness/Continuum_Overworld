# Continuum_Overworld

Single source of naming truth. Governed by THE_BRIDGE — Naming & Operating Standard v1.0.

## Environment Architecture

- **Claude Code**: Operating in WSL2 (`/mnt/c/users/password/`)
- **Cursor**: Operating in Windows (`C:\Users\Password\`)
- **Shared Filesystem**: Windows drives mounted at `/mnt/c/` in WSL2

## Quick Start

### From WSL2 (Claude Code):
```bash
bash scripts/mk-structure.sh
python3 scripts/bridge-validate.py
```

### From Windows (Cursor/User):
```batch
scripts\mk-structure.bat
python scripts\bridge-validate.py
```

## Division Structure

- **The_Bridge**: Control surface and governance
- **Pantheon**: Agent registry and lifecycle
- **Aegis**: Risk, compliance, validation
- **Atlas**: Planning and logistics
- **Forge**: Building and implementation
- **Oracle**: Forecasting and analysis
- **Meridian**: Notifications and alerts
- **Agora**: Outreach and communication
- **Ledger**: Contracts and records
- **Archive**: Deferred items

## Naming Convention

- Divisions: `Pascal_Snake`
- Files: `kebab-case`
- Versioned: `Component--Role__Qualifier@v<MAJOR>.<MINOR>.<PATCH>`
