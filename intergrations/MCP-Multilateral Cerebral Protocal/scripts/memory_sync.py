#!/usr/bin/env python3
"""
MCP Memory Sync Script
Handles loading, updating, and syncing memory across Claude Code sessions
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class MCPMemorySync:
    def __init__(self, projects_root: str = "/mnt/c/users/password/documents/projects"):
        self.projects_root = Path(projects_root)
        self.mcp_root = self.projects_root / "MCP"
        self.global_memory_path = self.mcp_root / "agents" / "claude_code.json"
        self.logs_dir = self.mcp_root / "logs"
        
    def load_global_memory(self) -> Dict[str, Any]:
        """Load global agent memory file"""
        try:
            with open(self.global_memory_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_global_memory()
    
    def load_project_memory(self, project_name: str) -> Dict[str, Any]:
        """Load project-specific memory file"""
        project_memory_path = self.projects_root / project_name / "memory.json"
        try:
            with open(project_memory_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_project_memory(project_name)
    
    def update_global_memory(self, updates: Dict[str, Any]) -> None:
        """Update global memory file with new data"""
        memory = self.load_global_memory()
        memory.update(updates)
        memory["updated"] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.global_memory_path, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def update_project_memory(self, project_name: str, updates: Dict[str, Any]) -> None:
        """Update project memory file with new data"""
        memory = self.load_project_memory(project_name)
        memory.update(updates)
        memory["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        project_memory_path = self.projects_root / project_name / "memory.json"
        with open(project_memory_path, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def log_session_summary(self, summary: Dict[str, Any]) -> None:
        """Log session summary to logs directory"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"session_{timestamp}.json"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_summary": summary
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    def get_active_projects(self) -> List[str]:
        """Get list of active projects from global memory"""
        memory = self.load_global_memory()
        return memory.get("active_projects", [])
    
    def sync_all_memories(self) -> Dict[str, Any]:
        """Sync and return all memory contexts"""
        global_memory = self.load_global_memory()
        project_memories = {}
        
        for project in self.get_active_projects():
            project_memories[project] = self.load_project_memory(project)
        
        return {
            "global": global_memory,
            "projects": project_memories,
            "sync_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def compress_memory_if_needed(self, memory: Dict[str, Any], token_limit: int = 10000) -> Dict[str, Any]:
        """Compress memory if it exceeds token limit (rough estimate)"""
        memory_str = json.dumps(memory)
        if len(memory_str) > token_limit:
            # Simple compression: keep only recent items
            if "session_log" in memory:
                memory["session_log"] = memory["session_log"][-10:]  # Keep last 10 entries
            if "notes" in memory:
                memory["notes"] = memory["notes"][-20:]  # Keep last 20 notes
        return memory
    
    def _create_default_global_memory(self) -> Dict[str, Any]:
        """Create default global memory structure"""
        return {
            "agent": "Claude Code",
            "updated": datetime.utcnow().isoformat() + "Z",
            "instructions": [
                "Load memory from MCP/agents/claude_code.json and [project]/memory.json at session start.",
                "Update memory to both files before session end.",
                "Summarize memory if token length is exceeded.",
                "Log session summary to MCP/logs/."
            ],
            "preferences": {
                "auto_code_review": True,
                "root_task_handling": "on_confirm",
                "security_first": True
            },
            "active_projects": [],
            "session_log": []
        }
    
    def _create_default_project_memory(self, project_name: str) -> Dict[str, Any]:
        """Create default project memory structure"""
        return {
            "project": project_name,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "context": [],
            "notes": []
        }

def main():
    """Main function for command line usage"""
    import sys
    
    sync = MCPMemorySync()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            memories = sync.sync_all_memories()
            print(json.dumps(memories, indent=2))
        
        elif command == "log" and len(sys.argv) > 2:
            summary = {"message": " ".join(sys.argv[2:])}
            sync.log_session_summary(summary)
            print("Session logged successfully")
        
        else:
            print("Usage: python memory_sync.py [sync|log <message>]")
    
    else:
        # Default: sync all memories
        memories = sync.sync_all_memories()
        print("Memory sync completed")
        print(f"Active projects: {memories['global']['active_projects']}")

if __name__ == "__main__":
    main()