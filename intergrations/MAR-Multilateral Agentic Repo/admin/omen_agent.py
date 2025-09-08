"""
Omen Agent: Operational Metadata Extraction Node
Enhanced for MAR Agent Generation System
"""

import os
import ast
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from llm.llm_service import query_llm

load_dotenv()


@dataclass
class CodeDiscovery:
    """Enhanced metadata for discovered code"""
    id: str
    name: str
    file: str
    type: str  # function, class, method
    source_code: str
    doc: str
    status: str
    
    # Enhanced fields for agent generation
    functionality_type: str  # processor, analyzer, extractor, validator, etc.
    input_signature: List[str]
    output_signature: List[str]
    dependencies: List[str]
    complexity_score: float
    reusability_score: float
    llm_compatible: bool
    agent_potential: str  # high, medium, low
    related_patterns: List[str]


class OmenAgent:
    def __init__(self, root_dir=".", output_dir="MAR-Multilateral Agentic Repo/agents/assets"):
        self.root = Path(root_dir)
        self.output = Path(output_dir)
        self.registry_path = Path("MAR-Multilateral Agentic Repo/configs/agent_registry.json")
        self.discoveries_path = Path("MAR-Multilateral Agentic Repo/admin/code_discoveries.json")
        self.collected = []
        self.patterns_of_interest = [
            r'def.*process.*\(',
            r'def.*extract.*\(',
            r'def.*analyze.*\(',
            r'def.*search.*\(',
            r'def.*validate.*\(',
            r'def.*transform.*\(',
            r'class.*Agent.*\(',
            r'class.*Engine.*\(',
            r'class.*Processor.*\(',
            r'class.*Extractor.*\(',
        ]

    def scan(self):
        """Enhanced scanning with pattern recognition"""
        print("🔍 Starting enhanced code discovery scan...")
        py_files = list(self.root.rglob("*.py"))
        
        for file in py_files:
            if "MAR" in str(file) or "__pycache__" in str(file):
                continue
                
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Check if file contains patterns of interest
                if self._has_interesting_patterns(content):
                    tree = ast.parse(content)
                    self.analyze_enhanced(file, tree, content)
                    
            except Exception as e:
                print(f"❌ Failed to analyze {file}: {e}")

    def _has_interesting_patterns(self, content: str) -> bool:
        """Check if file contains patterns useful for agent generation"""
        for pattern in self.patterns_of_interest:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def analyze_enhanced(self, path: Path, tree: ast.AST, content: str):
        """Enhanced analysis with agent generation focus"""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Extract source code for this node
                try:
                    source_code = ast.get_source_segment(content, node)
                    if not source_code:
                        continue
                        
                    # Enhanced analysis with LLM
                    discovery = self._analyze_code_with_llm(path, node, source_code)
                    if discovery:
                        self.collected.append(discovery)
                        
                except Exception as e:
                    print(f"⚠️  Failed to process {node.name} in {path}: {e}")
                    
    def _analyze_code_with_llm(self, path: Path, node: ast.AST, source_code: str) -> Optional[CodeDiscovery]:
        """Use LLM to analyze code for agent generation potential"""
        
        analysis_prompt = f"""
        Analyze this code for AI agent generation potential:
        
        File: {path}
        Name: {node.name}
        Type: {'function' if isinstance(node, ast.FunctionDef) else 'class'}
        
        Code:
        {source_code}
        
        Determine:
        1. functionality_type: What type of processing does this do? (processor/analyzer/extractor/validator/transformer/searcher/other)
        2. input_signature: What types of inputs does it expect? (list of type descriptions)
        3. output_signature: What types of outputs does it produce? (list of type descriptions)
        4. dependencies: What external libraries/modules does it use? (list)
        5. complexity_score: How complex is this code? (0.0-1.0, where 1.0 is very complex)
        6. reusability_score: How reusable is this for other contexts? (0.0-1.0, where 1.0 is highly reusable)
        7. llm_compatible: Could this benefit from LLM integration? (true/false)
        8. agent_potential: Overall potential as an agent component (high/medium/low)
        9. doc: Brief documentation of what this code does
        10. related_patterns: What other patterns might this work well with? (list of strings)
        
        Return JSON format only.
        """
        
        try:
            response = query_llm(analysis_prompt, model="gpt-4o")
            analysis_data = json.loads(response.get("output", "{}"))
            
            # Only keep high-potential discoveries
            if analysis_data.get("agent_potential", "low") in ["high", "medium"]:
                return CodeDiscovery(
                    id=self.make_id(path, node.name),
                    name=node.name,
                    file=str(path),
                    type="function" if isinstance(node, ast.FunctionDef) else "class",
                    source_code=source_code,
                    doc=analysis_data.get("doc", ""),
                    status="discovered",
                    functionality_type=analysis_data.get("functionality_type", "other"),
                    input_signature=analysis_data.get("input_signature", []),
                    output_signature=analysis_data.get("output_signature", []),
                    dependencies=analysis_data.get("dependencies", []),
                    complexity_score=float(analysis_data.get("complexity_score", 0.5)),
                    reusability_score=float(analysis_data.get("reusability_score", 0.5)),
                    llm_compatible=bool(analysis_data.get("llm_compatible", False)),
                    agent_potential=analysis_data.get("agent_potential", "low"),
                    related_patterns=analysis_data.get("related_patterns", [])
                )
        except Exception as e:
            print(f"❌ LLM analysis failed for {node.name}: {e}")
            
        return None

    def make_id(self, path, name):
        short = f"{path.stem}_{name}"
        return hashlib.md5(short.encode()).hexdigest()

    def copy_file(self, path):
        """Copy promising source files to MAR assets"""
        dest = self.output / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "r") as src, open(dest, "w") as dst:
            dst.write(src.read())

    def save_discoveries(self):
        """Save detailed discoveries for agent generation"""
        self.discoveries_path.parent.mkdir(parents=True, exist_ok=True)
        
        discoveries_data = [asdict(discovery) for discovery in self.collected]
        with open(self.discoveries_path, "w") as f:
            json.dump(discoveries_data, f, indent=2)
            
        print(f"💾 Saved {len(discoveries_data)} code discoveries to {self.discoveries_path}")

    def update_registry(self):
        """Update basic agent registry (legacy compatibility)"""
        if not self.registry_path.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, "w") as f:
                json.dump([], f)

        with open(self.registry_path, "r") as f:
            current = json.load(f)

        # Convert discoveries to legacy format
        for discovery in self.collected:
            legacy_entry = {
                "id": discovery.id,
                "name": discovery.name,
                "file": discovery.file,
                "type": discovery.type,
                "doc": discovery.doc,
                "status": discovery.status,
                "agent_potential": discovery.agent_potential,
                "functionality_type": discovery.functionality_type
            }
            
            if not any(e["id"] == legacy_entry["id"] for e in current):
                current.append(legacy_entry)

        with open(self.registry_path, "w") as f:
            json.dump(current, f, indent=2)

    def get_high_potential_discoveries(self) -> List[CodeDiscovery]:
        """Get discoveries with high agent generation potential"""
        return [d for d in self.collected if d.agent_potential == "high"]
    
    def get_discoveries_by_type(self, functionality_type: str) -> List[CodeDiscovery]:
        """Get discoveries by functionality type"""
        return [d for d in self.collected if d.functionality_type == functionality_type]
    
    def generate_agent_suggestions(self) -> List[Dict[str, Any]]:
        """Generate suggestions for agents that could be created"""
        suggestions = []
        
        # Group by functionality type
        type_groups = {}
        for discovery in self.collected:
            if discovery.agent_potential in ["high", "medium"]:
                func_type = discovery.functionality_type
                if func_type not in type_groups:
                    type_groups[func_type] = []
                type_groups[func_type].append(discovery)
        
        # Create suggestions for each group
        for func_type, discoveries in type_groups.items():
            if len(discoveries) >= 1:  # At least one discovery needed
                suggestions.append({
                    "suggested_agent_name": f"{func_type}_agent",
                    "agent_category": self._infer_category(func_type),
                    "source_discoveries": len(discoveries),
                    "avg_reusability": sum(d.reusability_score for d in discoveries) / len(discoveries),
                    "primary_sources": [d.file for d in discoveries[:3]],  # Top 3 sources
                    "functionality_type": func_type
                })
                
        return sorted(suggestions, key=lambda x: x["avg_reusability"], reverse=True)
    
    def _infer_category(self, functionality_type: str) -> str:
        """Infer agent category from functionality type"""
        category_mapping = {
            "processor": "data",
            "analyzer": "analysis", 
            "extractor": "extraction",
            "validator": "validation",
            "transformer": "transformation",
            "searcher": "search",
            "other": "utility"
        }
        return category_mapping.get(functionality_type, "utility")

    def run(self):
        """Enhanced run with agent generation workflow"""
        print("🚀 Starting Omen Agent enhanced discovery...")
        
        # Scan and analyze
        self.scan()
        
        # Save detailed discoveries
        self.save_discoveries()
        
        # Update legacy registry
        self.update_registry()
        
        # Generate agent suggestions
        suggestions = self.generate_agent_suggestions()
        
        print(f"\n📊 Discovery Summary:")
        print(f"   • Total discoveries: {len(self.collected)}")
        print(f"   • High potential: {len(self.get_high_potential_discoveries())}")
        print(f"   • Agent suggestions: {len(suggestions)}")
        
        if suggestions:
            print(f"\n💡 Top Agent Suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion['suggested_agent_name']} "
                      f"(reusability: {suggestion['avg_reusability']:.2f})")
                      
        return {
            "discoveries": self.collected,
            "suggestions": suggestions,
            "high_potential_count": len(self.get_high_potential_discoveries())
        }
