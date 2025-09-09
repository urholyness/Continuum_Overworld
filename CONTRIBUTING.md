# Commit Message Guidelines for Continuum_Overworld

## Rules for AWS Amplify Compatibility

DO NOT use these characters in commit messages:
- `:` (colon)
- `|` (pipe)
- `>` (greater-than)
- `&` (ampersand)
- `*` (asterisk)
- `@` (at symbol in excess)

## Good Examples
- "Add farm validation Lambda with geospatial indexing"
- "Update DynamoDB tables for KMS encryption"
- "Fix build configuration for Amplify deployment"

## Bad Examples
- "feat: Add new feature" (colon breaks YAML)
- "Update config | Deploy to prod" (pipe breaks YAML)
- "Fix: KMS::PROD settings" (multiple colons)

## Safe Characters
- Letters and numbers
- Spaces
- Dashes (-)
- Underscores (_)
- Periods (.)
- Commas (,)

Keep commit messages simple and descriptive without special formatting.

## Deployment Process
1. Always test changes locally before pushing
2. Use `git commit --allow-empty -m "message"` for deployment triggers
3. Keep messages under 50 characters when possible
4. Describe what was changed, not how it was changed

## Emergency Fixes
For urgent deployment fixes:
- Use simple, clear commit messages
- Push directly to main after testing
- Notify team of emergency deployment