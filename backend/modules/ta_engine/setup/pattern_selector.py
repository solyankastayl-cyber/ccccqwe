"""
Pattern Selection Engine (PSE)
==============================

Final selection: Choose the best pattern WITH Market Context Scoring.

NOT just geometry scoring — FULL context validation:
  - geometry (25%)
  - structure alignment (20%)
  - liquidity alignment (20%)
  - location relevance (15%)
  - recency (10%)
  - confluence (10%)

Key rule: Better to show NOTHING than show a weak pattern.

If the best pattern doesn't meet minimum threshold → return None.
Also returns alternatives for user to see other possibilities.
"""

from typing import List, Optional, Tuple, Dict, Any
from .pattern_candidate import PatternCandidate


class PatternSelector:
    """
    Pattern Selection Engine — selects the best pattern using Market Context Scoring.
    
    FINAL SCORE calculation:
      geometry (25%) + structure_alignment (20%) + liquidity_alignment (20%)
      + location_relevance (15%) + recency (10%) + confluence (10%)
    
    Rules:
    1. Primary must exceed MIN_SCORE threshold (0.6)
    2. Pattern must be near current price (within 5%)
    3. If nothing qualifies → return None
    4. CHANNELS ARE NOT PATTERNS — they go to market_state
    """
    
    MIN_PRIMARY_SCORE = 0.45    # Primary pattern must score at least this (was 0.50)
    MIN_ALTERNATIVE_SCORE = 0.40  # Alternatives can be slightly lower
    MAX_ALTERNATIVES = 2         # Show up to 2 alternatives
    MAX_PRICE_DISTANCE = 0.15    # Pattern must be within 15% of current price (was 5%)
    
    # ═══════════════════════════════════════════════════════════════
    # FORBIDDEN PATTERN TYPES — these belong to MARKET STATE, not patterns
    # ═══════════════════════════════════════════════════════════════
    FORBIDDEN_AS_PATTERN = {
        "horizontal_channel",
        "ascending_channel", 
        "descending_channel",
        "channel",
        "range",
        "sideways",
        "trend",
        "uptrend",
        "downtrend",
        "compression",
        "expansion",
    }
    
    # Score weights
    WEIGHT_GEOMETRY = 0.25
    WEIGHT_STRUCTURE = 0.20
    WEIGHT_LIQUIDITY = 0.20
    WEIGHT_LOCATION = 0.15
    WEIGHT_RECENCY = 0.10
    WEIGHT_CONFLUENCE = 0.10
    
    def __init__(self):
        pass
    
    def _is_forbidden_pattern(self, pattern: PatternCandidate) -> bool:
        """
        Check if pattern type is FORBIDDEN as primary pattern.
        
        Channels, trends, ranges are NOT patterns — they belong to market_state.
        """
        if not pattern or not pattern.type:
            return False
        
        pattern_type = pattern.type.lower().replace(" ", "_").replace("-", "_")
        
        # Check exact match
        if pattern_type in self.FORBIDDEN_AS_PATTERN:
            return True
        
        # Check partial match (contains channel, trend, range)
        forbidden_keywords = ["channel", "trend", "range", "sideways", "compression", "expansion"]
        for keyword in forbidden_keywords:
            if keyword in pattern_type:
                return True
        
        return False
    
    def _is_near_price(self, pattern: PatternCandidate, current_price: float) -> bool:
        """Check if pattern is near current price."""
        if not current_price or current_price <= 0:
            return True
        
        # Get pattern mid price
        mid_price = pattern.breakout_level or pattern.invalidation
        if not mid_price:
            return True
        
        distance = abs(mid_price - current_price) / current_price
        return distance < self.MAX_PRICE_DISTANCE
    
    def _structure_alignment(self, pattern: PatternCandidate, context: Dict[str, Any]) -> float:
        """
        Calculate structure alignment score.
        
        bullish pattern + uptrend → +
        bullish pattern + downtrend → -
        """
        if not context:
            return 0.5
        
        pattern_dir = pattern.direction or "neutral"
        structure_bias = context.get("bias", "neutral")
        regime = context.get("regime", "unknown")
        
        # Perfect alignment
        if pattern_dir == "bullish" and structure_bias == "bullish":
            return 1.0
        if pattern_dir == "bearish" and structure_bias == "bearish":
            return 1.0
        
        # Conflict
        if pattern_dir == "bullish" and structure_bias == "bearish":
            return 0.2
        if pattern_dir == "bearish" and structure_bias == "bullish":
            return 0.2
        
        # Neutral
        return 0.5
    
    def _liquidity_alignment(self, pattern: PatternCandidate, liquidity: Dict[str, Any]) -> float:
        """
        Calculate liquidity alignment score.
        
        pattern near liquidity → +
        pattern after sweep → ++
        pattern in empty area → -
        """
        if not liquidity:
            return 0.5
        
        score = 0.5
        
        # Check for sweeps
        sweeps = liquidity.get("sweeps", [])
        if sweeps:
            score += 0.3  # Sweep detected → higher value
        
        # Check for liquidity pools near pattern
        pools = liquidity.get("pools", []) or liquidity.get("equal_highs", []) + liquidity.get("equal_lows", [])
        if pools:
            score += 0.2
        
        return min(1.0, score)
    
    def _location_relevance(self, pattern: PatternCandidate, current_price: float) -> float:
        """
        Calculate location relevance score.
        
        pattern near current price → +
        pattern far away → -
        """
        if not current_price or current_price <= 0:
            return 0.5
        
        mid_price = pattern.breakout_level or pattern.invalidation
        if not mid_price:
            return 0.5
        
        distance = abs(mid_price - current_price) / current_price
        
        if distance < 0.01:
            return 1.0
        if distance < 0.02:
            return 0.8
        if distance < 0.03:
            return 0.6
        if distance < 0.05:
            return 0.4
        return 0.2
    
    def _confluence_score(self, pattern: PatternCandidate, fib: Dict[str, Any], poi: Dict[str, Any]) -> float:
        """
        Calculate confluence score.
        
        fib coincides → +
        POI coincides → +
        """
        score = 0.5
        
        breakout = pattern.breakout_level
        if not breakout:
            return score
        
        # Check fib alignment
        if fib:
            levels = fib.get("levels", {})
            for key, val in levels.items():
                try:
                    fib_price = float(val) if not isinstance(val, dict) else float(val.get("price", 0))
                    if abs(fib_price - breakout) / max(breakout, 1) < 0.02:
                        score += 0.25
                        break
                except:
                    pass
        
        # Check POI alignment
        if poi:
            zones = poi.get("zones", [])
            for z in zones:
                zl = float(z.get("price_low", z.get("lower", 0)))
                zh = float(z.get("price_high", z.get("upper", 0)))
                if zl <= breakout <= zh:
                    score += 0.25
                    break
        
        return min(1.0, score)
    
    def calculate_market_context_score(
        self,
        pattern: PatternCandidate,
        current_price: float,
        structure_context: Dict[str, Any] = None,
        liquidity: Dict[str, Any] = None,
        fib: Dict[str, Any] = None,
        poi: Dict[str, Any] = None,
    ) -> float:
        """
        Calculate final score with Market Context Scoring.
        
        FINAL SCORE =
          geometry (25%) + structure_alignment (20%) + liquidity_alignment (20%)
          + location_relevance (15%) + recency (10%) + confluence (10%)
        """
        geometry = pattern.geometry_score or 0.5
        structure = self._structure_alignment(pattern, structure_context)
        liquidity_score = self._liquidity_alignment(pattern, liquidity)
        location = self._location_relevance(pattern, current_price)
        recency = pattern.recency_score or 0.5
        confluence = self._confluence_score(pattern, fib, poi)
        
        final_score = (
            geometry * self.WEIGHT_GEOMETRY +
            structure * self.WEIGHT_STRUCTURE +
            liquidity_score * self.WEIGHT_LIQUIDITY +
            location * self.WEIGHT_LOCATION +
            recency * self.WEIGHT_RECENCY +
            confluence * self.WEIGHT_CONFLUENCE
        )
        
        return final_score

    def select(
        self, 
        ranked_candidates: List[PatternCandidate],
        current_price: float = None,
        structure_context: Dict[str, Any] = None,
        liquidity: Dict[str, Any] = None,
        fib: Dict[str, Any] = None,
        poi: Dict[str, Any] = None,
    ) -> Tuple[Optional[PatternCandidate], List[PatternCandidate]]:
        """
        Select primary pattern and alternatives using Market Context Scoring.
        
        Args:
            ranked_candidates: Candidates sorted by total_score (highest first)
            current_price: Current market price
            structure_context: Market structure data
            liquidity: Liquidity data
            fib: Fibonacci data
            poi: POI zones data
            
        Returns:
            (primary, alternatives) tuple
            primary is None if nothing qualifies
            
        IMPORTANT: Channels/ranges/trends are FORBIDDEN as patterns.
                   They belong to market_state layer, not pattern layer.
        """
        if not ranked_candidates:
            return None, []
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: FILTER OUT FORBIDDEN PATTERNS (channels, trends, ranges)
        # ═══════════════════════════════════════════════════════════════
        valid_candidates = []
        for c in ranked_candidates:
            if self._is_forbidden_pattern(c):
                print(f"[PatternSelector] FORBIDDEN: {c.type} is market_state, not pattern")
                continue
            valid_candidates.append(c)
        
        if not valid_candidates:
            print(f"[PatternSelector] No valid patterns after filtering forbidden types")
            return None, []
        
        # Re-score with market context if data available
        if current_price:
            for c in valid_candidates:
                if not self._is_near_price(c, current_price):
                    c.total_score = 0  # Reject patterns far from price
                    continue
                
                # Calculate market context score
                ctx_score = self.calculate_market_context_score(
                    c, current_price, structure_context, liquidity, fib, poi
                )
                # Blend with existing score (50/50)
                c.total_score = (c.total_score + ctx_score) / 2
            
            # Re-sort after context scoring
            valid_candidates.sort(key=lambda x: x.total_score, reverse=True)

        primary = valid_candidates[0] if valid_candidates else None

        # Hard filter: primary must meet minimum threshold
        if primary:
            print(f"[PatternSelector] Primary candidate: {primary.type}, score={primary.total_score:.3f}, min={self.MIN_PRIMARY_SCORE}")
        
        if not primary or primary.total_score < self.MIN_PRIMARY_SCORE:
            if primary:
                print(f"[PatternSelector] REJECTED: score {primary.total_score:.3f} < {self.MIN_PRIMARY_SCORE}")
            return None, []

        # Get alternatives (next best patterns that also qualify)
        alternatives = []
        for c in valid_candidates[1:]:
            if c.total_score >= self.MIN_ALTERNATIVE_SCORE:
                alternatives.append(c)
            if len(alternatives) >= self.MAX_ALTERNATIVES:
                break
        
        return primary, alternatives
    
    def explain_selection(
        self, 
        primary: Optional[PatternCandidate],
        alternatives: List[PatternCandidate]
    ) -> dict:
        """Generate explanation for the selection."""
        if primary is None:
            return {
                "status": "no_pattern",
                "reason": "No pattern met minimum quality threshold",
                "suggestion": "Market may be in unclear/choppy state"
            }
        
        # Build explanation
        explanation = {
            "status": "pattern_found",
            "primary": {
                "type": primary.type,
                "score": round(primary.total_score, 2),
                "strengths": [],
                "weaknesses": []
            }
        }
        
        # Identify strengths
        if primary.structure_score > 0.7:
            explanation["primary"]["strengths"].append("Aligns with market structure")
        if primary.recency_score > 0.7:
            explanation["primary"]["strengths"].append("Recently tested")
        if primary.geometry_score > 0.7:
            explanation["primary"]["strengths"].append("Clean geometry")
        
        # Identify weaknesses
        if primary.structure_score < 0.4:
            explanation["primary"]["weaknesses"].append("Conflicts with market regime")
        if primary.recency_score < 0.4:
            explanation["primary"]["weaknesses"].append("Last touch was long ago")
        if primary.level_score < 0.4:
            explanation["primary"]["weaknesses"].append("Far from key levels")
        
        if alternatives:
            explanation["alternatives_count"] = len(alternatives)
            explanation["alternatives"] = [
                {"type": a.type, "score": round(a.total_score, 2)}
                for a in alternatives
            ]
        
        return explanation


# Singleton instance
pattern_selector = PatternSelector()
