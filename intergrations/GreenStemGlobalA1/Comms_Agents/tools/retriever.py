"""
Retriever tool for accessing knowledge base and issue cards.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

logger = logging.getLogger(__name__)

# Global index cache
_INDEX = {}


def retrieve_context(issue_card_path: str) -> Dict[str, Any]:
    """
    Retrieve context from an issue card file.
    
    Args:
        issue_card_path: Path to the issue card file
        
    Returns:
        Dictionary containing title, TL;DR, and links
    """
    try:
        # Resolve path
        if not issue_card_path.startswith('/'):
            issue_card_path = Path.cwd() / issue_card_path
        
        path = Path(issue_card_path)
        
        if not path.exists():
            logger.warning(f"Issue card not found: {issue_card_path}")
            return {
                "title": "Unknown Issue",
                "tldr": "No content available",
                "links": [],
                "tags": [],
                "priority": "medium"
            }
        
        # Read and parse the file
        content = path.read_text(encoding="utf-8")
        parsed = _parse_issue_card(content, path)
        
        logger.info(f"Retrieved context from {issue_card_path}")
        return parsed
        
    except Exception as e:
        logger.error(f"Failed to retrieve context from {issue_card_path}: {e}")
        return {
            "title": "Error Loading Issue",
            "tldr": f"Failed to load content: {str(e)}",
            "links": [],
            "tags": [],
            "priority": "low"
        }


def _parse_issue_card(content: str, path: Path) -> Dict[str, Any]:
    """
    Parse issue card content to extract structured information.
    
    Args:
        content: Raw file content
        path: Path to the file
        
    Returns:
        Parsed issue card data
    """
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # Extract title from filename or first heading
    title = _extract_title(content, path)
    
    # Extract TL;DR (first paragraph that's not a heading)
    tldr = _extract_tldr(lines)
    
    # Extract links
    links = _extract_links(content)
    
    # Extract tags
    tags = _extract_tags(content)
    
    # Extract priority
    priority = _extract_priority(content)
    
    # Extract sources
    sources = _extract_sources(content)
    
    return {
        "title": title,
        "tldr": tldr,
        "links": links,
        "tags": tags,
        "priority": priority,
        "sources": sources,
        "file_path": str(path),
        "content_length": len(content)
    }


def _extract_title(content: str, path: Path) -> str:
    """Extract title from content or filename."""
    # Look for first heading
    heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    
    # Fallback to filename
    return path.stem.replace("_", " ").title()


def _extract_tldr(lines: List[str]) -> str:
    """Extract TL;DR from first non-heading paragraph."""
    for line in lines:
        if line and not line.startswith('#') and not line.startswith('http'):
            # Clean up the line
            cleaned = line.strip()
            if len(cleaned) > 20:  # Ensure it's substantial
                return cleaned
    
    return "No TL;DR available"


def _extract_links(content: str) -> List[str]:
    """Extract HTTP links from content."""
    url_pattern = r'https?://[^\s\)]+'
    links = re.findall(url_pattern, content)
    return [link.rstrip('.,;:!?') for link in links]


def _extract_tags(content: str) -> List[str]:
    """Extract tags from content."""
    # Look for tag patterns like #tag or [tag]
    tag_patterns = [
        r'#(\w+)',  # Hashtags
        r'\[(\w+)\]',  # Bracketed tags
        r'tags?:\s*([^\n]+)',  # Explicit tag declarations
    ]
    
    tags = []
    for pattern in tag_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        tags.extend(matches)
    
    # Clean and deduplicate tags
    cleaned_tags = []
    for tag in tags:
        cleaned = tag.strip().lower()
        if cleaned and cleaned not in cleaned_tags:
            cleaned_tags.append(cleaned)
    
    return cleaned_tags


def _extract_priority(content: str) -> str:
    """Extract priority from content."""
    priority_patterns = [
        (r'priority:\s*(high|medium|low|urgent)', r'\1'),
        (r'priority:\s*(\d+)', lambda m: 'high' if int(m.group(1)) >= 8 else 'medium' if int(m.group(1)) >= 5 else 'low'),
        (r'urgent|critical', 'high'),
        (r'important', 'medium'),
    ]
    
    for pattern, replacement in priority_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            if callable(replacement):
                return replacement(match)
            else:
                return replacement
    
    return "medium"  # Default priority


def _extract_sources(content: str) -> List[str]:
    """Extract source references from content."""
    source_patterns = [
        r'source[s]?:\s*([^\n]+)',
        r'reference[s]?:\s*([^\n]+)',
        r'cite[d]?:\s*([^\n]+)',
    ]
    
    sources = []
    for pattern in source_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        sources.extend(matches)
    
    # Clean sources
    cleaned_sources = []
    for source in sources:
        cleaned = source.strip()
        if cleaned and cleaned not in cleaned_sources:
            cleaned_sources.append(cleaned)
    
    return cleaned_sources


def index_path(path: str, tags: Optional[List[str]] = None) -> tuple[List[str], int]:
    """
    Index a file path for vector search.
    
    Args:
        path: Path to the file to index
        tags: Optional tags for categorization
        
    Returns:
        Tuple of (entities, vector_count)
    """
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            logger.warning(f"File not found for indexing: {path}")
            return [], 0
        
        # Read file content
        content = file_path.read_text(encoding="utf-8")
        
        # Extract entities (basic implementation)
        entities = _extract_entities(content)
        
        # Generate tags if not provided
        if not tags:
            tags = _extract_tags(content)
        
        # Store in index
        _INDEX[path] = {
            "tags": tags,
            "entities": entities,
            "content_length": len(content),
            "file_type": file_path.suffix,
            "last_indexed": "now"  # In production, use actual timestamp
        }
        
        # Return entities and vector count (placeholder)
        vector_count = len(entities) + len(tags)
        
        logger.info(f"Indexed {path} with {len(entities)} entities and {vector_count} vectors")
        return entities, vector_count
        
    except Exception as e:
        logger.error(f"Failed to index {path}: {e}")
        return [], 0


def _extract_entities(content: str) -> List[str]:
    """Extract entities from content (basic implementation)."""
    # This is a simple entity extraction
    # In production, you'd use NER models or LLM-based extraction
    
    # Look for capitalized phrases that might be entities
    entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    entities = re.findall(entity_pattern, content)
    
    # Filter out common words and short entities
    common_words = {'The', 'This', 'That', 'These', 'Those', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
    filtered_entities = [
        entity for entity in entities 
        if entity not in common_words and len(entity) > 2
    ]
    
    # Limit to reasonable number
    return filtered_entities[:20]


def search_knowledge(query: str, tags: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search knowledge base for relevant content.
    
    Args:
        query: Search query
        tags: Optional tags to filter by
        limit: Maximum number of results
        
    Returns:
        List of relevant documents
    """
    try:
        # Simple keyword-based search
        # In production, this would use vector similarity search
        
        results = []
        query_terms = query.lower().split()
        
        for path, index_data in _INDEX.items():
            # Calculate relevance score
            score = _calculate_relevance(query_terms, index_data)
            
            if score > 0:
                results.append({
                    "path": path,
                    "score": score,
                    "tags": index_data.get("tags", []),
                    "entities": index_data.get("entities", []),
                    "content_length": index_data.get("content_length", 0),
                    "file_type": index_data.get("file_type", ""),
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return []


def _calculate_relevance(query_terms: List[str], index_data: Dict[str, Any]) -> float:
    """Calculate relevance score for search results."""
    score = 0.0
    
    # Score based on tag matches
    tags = index_data.get("tags", [])
    for term in query_terms:
        for tag in tags:
            if term in tag.lower():
                score += 2.0
    
    # Score based on entity matches
    entities = index_data.get("entities", [])
    for term in query_terms:
        for entity in entities:
            if term in entity.lower():
                score += 1.5
    
    # Bonus for exact matches
    if any(term in str(index_data).lower() for term in query_terms):
        score += 0.5
    
    return score


def get_index_stats() -> Dict[str, Any]:
    """Get statistics about the indexed content."""
    total_files = len(_INDEX)
    total_tags = sum(len(data.get("tags", [])) for data in _INDEX.values())
    total_entities = sum(len(data.get("entities", [])) for data in _INDEX.values())
    total_content = sum(data.get("content_length", 0) for data in _INDEX.values())
    
    return {
        "total_files": total_files,
        "total_tags": total_tags,
        "total_entities": total_entities,
        "total_content_bytes": total_content,
        "file_types": list(set(data.get("file_type", "") for data in _INDEX.values())),
        "indexed_paths": list(_INDEX.keys())
    }


def clear_index():
    """Clear the in-memory index."""
    global _INDEX
    _INDEX.clear()
    logger.info("Knowledge index cleared")


if __name__ == "__main__":
    # Test the retriever
    test_path = "issue_cards/eudr_smallholders.md"
    
    print("Testing retriever...")
    context = retrieve_context(test_path)
    print(f"Retrieved context: {json.dumps(context, indent=2)}")
    
    # Test indexing
    entities, vectors = index_path(test_path)
    print(f"Indexed entities: {entities}")
    print(f"Vector count: {vectors}")
    
    # Test search
    results = search_knowledge("EUDR smallholders")
    print(f"Search results: {len(results)} documents found")
    
    # Show stats
    stats = get_index_stats()
    print(f"Index stats: {json.dumps(stats, indent=2)}")

