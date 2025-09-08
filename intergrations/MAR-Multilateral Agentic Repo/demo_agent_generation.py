#!/usr/bin/env python3
"""
MAR Agent Generation System Demo
Demonstrates the automated agent generation pipeline
"""

import sys
import os
from pathlib import Path

# Add the admin directory to path for imports
sys.path.append(str(Path(__file__).parent / "admin"))

from agent_generation_orchestrator import AgentGenerationOrchestrator


def demo_full_pipeline():
    """Demonstrate the full agent generation pipeline"""
    print("🌟 MAR Agent Generation System Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AgentGenerationOrchestrator(
        projects_root=".",  # Scan current directory and subdirectories
        mar_root="MAR-Multilateral Agentic Repo"
    )
    
    print("\n🎯 Demo Mode: Discovery + Analysis (no auto-generation)")
    print("   This will scan your codebase and suggest agents that could be created")
    
    # Run pipeline without auto-generation
    results = orchestrator.run_full_pipeline(
        auto_generate=False,  # Set to True to actually generate agents
        max_agents=3
    )
    
    # Show what we found
    if results["suggestions"]:
        print(f"\n🚀 Ready to Generate Agents!")
        print(f"   Found {len(results['suggestions'])} agent suggestions")
        print(f"   To generate agents automatically, run with auto_generate=True")
        
        # Show top suggestions
        print(f"\n💡 Top Agent Suggestions:")
        for i, suggestion in enumerate(results["suggestions"][:3], 1):
            print(f"   {i}. {suggestion['suggested_agent_name']}")
            print(f"      Category: {suggestion['agent_category']}")
            print(f"      Reusability: {suggestion['avg_reusability']:.2f}")
            print(f"      Sources: {suggestion['source_discoveries']} discoveries")
            print()
    
    return results


def demo_specific_agent_generation():
    """Demonstrate generating a specific agent"""
    print("\n🎯 Demo: Generating a Specific Agent")
    print("=" * 40)
    
    orchestrator = AgentGenerationOrchestrator()
    
    # List available patterns first
    print("📋 Scanning for available patterns...")
    patterns = orchestrator.list_available_patterns()
    
    if patterns:
        print(f"Found patterns in {len(patterns)} functionality types:")
        for func_type, pattern_list in patterns.items():
            print(f"   • {func_type}: {len(pattern_list)} patterns")
            
        # Try to generate an agent from the most common functionality type
        most_common_type = max(patterns.keys(), key=lambda k: len(patterns[k]))
        
        print(f"\n🔧 Generating agent from '{most_common_type}' patterns...")
        blueprint = orchestrator.generate_specific_agent(
            agent_name=f"demo_{most_common_type}",
            functionality_types=[most_common_type]
        )
        
        if blueprint:
            print(f"✅ Successfully generated demo agent!")
            print(f"   Name: {blueprint.agent_name}")
            print(f"   Category: {blueprint.agent_category}")
            print(f"   Compatible LLMs: {blueprint.compatible_llms}")
    else:
        print("❌ No patterns found. Make sure you have Python files with interesting functions/classes.")


def interactive_demo():
    """Interactive demo allowing user choices"""
    print("\n🎮 Interactive MAR Agent Generation Demo")
    print("=" * 45)
    
    while True:
        print(f"\nChoose an option:")
        print(f"1. Run full discovery pipeline")
        print(f"2. List available patterns")
        print(f"3. Generate specific agent")
        print(f"4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            demo_full_pipeline()
            
        elif choice == "2":
            orchestrator = AgentGenerationOrchestrator()
            patterns = orchestrator.list_available_patterns()
            
            if patterns:
                print(f"\n📋 Available Patterns:")
                for func_type, pattern_list in patterns.items():
                    print(f"\n{func_type.upper()} ({len(pattern_list)} patterns):")
                    for pattern in pattern_list[:3]:
                        print(f"   • {pattern['name']} - {Path(pattern['file']).name}")
            else:
                print("❌ No patterns found.")
                
        elif choice == "3":
            agent_name = input("Enter agent name: ").strip()
            if agent_name:
                demo_specific_agent_generation()
            else:
                print("❌ Agent name required.")
                
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        # Run basic demo
        results = demo_full_pipeline()
        
        # Offer to continue with specific generation
        if results.get("suggestions"):
            response = input(f"\n🤔 Generate a demo agent? (y/n): ").strip().lower()
            if response == 'y':
                demo_specific_agent_generation()


