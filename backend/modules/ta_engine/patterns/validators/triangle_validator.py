"""
Triangle Validator
==================
Validates ascending, descending, and symmetrical triangles.

Triangle requirements:
- Upper line: 2+ touches
- Lower line: 2+ touches  
- Lines converging (apex in future)
- Price mostly contained within boundaries
- Recent formation (not too old)
"""

from __future__ import annotations

import uuid
import math
from typing import Any, Dict, List, Optional, Tuple

from ..pattern_candidate import PatternCandidate, PatternLine, PatternScores, PatternWindow


class TriangleValidator:
    """Validates triangle patterns with strict geometry checks."""
    
    pattern_type = "triangle"
    
    MIN_TOUCHES = 2
    MIN_SCORE_THRESHOLD = 0.55
    
    def validate(
        self,
        candles: List[Dict[str, Any]],
        pivot_highs: List[Dict[str, Any]],
        pivot_lows: List[Dict[str, Any]],
        window: PatternWindow,
        structure_context: Dict[str, Any],
        liquidity: Dict[str, Any],
        displacement: Dict[str, Any],
        poi: Dict[str, Any],
    ) -> Optional[PatternCandidate]:
        """Validate triangle pattern in given window."""
        
        if len(pivot_highs) < self.MIN_TOUCHES or len(pivot_lows) < self.MIN_TOUCHES:
            return None
        
        # Build upper and lower lines
        upper = self._build_trendline(pivot_highs, "upper")
        lower = self._build_trendline(pivot_lows, "lower")
        
        if not upper or not lower:
            return None
        
        # Classify triangle type
        triangle_type, direction = self._classify_triangle(upper, lower)
        if not triangle_type:
            return None
        
        # Calculate scores
        geometry = self._score_geometry(upper, lower, candles)
        touches = self._score_touches(upper, lower)
        containment = self._score_containment(candles, upper, lower)
        context_fit = self._score_context(structure_context, triangle_type)
        recency = self._score_recency(window, len(candles))
        cleanliness = self._score_cleanliness(candles, upper, lower)
        
        scores = PatternScores(
            geometry=geometry,
            touch_quality=touches,
            containment=containment,
            context_fit=context_fit,
            recency=recency,
            cleanliness=cleanliness,
        )
        
        if scores.total < self.MIN_SCORE_THRESHOLD:
            return None
        
        # Calculate breakout/invalidation levels
        breakout_level, invalidation_level = self._get_levels(upper, lower, direction, candles)
        
        return PatternCandidate(
            pattern_id=str(uuid.uuid4()),
            type=triangle_type,
            direction_bias=direction,
            state="forming",
            window=window,
            lines=[
                PatternLine(
                    name="upper",
                    points=upper["points"],
                    touches=upper["touches"],
                    slope=upper["slope"]
                ),
                PatternLine(
                    name="lower",
                    points=lower["points"],
                    touches=lower["touches"],
                    slope=lower["slope"]
                ),
            ],
            breakout_level=breakout_level,
            invalidation_level=invalidation_level,
            scores=scores,
            meta={
                "touches_upper": upper["touches"],
                "touches_lower": lower["touches"],
                "upper_slope": upper["slope"],
                "lower_slope": lower["slope"],
            }
        )
    
    def _build_trendline(
        self, 
        pivots: List[Dict[str, Any]], 
        side: str
    ) -> Optional[Dict[str, Any]]:
        """Build trendline from pivot points using linear regression."""
        if len(pivots) < 2:
            return None
        
        # Use last 4 pivots max for local pattern
        recent_pivots = pivots[-4:]
        
        # Extract x (index) and y (price) values
        xs = [p["index"] for p in recent_pivots]
        ys = [p["price"] for p in recent_pivots]
        
        # Linear regression
        n = len(xs)
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        sum_xx = sum(x * x for x in xs)
        
        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-10:
            return None
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate line points
        start_idx = recent_pivots[0]["index"]
        end_idx = recent_pivots[-1]["index"]
        
        start_price = slope * start_idx + intercept
        end_price = slope * end_idx + intercept
        
        # Count touches (pivots close to line)
        touches = self._count_touches(recent_pivots, slope, intercept)
        
        return {
            "points": [
                {"time": recent_pivots[0]["time"], "value": round(start_price, 2), "index": start_idx},
                {"time": recent_pivots[-1]["time"], "value": round(end_price, 2), "index": end_idx},
            ],
            "touches": touches,
            "slope": slope,
            "intercept": intercept,
        }
    
    def _count_touches(
        self, 
        pivots: List[Dict[str, Any]], 
        slope: float, 
        intercept: float
    ) -> int:
        """Count pivots that touch the trendline (within tolerance)."""
        touches = 0
        for p in pivots:
            expected = slope * p["index"] + intercept
            tolerance = abs(expected) * 0.02  # 2% tolerance
            if abs(p["price"] - expected) <= tolerance:
                touches += 1
        return max(touches, 2)  # At least 2 since we built from them
    
    def _classify_triangle(
        self, 
        upper: Dict[str, Any], 
        lower: Dict[str, Any]
    ) -> Tuple[Optional[str], str]:
        """Classify triangle type based on slopes."""
        upper_slope = upper["slope"]
        lower_slope = lower["slope"]
        
        # Slopes must be converging (different signs or both toward each other)
        if upper_slope > 0 and lower_slope < 0:
            # Lines diverging - not a triangle
            return None, "neutral"
        
        slope_diff = abs(upper_slope - lower_slope)
        if slope_diff < 0.0001:
            # Parallel lines - channel, not triangle
            return None, "neutral"
        
        # Descending triangle: upper descending, lower flat
        if upper_slope < -0.0001 and abs(lower_slope) < abs(upper_slope) * 0.5:
            return "descending_triangle", "bearish"
        
        # Ascending triangle: lower ascending, upper flat
        if lower_slope > 0.0001 and abs(upper_slope) < abs(lower_slope) * 0.5:
            return "ascending_triangle", "bullish"
        
        # Symmetrical triangle: both converging
        if upper_slope < 0 and lower_slope > 0:
            return "symmetrical_triangle", "neutral"
        
        # Falling wedge: both descending but lower more steeply
        if upper_slope < 0 and lower_slope < 0 and lower_slope < upper_slope:
            return "falling_wedge", "bullish"
        
        # Rising wedge: both ascending but upper more steeply
        if upper_slope > 0 and lower_slope > 0 and upper_slope > lower_slope:
            return "rising_wedge", "bearish"
        
        return "symmetrical_triangle", "neutral"
    
    def _score_geometry(
        self, 
        upper: Dict[str, Any], 
        lower: Dict[str, Any],
        candles: List[Dict[str, Any]]
    ) -> float:
        """Score based on convergence quality and angle."""
        upper_slope = upper["slope"]
        lower_slope = lower["slope"]
        
        # Check convergence rate
        convergence = abs(upper_slope - lower_slope)
        if convergence < 0.0001:
            return 0.3  # Too parallel
        
        # Calculate apex (intersection point)
        if abs(upper_slope - lower_slope) > 0.0001:
            apex_idx = (lower["intercept"] - upper["intercept"]) / (upper_slope - lower_slope)
            current_idx = candles[-1].get("index", len(candles) - 1) if candles else 0
            
            # Apex should be in the future but not too far
            apex_distance = apex_idx - current_idx
            if apex_distance < 0:
                return 0.4  # Apex already passed
            if apex_distance > len(candles):
                return 0.5  # Apex too far
            
            # Ideal: apex 10-50% of pattern length ahead
            pattern_len = upper["points"][-1]["index"] - upper["points"][0]["index"]
            ideal_distance = pattern_len * 0.3
            distance_score = 1.0 - min(abs(apex_distance - ideal_distance) / pattern_len, 1.0)
            
            return 0.6 + distance_score * 0.4
        
        return 0.5
    
    def _score_touches(self, upper: Dict[str, Any], lower: Dict[str, Any]) -> float:
        """Score based on number of valid touches."""
        total_touches = upper["touches"] + lower["touches"]
        # 4 touches minimum (2 each), 8+ is excellent
        return min(total_touches / 8.0, 1.0)
    
    def _score_containment(
        self, 
        candles: List[Dict[str, Any]], 
        upper: Dict[str, Any], 
        lower: Dict[str, Any]
    ) -> float:
        """Score based on price staying within boundaries."""
        if not candles:
            return 0.5
        
        start_idx = upper["points"][0].get("index", 0)
        end_idx = upper["points"][-1].get("index", len(candles) - 1)
        
        violations = 0
        total = 0
        
        for i, c in enumerate(candles):
            candle_idx = c.get("index", i)
            if candle_idx < start_idx or candle_idx > end_idx:
                continue
            
            total += 1
            upper_val = upper["slope"] * candle_idx + upper["intercept"]
            lower_val = lower["slope"] * candle_idx + lower["intercept"]
            
            # Check for violations (wicks outside)
            if c["high"] > upper_val * 1.02:  # 2% tolerance
                violations += 1
            if c["low"] < lower_val * 0.98:
                violations += 1
        
        if total == 0:
            return 0.5
        
        violation_rate = violations / (total * 2)  # 2 checks per candle
        return 1.0 - min(violation_rate, 1.0)
    
    def _score_context(self, structure_context: Dict[str, Any], triangle_type: str) -> float:
        """Score based on market regime alignment."""
        regime = structure_context.get("regime", "unknown")
        
        context_map = {
            "descending_triangle": {
                "trend_down": 0.9,
                "reversal_candidate": 0.8,
                "range": 0.7,
                "compression": 0.8,
            },
            "ascending_triangle": {
                "trend_up": 0.9,
                "reversal_candidate": 0.8,
                "range": 0.7,
                "compression": 0.8,
            },
            "symmetrical_triangle": {
                "range": 0.9,
                "compression": 0.9,
                "reversal_candidate": 0.7,
            },
            "falling_wedge": {
                "trend_down": 0.9,
                "reversal_candidate": 0.9,
            },
            "rising_wedge": {
                "trend_up": 0.9,
                "reversal_candidate": 0.9,
            },
        }
        
        type_context = context_map.get(triangle_type, {})
        return type_context.get(regime, 0.5)
    
    def _score_recency(self, window: PatternWindow, total_candles: int) -> float:
        """Score based on how recent the pattern is."""
        age = total_candles - 1 - window.end_index
        if age <= 5:
            return 1.0
        if age <= 15:
            return 0.8
        if age <= 30:
            return 0.5
        return 0.3
    
    def _score_cleanliness(
        self, 
        candles: List[Dict[str, Any]], 
        upper: Dict[str, Any], 
        lower: Dict[str, Any]
    ) -> float:
        """Score based on how clean/noise-free the pattern is."""
        if not candles:
            return 0.5
        
        # Check for large wicks/noise
        large_wicks = 0
        for c in candles[-20:]:  # Check recent candles
            body = abs(c["close"] - c["open"])
            total_range = c["high"] - c["low"]
            if total_range > 0 and body / total_range < 0.3:
                large_wicks += 1
        
        wick_ratio = large_wicks / min(len(candles), 20)
        return 1.0 - wick_ratio * 0.5
    
    def _get_levels(
        self, 
        upper: Dict[str, Any], 
        lower: Dict[str, Any], 
        direction: str,
        candles: List[Dict[str, Any]]
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate breakout and invalidation levels."""
        if not candles:
            return None, None
        
        current_idx = len(candles) - 1
        
        # Project lines to current position
        upper_now = upper["slope"] * current_idx + upper["intercept"]
        lower_now = lower["slope"] * current_idx + lower["intercept"]
        
        if direction == "bearish":
            breakout_level = round(lower_now, 2)
            invalidation_level = round(upper_now, 2)
        elif direction == "bullish":
            breakout_level = round(upper_now, 2)
            invalidation_level = round(lower_now, 2)
        else:
            # Neutral - could break either way
            breakout_level = round(upper_now, 2)
            invalidation_level = round(lower_now, 2)
        
        return breakout_level, invalidation_level
