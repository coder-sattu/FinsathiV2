"""Cognee-inspired Knowledge Graph & Vector Policy Document RAG module.

Indexes policy clauses, coverage terms, waiting periods, room rent limits,
and timelines for agentic retrieval and grounded LLM answers.
"""

import json
from pathlib import Path
from typing import Any
from rapidfuzz import process, fuzz


class CogneePolicyRAG:
    """Policy Document Knowledge Graph & RAG Retriever."""

    def __init__(self, data_path: Path | None = None) -> None:
        path = data_path or (Path(__file__).parent.parent.parent / "data" / "policy_clauses.json")
        self.clauses: list[dict[str, Any]] = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.clauses = json.load(f)

    def retrieve_relevant_clauses(
        self, query: str, product_name: str | None = None, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Retrieve relevant policy clauses matching query and optional product filtering."""
        query_clean = query.lower().strip()
        results: list[tuple[dict[str, Any]], float] = []

        for clause in self.clauses:
            # Check product applicability
            prods = clause.get("products", [])
            if product_name and "ALL" not in prods:
                if not any(p.lower() in product_name.lower() for p in prods):
                    continue

            # Calculate match score based on keywords, title, and content
            keywords = clause.get("keywords", [])
            title = clause.get("title", "")
            content = clause.get("content", "")

            # Keyword score
            kw_matches = sum(1 for kw in keywords if kw in query_clean)
            kw_score = (kw_matches / max(len(keywords), 1)) * 50.0

            # Rapidfuzz title & content matching
            title_score = fuzz.partial_ratio(query_clean, title.lower()) * 0.3
            content_score = fuzz.partial_ratio(query_clean, content.lower()) * 0.2

            total_score = kw_score + title_score + content_score

            results.append((clause, total_score))

        # Sort by total_score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k] if r[1] > 15.0] or [self.clauses[0]] if self.clauses else []

    def get_grounded_clause_summary(self, query: str, product_name: str | None = None) -> str:
        """Get a concise, grounded policy document answer for the agent."""
        matching = self.retrieve_relevant_clauses(query, product_name=product_name, top_k=2)
        if not matching:
            return "No specific policy clause found for your query. Standard policy terms apply."

        snippets = []
        for c in matching:
            snippets.append(f"• **{c['title']}**: {c['content']}")

        return "\n".join(snippets)
