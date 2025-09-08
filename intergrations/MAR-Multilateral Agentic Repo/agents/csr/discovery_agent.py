"""
Discovery Agent Module - CSR
"""

from shared.memory.memory_manager import MemoryManager
from shared.prompts.loader import load_prompt
from llm.llm_service import query_llm

class DiscoveryAgent:
    def __init__(self, company, year):
        self.company = company
        self.year = year
        self.prompt_template = load_prompt("esg_discovery_prompt.txt")
        self.memory = MemoryManager()

    def generate_prompt(self):
        return self.prompt_template.format(company=self.company, year=self.year)

    def run(self):
        prompt = self.generate_prompt()
        response = query_llm(prompt, model="gpt-4o")
        self.memory.store_interaction("discovery", self.company, self.year, prompt, response)
        return response
