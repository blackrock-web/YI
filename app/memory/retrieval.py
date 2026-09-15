"""
MY AI - Deterministic Memory Retrieval System
Scores and ranks local memories using exact match, key token matching, importance weighting, and recency.
"""
from typing import List, Dict, Any, Optional
import math
from datetime import datetime

class MemoryRetriever:
    @staticmethod
    def score_memory(query: str, memory: Dict[str, Any]) -> float:
        """
        Deterministic scoring function:
        Score = TokenOverlap * 10 + ExactSubstring * 15 + (Importance / 10) * 5 + RecencyBonus
        """
        q_clean = query.lower().strip()
        key_raw = memory["key"].lower().strip()
        key_clean = key_raw.replace("_", " ")
        val_clean = memory["value"].lower().strip()
        
        score = 0.0
        
        # 1. Exact key match
        if q_clean == key_clean or q_clean == key_raw:
            score += 50.0
        elif key_clean in q_clean or key_raw in q_clean or q_clean in key_clean:
            score += 30.0
            
        # 2. Token overlap
        q_tokens = set(q_clean.split())
        key_tokens = set(key_clean.split())
        overlap = len(q_tokens.intersection(key_tokens))
        if len(key_tokens) > 0:
            score += (overlap / len(key_tokens)) * 20.0
            
        # Also check value tokens
        val_tokens = set(val_clean.split())
        val_overlap = len(q_tokens.intersection(val_tokens))
        if val_overlap > 0:
            score += val_overlap * 5.0
            
        # 3. Importance weighting (1 - 10)
        importance = memory.get("importance", 5) or 5
        score += (importance / 10.0) * 10.0
        
        # 4. Confidence weighting (0.0 - 1.0)
        confidence = memory.get("confidence", 1.0) or 1.0
        score *= confidence
        
        # 5. Recency weighting
        try:
            created_at_str = memory.get("updated_at") or memory.get("created_at")
            if created_at_str:
                created_dt = datetime.fromisoformat(created_at_str.replace("Z", ""))
                age_hours = (datetime.utcnow() - created_dt).total_seconds() / 3600.0
                recency_bonus = max(0.0, 5.0 - math.log1p(age_hours))
                score += recency_bonus
        except Exception:
            pass
            
        return score

    @classmethod
    def rank_memories(cls, query: str, memories: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        scored = []
        for mem in memories:
            s = cls.score_memory(query, mem)
            if s > 0:
                mem_copy = dict(mem)
                mem_copy["_retrieval_score"] = round(s, 2)
                scored.append(mem_copy)
                
        # Sort by score descending
        scored.sort(key=lambda x: x["_retrieval_score"], reverse=True)
        return scored[:limit]
