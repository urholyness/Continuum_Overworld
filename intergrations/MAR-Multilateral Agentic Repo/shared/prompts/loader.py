"""
Prompt Loader - MAR Shared Component
Loads and manages prompt templates for agents
"""

from pathlib import Path
from typing import Dict, Optional


class PromptTemplate:
    """Simple prompt template with formatting"""
    
    def __init__(self, template: str):
        self.template = template
    
    def format(self, **kwargs) -> str:
        """Format template with provided arguments"""
        return self.template.format(**kwargs)


def load_prompt(prompt_name: str, prompts_dir: str = "MAR-Multilateral Agentic Repo/shared/prompts") -> PromptTemplate:
    """Load a prompt template by name"""
    prompts_path = Path(prompts_dir)
    prompt_file = prompts_path / prompt_name
    
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return PromptTemplate(content)
    else:
        # Return default template if file doesn't exist
        default_template = f"""
You are an AI agent processing the following data:

{{data}}

Please process this data according to your agent's purpose and return structured results.
"""
        return PromptTemplate(default_template.strip())


