#!/usr/bin/env python3
"""
The_Bridge Cross-Platform Communication Bridge
Handles WSL2 ↔ Windows communication and path translation
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Union, Optional

class PlatformBridge:
    """Manages cross-platform communication and path translation"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.is_wsl = 'microsoft' in platform.uname().release.lower()
        
        # Load environment configuration
        self.config = self._load_config()
        self.current_env = self._detect_environment()
        
    def _load_config(self) -> Dict:
        """Load cross-platform configuration"""
        if self.is_windows:
            config_path = Path("C:/Users/Password/Continuum_Overworld/.bridge/environments.json")
        else:
            config_path = Path("/mnt/c/users/password/Continuum_Overworld/.bridge/environments.json")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "claude_code": {
                    "type": "WSL2",
                    "python": "/usr/bin/python3",
                    "shell": "/bin/bash",
                    "path_prefix": "/mnt/c/users/password"
                },
                "cursor": {
                    "type": "Windows", 
                    "python": "python",
                    "shell": "cmd.exe",
                    "path_prefix": "C:\\Users\\Password"
                }
            }
    
    def _detect_environment(self) -> str:
        """Detect current environment"""
        if self.is_windows:
            return "cursor"
        else:
            return "claude_code"
    
    def translate_path(self, path: str, target_env: str) -> str:
        """Translate path between Windows and WSL2 formats"""
        current_config = self.config[self.current_env]
        target_config = self.config[target_env]
        
        # Normalize input path
        path = str(Path(path))
        
        if self.current_env == "claude_code" and target_env == "cursor":
            # WSL2 to Windows
            if path.startswith("/mnt/c/"):
                # Remove WSL2 prefix and convert to Windows
                relative = path[7:]  # Remove "/mnt/c/"
                windows_path = "C:\\" + relative.replace("/", "\\")
                return windows_path
        
        elif self.current_env == "cursor" and target_env == "claude_code":
            # Windows to WSL2
            if path.startswith("C:\\"):
                # Convert to WSL2 format
                relative = path[3:]  # Remove "C:\\"
                wsl_path = "/mnt/c/" + relative.replace("\\", "/").lower()
                return wsl_path
        
        # Return original path if no translation needed
        return path
    
    def execute_command(self, command: str, target_env: str = None) -> Dict:
        """Execute command in target environment"""
        if target_env is None:
            target_env = self.current_env
        
        target_config = self.config[target_env]
        
        try:
            if target_env == "claude_code" and self.current_env == "cursor":
                # Execute in WSL2 from Windows
                wsl_command = f'wsl bash -c "cd /mnt/c/users/password/Continuum_Overworld && {command}"'
                result = subprocess.run(wsl_command, shell=True, capture_output=True, text=True)
            
            elif target_env == "cursor" and self.current_env == "claude_code":
                # Execute in Windows from WSL2 (limited capability)
                # This would require powershell.exe or cmd.exe
                cmd_command = f'cmd.exe /c "cd C:\\Users\\Password\\Continuum_Overworld && {command}"'
                result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            
            else:
                # Execute in current environment
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "environment": target_env
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "environment": target_env
            }
    
    def create_agent_message(self, from_agent: str, to_agent: str, action: str, data: Dict) -> Dict:
        """Create standard agent communication message"""
        return {
            "header": {
                "message_id": self._generate_id(),
                "timestamp": self._get_timestamp(),
                "from": from_agent,
                "to": to_agent,
                "environment": self.current_env,
                "bridge_version": "v1.0.0"
            },
            "body": {
                "action": action,
                "data": data,
                "context": {
                    "working_directory": self._get_working_directory(),
                    "platform": platform.platform()
                }
            },
            "routing": {
                "requires_translation": from_agent != to_agent,
                "target_environment": self._get_agent_environment(to_agent)
            }
        }
    
    def _generate_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_working_directory(self) -> str:
        """Get current working directory"""
        cwd = os.getcwd()
        if self.is_windows:
            return cwd
        else:
            return cwd
    
    def _get_agent_environment(self, agent_id: str) -> str:
        """Determine agent's environment"""
        if "WSL2" in agent_id or "claude" in agent_id.lower():
            return "claude_code"
        elif "WIN" in agent_id or "cursor" in agent_id.lower():
            return "cursor"
        else:
            return self.current_env

def main():
    """Bridge CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python cross-platform-bridge.py <command> [target_env]")
        print("Commands:")
        print("  translate <path> <target_env> - Translate path")
        print("  execute <command> [target_env] - Execute command")
        print("  message <from> <to> <action> - Create agent message")
        sys.exit(1)
    
    bridge = PlatformBridge()
    command = sys.argv[1]
    
    if command == "translate":
        if len(sys.argv) < 4:
            print("Usage: translate <path> <target_env>")
            sys.exit(1)
        
        path = sys.argv[2]
        target_env = sys.argv[3]
        result = bridge.translate_path(path, target_env)
        print(result)
    
    elif command == "execute":
        if len(sys.argv) < 3:
            print("Usage: execute <command> [target_env]")
            sys.exit(1)
        
        cmd = sys.argv[2]
        target_env = sys.argv[3] if len(sys.argv) > 3 else None
        result = bridge.execute_command(cmd, target_env)
        
        if result["success"]:
            print(result["stdout"])
        else:
            print(f"Error: {result.get('stderr', result.get('error'))}", file=sys.stderr)
            sys.exit(1)
    
    elif command == "message":
        if len(sys.argv) < 5:
            print("Usage: message <from> <to> <action>")
            sys.exit(1)
        
        from_agent = sys.argv[2]
        to_agent = sys.argv[3]
        action = sys.argv[4]
        
        message = bridge.create_agent_message(from_agent, to_agent, action, {})
        print(json.dumps(message, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()