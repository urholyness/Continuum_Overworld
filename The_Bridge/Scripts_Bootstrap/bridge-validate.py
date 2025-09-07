#!/usr/bin/env python3
"""
Continuum_Overworld Structure & Naming Validator
Works on both WSL2 and Windows environments
"""

import json
import re
import sys
import os
from pathlib import Path
import platform

# Detect environment
IS_WINDOWS = platform.system() == 'Windows'
IS_WSL = 'microsoft' in platform.uname().release.lower()

# Set root path based on environment
if IS_WINDOWS:
    ROOT = Path("C:/Users/Password/Continuum_Overworld")
else:
    ROOT = Path("/mnt/c/users/password/Continuum_Overworld")

# Required paths that must exist
REQUIRED_PATHS = [
    "The_Bridge/Console--Core__PROD@",
    "The_Bridge/Playbooks",
    "The_Bridge/RFCs",
    "Pantheon/Registry.json",
    "Pantheon/Orion",
    "Pantheon/Omen",
    "Aegis/Audit",
    "Aegis/Playbooks",
    "Atlas",
    "Forge",
    "Oracle",
    "Meridian",
    "Agora",
    "Ledger",
    "Archive/BACK_BURNER",
    ".bridge/grammar.json",
    ".bridge/environments.json"
]

