"""
Memory Manager - MAR Shared Component
Handles memory storage and retrieval for agents
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class MemoryManager:
    """Manages memory storage for MAR agents"""
    
    def __init__(self, memory_dir: str = "MAR-Multilateral Agentic Repo/shared/memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.memory_dir / "interactions.json"
        self.project_memory_file = self.memory_dir / "project_memory.json"
        
    def store_interaction(self, agent_name: str, input_data: Any, output_data: Any):
        """Store an agent interaction"""
        interaction = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "output": output_data
        }
        
        # Load existing interactions
        interactions = self._load_interactions()
        interactions.append(interaction)
        
        # Keep only last 1000 interactions
        if len(interactions) > 1000:
            interactions = interactions[-1000:]
            
        # Save
        with open(self.interactions_file, 'w') as f:
            json.dump(interactions, f, indent=2)
    
    def _load_interactions(self) -> List[Dict]:
        """Load existing interactions"""
        if self.interactions_file.exists():
            try:
                with open(self.interactions_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def get_recent_interactions(self, agent_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent interactions, optionally filtered by agent"""
        interactions = self._load_interactions()
        
        if agent_name:
            interactions = [i for i in interactions if i.get('agent') == agent_name]
            
        return interactions[-limit:]
    
    def store_project_context(self, key: str, value: Any):
        """Store project-level context"""
        project_memory = self._load_project_memory()
        project_memory[key] = value
        
        with open(self.project_memory_file, 'w') as f:
            json.dump(project_memory, f, indent=2)
    
    def get_project_context(self, key: str, default: Any = None) -> Any:
        """Get project-level context"""
        project_memory = self._load_project_memory()
        return project_memory.get(key, default)
    
    def _load_project_memory(self) -> Dict:
        """Load project memory"""
        if self.project_memory_file.exists():
            try:
                with open(self.project_memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}


