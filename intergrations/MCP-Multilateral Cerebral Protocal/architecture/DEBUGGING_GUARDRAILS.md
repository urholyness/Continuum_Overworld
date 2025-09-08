# Universal Debugging Guardrails for Claude Code

**CRITICAL**: This document was created after Grok's analysis identified a destructive cycle of partial fixes creating cascading problems. **READ THIS EVERY TIME** you encounter recurring issues.

## 🚨 The Anti-Pattern to Avoid

**NEVER DO THIS:**
- Generate new code/scripts before fully understanding the problem
- Make multiple changes across files simultaneously  
- Focus on symptoms instead of root causes
- Create "fixes" that introduce new problems
- Skip verification steps to "move faster"

## 🛡️ STOP-FIX-VERIFY Methodology

### STOP Phase
1. **Identify the EXACT error** from logs/traces
2. **Map the dependency chain** (what depends on what)
3. **Understand the root cause** (not just the symptom)
4. **NO CODE GENERATION** until diagnosis is complete

### FIX Phase  
1. **Fix ONE thing at a time** (not multiple related issues)
2. **Change the MINIMUM required** to fix the root cause
3. **Document what you're changing and why**
4. **Predict what else might be affected**

### VERIFY Phase
1. **Test the specific fix in isolation** 
2. **Verify no new problems introduced**
3. **Check all predicted affected areas**
4. **Only proceed to next issue if current is fully resolved**

## 🔍 Dependency Chain Analysis Framework

Before making ANY changes, map the full chain:

```
Error → Immediate Cause → Root Cause → Dependencies → Cascade Effects
```

**Example from Nyxion:**
```
Import Error → Missing 'Response' class → Models not loading → SQLAlchemy metadata conflict → All imports fail
```

**Wrong Approach:** Fix import statement
**Right Approach:** Fix metadata conflict first, then verify imports work

## 📋 Layer-by-Layer Verification Protocol

**ALWAYS verify in this order:**

1. **Environment Layer**
   - Dependencies installed correctly
   - Virtual environment clean
   - No conflicting packages

2. **Model Layer** 
   - All classes define correctly
   - No reserved attribute conflicts
   - Database types consistent

3. **Database Layer**
   - Schema matches models
   - No transaction failures
   - Foreign key types match

4. **API Layer**
   - Routes define correctly
   - Parameter ordering valid
   - Dependencies inject properly

5. **Integration Layer**
   - Full system works together
   - No cascade failures

## ⚠️ Warning Signs You're In The Cycle

- **Multiple error types** appearing simultaneously
- **"Fixing" one thing** breaks something else
- **Creating new scripts** instead of fixing fundamentals
- **Error messages changing** but not disappearing
- **Transaction failures** persisting across runs

## 🔧 Emergency Break-Glass Procedures

If you detect the cycle:

1. **STOP all code generation immediately**
2. **Reset to last known working state**
3. **Wipe and recreate environment if needed**
4. **Fix ONE root cause completely before proceeding**
5. **Test each layer in isolation**

## 📝 Mandatory Questions Before Any Code Change

1. **What exactly is the root cause?** (Not just the error message)
2. **What will this change affect?** (List all dependencies)
3. **How will I verify it works?** (Specific test plan)
4. **What could go wrong?** (Predict cascade effects)
5. **Is there a simpler fix?** (Minimum viable change)

## 🎯 Success Criteria

- **One error type at a time** (no new errors introduced)
- **Each fix verified in isolation** before proceeding
- **Full understanding** of why the error occurred
- **Documentation** of what was changed and why
- **Stable system** after each change

## 💡 Framework Integration

- **SCIP**: Add dependency analysis step before System design
- **MAR**: Enforce single-issue resolution with verification
- **MCP**: Require diagnostic verification before code generation

---

**Remember**: The goal is to solve problems permanently, not create an endless cycle of new issues. When in doubt, STOP and diagnose deeper.

**Last Updated**: 2025-08-06 - After Nyxion recurring cycle identified by Grok