def load_grammar():
    """Load grammar configuration"""
    grammar_file = ROOT / ".bridge" / "grammar.json"
    if not grammar_file.exists():
        print(f"❌ Grammar configuration not found: {grammar_file}")
        return None
    
    with open(grammar_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_structure():
    """Validate directory structure exists"""
    errors = []
    
    print("🔍 Validating directory structure...")
    
    for path_str in REQUIRED_PATHS:
        full_path = ROOT / path_str
        if not full_path.exists():
            errors.append(f"MISSING: {path_str}")
        else:
            print(f"  ✅ {path_str}")
    
    return errors

def validate_naming(grammar):
    """Validate naming conventions"""
    errors = []
    
    print("\n🔍 Validating naming conventions...")
    
    # Compile patterns
    div_pattern = re.compile(grammar["label_pattern"])  # Pascal_Snake
    ver_pattern = re.compile(grammar["versioned_dir_pattern"])  # versioned dirs
    playbook_pattern = re.compile(grammar["playbook_pattern"])  # playbook files
    rfc_pattern = re.compile(grammar.get("rfc_pattern", r"^RFC--.+__.+@v\d+\.\d+\.\d+\.md$"))
    
    # Check division names
    if ROOT.exists():
        for item in ROOT.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if not div_pattern.match(item.name):
                    errors.append(f"DIVISION_CASE: '{item.name}' not Pascal_Snake")
                else:
                    print(f"  ✅ Division: {item.name}")
    
    # Check versioned directories
    for root, dirs, files in os.walk(ROOT):
        rel_path = Path(root).relative_to(ROOT)
        
        # Check versioned directory names
        for dir_name in dirs:
            if "@v" in dir_name:
                test_name = dir_name if dir_name.endswith('/') else dir_name + '/'
                if not ver_pattern.match(test_name):
                    errors.append(f"VERSIONED_DIR: '{rel_path / dir_name}' invalid pattern")
        
        # Check playbook files
        for file_name in files:
            if file_name.startswith("Playbook--"):
                if not playbook_pattern.match(file_name):
                    errors.append(f"PLAYBOOK_NAME: '{rel_path / file_name}' invalid pattern")
            elif file_name.startswith("RFC--"):
                if not rfc_pattern.match(file_name):
                    errors.append(f"RFC_NAME: '{rel_path / file_name}' invalid pattern")
    
    return errors

def validate_cross_platform():
    """Validate cross-platform compatibility"""
    errors = []
    warnings = []
    
    print("\n🔍 Validating cross-platform compatibility...")
    
    # Check for both script types
    scripts_dir = ROOT / "scripts"
    if scripts_dir.exists():
        sh_scripts = list(scripts_dir.glob("*.sh"))
        bat_scripts = list(scripts_dir.glob("*.bat"))
        
        # Find scripts without cross-platform pairs
        sh_names = {s.stem for s in sh_scripts}
        bat_names = {b.stem for b in bat_scripts}
        
        for sh_name in sh_names:
            if sh_name not in bat_names and sh_name != "mk-structure":  # mk-structure is special
                warnings.append(f"CROSS_PLATFORM: {sh_name}.sh lacks .bat equivalent")
        
        for bat_name in bat_names:
            if bat_name not in sh_names and bat_name not in ["validate", "quick-check", "wsl-bridge", "run-python"]:
                warnings.append(f"CROSS_PLATFORM: {bat_name}.bat lacks .sh equivalent")
        
        print(f"  ✅ Found {len(sh_scripts)} .sh scripts")
        print(f"  ✅ Found {len(bat_scripts)} .bat scripts")
    
    # Check line endings configuration
    gitattributes = ROOT / ".gitattributes"
    if not gitattributes.exists():
        errors.append("MISSING: .gitattributes for line ending management")
    else:
        print("  ✅ .gitattributes present")
    
    return errors, warnings

def validate_agents():
    """Validate agent registry"""
    errors = []
    
    print("\n🔍 Validating agent registry...")
    
    registry_file = ROOT / "Pantheon" / "Registry.json"
    if not registry_file.exists():
        errors.append("MISSING: Pantheon/Registry.json")
        return errors
    
    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Check for required agents
        agent_ids = {agent['id'] for agent in registry.get('agents', [])}
        
        if 'claude-code-wsl2' not in agent_ids:
            errors.append("AGENT_MISSING: Claude Code (WSL2) not in registry")
        else:
            print("  ✅ Claude Code registered")
        
        if 'cursor-validator-win' not in agent_ids:
            errors.append("AGENT_MISSING: Cursor Validator (Windows) not in registry")
        else:
            print("  ✅ Cursor Validator registered")
        
        # Validate schema version
        if 'schema_version' not in registry:
            errors.append("REGISTRY: Missing schema_version")
        else:
            print(f"  ✅ Registry schema v{registry['schema_version']}")
    
    except json.JSONDecodeError as e:
        errors.append(f"REGISTRY: Invalid JSON - {e}")
    
    return errors

def generate_report(errors, warnings):
    """Generate validation report"""
    report = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "environment": "Windows" if IS_WINDOWS else "WSL2",
        "platform": platform.platform(),
        "validation_results": {
            "structure": "PASS" if not any("MISSING" in e for e in errors) else "FAIL",
            "naming": "PASS" if not any("CASE" in e or "PATTERN" in e for e in errors) else "FAIL",
            "agents": "PASS" if not any("AGENT" in e or "REGISTRY" in e for e in errors) else "FAIL",
            "cross_platform": "PASS" if not any("CROSS_PLATFORM" in e for e in errors) else "WARN"
        },
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "status": "PASS" if len(errors) == 0 else "FAIL"
        }
    }
    
    # Save report
    report_file = ROOT / ".bridge" / "validation-report.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main validation routine"""
    print("=" * 60)
    print("🌉 THE_BRIDGE Structure & Naming Validator")
    print("=" * 60)
    print(f"Environment: {'Windows' if IS_WINDOWS else 'WSL2' if IS_WSL else 'Linux'}")
    print(f"Root Path: {ROOT}")
    print("=" * 60)
    
    all_errors = []
    all_warnings = []
    
    # Check if root exists
    if not ROOT.exists():
        print(f"❌ Root directory not found: {ROOT}")
        print("   Run mk-structure.sh (WSL2) or mk-structure.bat (Windows) first")
        sys.exit(1)
    
    # Load grammar
    grammar = load_grammar()
    if not grammar:
        all_errors.append("GRAMMAR: Configuration file missing or invalid")
    
    # Run validations
    struct_errors = validate_structure()
    all_errors.extend(struct_errors)
    
    if grammar:
        naming_errors = validate_naming(grammar)
        all_errors.extend(naming_errors)
    
    platform_errors, platform_warnings = validate_cross_platform()
    all_errors.extend(platform_errors)
    all_warnings.extend(platform_warnings)
    
    agent_errors = validate_agents()
    all_errors.extend(agent_errors)
    
    # Generate report
    report = generate_report(all_errors, all_warnings)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    
    if all_errors:
        print("\n❌ ERRORS FOUND:")
        for error in all_errors:
            print(f"   • {error}")
    
    if all_warnings:
        print("\n⚠️  WARNINGS:")
        for warning in all_warnings:
            print(f"   • {warning}")
    
    if not all_errors:
        print("\n✅ VALIDATION PASSED")
        print("   Structure and naming conform to THE_BRIDGE standard")
    else:
        print(f"\n❌ VALIDATION FAILED")
        print(f"   {len(all_errors)} error(s) found")
    
    print(f"\n📄 Report saved to: .bridge/validation-report.json")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if not all_errors else 1)

if __name__ == "__main__":
    main()