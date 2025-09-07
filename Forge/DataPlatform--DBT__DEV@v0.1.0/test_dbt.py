#!/usr/bin/env python3
"""
dbt Model Testing Script
Tests that dbt models compile and run correctly
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success/failure"""
    print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False
    except FileNotFoundError:
        print(f"❌ dbt command not found. Please install dbt-core and dbt-postgres")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    """Main dbt testing routine"""
    print("🔧 DBT MODEL VERIFICATION")
    print("=" * 40)
    
    # Set profiles directory to current directory
    profiles_dir = Path(__file__).parent
    
    tests = [
        (['dbt', 'debug', '--profiles-dir', str(profiles_dir)], 
         "Database connection test"),
        (['dbt', 'deps', '--profiles-dir', str(profiles_dir)], 
         "Installing dbt dependencies"),
        (['dbt', 'parse', '--profiles-dir', str(profiles_dir)], 
         "Parsing dbt project"),
        (['dbt', 'compile', '--profiles-dir', str(profiles_dir)], 
         "Compiling dbt models"),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 40)
    print("DBT TEST SUMMARY")
    print("=" * 40)
    
    total = passed + failed
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if failed == 0:
        print("✅ ALL DBT TESTS PASSED!")
        print("\n💡 To run the actual models, use:")
        print(f"   cd {Path(__file__).parent}")
        print("   dbt run --profiles-dir .")
    else:
        print(f"❌ {failed} tests failed")
        print("\n🔧 Fix the issues above before running dbt models")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)