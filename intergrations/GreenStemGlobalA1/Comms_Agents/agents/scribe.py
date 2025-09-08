"""
Scribe Agent - Content drafting and creation.
"""

import os
import logging
from typing import Dict, Any, List
from pathlib import Path

from app.deps import ScribeIn, ScribeOut
from app.database import get_db_context
from tools.retriever import retrieve_context
from tools.llm import get_llm_client

logger = logging.getLogger(__name__)


class ScribeAgent:
    """Agent responsible for drafting content across different platforms."""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt for the Scribe agent."""
        prompt_path = Path("prompts/scribe.system.md")
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        else:
            # Fallback prompt
            return """You are Scribe, a boardroom-poetic strategist with skeptical edge and quick wit. 
            Forward-looking, no fluff, cite sources. Output LinkedIn + X + 3 smart comments. 
            Avoid promises; propose pilots."""
    
    async def run(self, payload: ScribeIn, db=None) -> ScribeOut:
        """Run the Scribe agent to create content."""
        try:
            logger.info(f"Scribe agent started for issue: {payload.issue_card_path}")
            
            # Retrieve context from issue card
            context = await self._retrieve_context(payload.issue_card_path)
            
            # Generate content using LLM
            content = await self._generate_content(payload, context)
            
            # Log the agent run
            if db:
                await self._log_run(payload, content, db)
            
            logger.info(f"Scribe agent completed successfully")
            return content
            
        except Exception as e:
            logger.error(f"Scribe agent failed: {e}")
            raise
    
    async def _retrieve_context(self, issue_card_path: str) -> Dict[str, Any]:
        """Retrieve context from issue card and knowledge base."""
        try:
            # Get issue card content
            context = retrieve_context(issue_card_path)
            
            # Enhance with knowledge base search
            enhanced_context = await self._enhance_with_knowledge(context)
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            # Return basic context if enhancement fails
            return retrieve_context(issue_card_path)
    
    async def _enhance_with_knowledge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with knowledge base search."""
        try:
            # This would integrate with your RAG system
            # For now, return the original context
            return context
        except Exception as e:
            logger.warning(f"Knowledge enhancement failed: {e}")
            return context
    
    async def _generate_content(self, payload: ScribeIn, context: Dict[str, Any]) -> ScribeOut:
        """Generate content using LLM."""
        try:
            # Prepare prompt
            prompt = self._prepare_prompt(payload, context)
            
            # Generate content using LLM
            if self.llm_client:
                content = await self._generate_with_llm(prompt, payload)
            else:
                # Fallback to template-based generation
                content = self._generate_with_template(payload, context)
            
            return content
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            # Return template-based content as fallback
            return self._generate_with_template(payload, context)
    
    def _prepare_prompt(self, payload: ScribeIn, context: Dict[str, Any]) -> str:
        """Prepare the prompt for LLM generation."""
        prompt = f"""
{self.system_prompt}

Issue Card: {context.get('title', 'Unknown')}
Summary: {context.get('tldr', 'No summary available')}
Sources: {', '.join(context.get('links', []))}

Audience: {payload.audience.value}
Tone: {payload.tone.value}

Generate:
1. A LinkedIn post (professional, engaging, with call-to-action)
2. An X (Twitter) thread (2-3 tweets, engaging, shareable)
3. Three thoughtful comment variations for engagement
4. Proper citations and source attribution

Focus on actionable insights and avoid making promises or guarantees.
"""
        return prompt
    
    async def _generate_with_llm(self, prompt: str, payload: ScribeIn) -> ScribeOut:
        """Generate content using LLM."""
        try:
            # This would integrate with your LLM provider
            # For now, return a placeholder
            logger.info("LLM generation requested (not implemented)")
            return self._generate_with_template(payload, {})
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_with_template(payload, {})
    
    def _generate_with_template(self, payload: ScribeIn, context: Dict[str, Any]) -> ScribeOut:
        """Generate content using templates (fallback method)."""
        title = context.get('title', 'Policy Update')
        tldr = context.get('tldr', 'Important policy changes affecting stakeholders.')
        links = context.get('links', [])
        
        # LinkedIn post
        linkedin_post = f"""[{payload.tone.value.upper()}] {title}

{tldr}

Key implications for {payload.audience.value}s:
• Strategic considerations
• Operational impact
• Next steps

What's your take on this? Share your thoughts below.

Sources: {', '.join(links) if links else 'Available upon request'}"""
        
        # X thread
        x_thread = [
            f"{title} - {tldr}",
            f"Key implications for {payload.audience.value}s: strategic considerations, operational impact, and next steps.",
            "What's your perspective? Share your thoughts and let's discuss the implications."
        ]
        
        # Comment variations
        comments_pack = [
            "Great analysis! The operational impact on small businesses is particularly concerning. We need more clarity on implementation timelines.",
            "Interesting perspective. I'd love to see how this compares to similar regulations in other regions.",
            "The strategic considerations here are spot on. This could reshape the entire industry landscape."
        ]
        
        return ScribeOut(
            linkedin_post=linkedin_post,
            x_thread=x_thread,
            comments_pack=comments_pack,
            citations=links,
            metadata={
                "generation_method": "template",
                "audience": payload.audience.value,
                "tone": payload.tone.value,
                "issue_card": payload.issue_card_path
            }
        )
    
    async def _log_run(self, payload: ScribeIn, content: ScribeOut, db) -> None:
        """Log the agent run to database."""
        try:
            from app.crud.agent_runs import create_agent_run
            
            await create_agent_run(
                db,
                "scribe",
                payload.dict(),
                content.dict()
            )
            
        except Exception as e:
            logger.warning(f"Failed to log agent run: {e}")


# Convenience function for direct usage
async def run(payload: ScribeIn, db=None) -> ScribeOut:
    """Run the Scribe agent."""
    agent = ScribeAgent()
    return await agent.run(payload, db)


if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test():
        payload = ScribeIn(
            issue_card_path="issue_cards/eudr_smallholders.md",
            audience="buyer",
            tone="boardroom"
        )
        
        result = await run(payload)
        print("LinkedIn Post:")
        print(result.linkedin_post)
        print("\nX Thread:")
        for tweet in result.x_thread:
            print(f"- {tweet}")
        print("\nComments:")
        for comment in result.comments_pack:
            print(f"- {comment}")
    
    asyncio.run(test())

