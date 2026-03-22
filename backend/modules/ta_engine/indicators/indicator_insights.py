"""
Indicator Insights Engine
=========================
Transforms raw indicator values into meaningful interpretations.

For Research view, users need to understand:
- What the indicator state means
- What bias it suggests
- How strong the signal is
- One-line summary

Supported indicators:
- RSI: oversold/overbought states, momentum direction
- MACD: crossovers, momentum building/fading
- ADX: trend strength (future)
- Volume/OBV: confirmation (future)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SignalBias(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH_WEAKENING = "bullish_weakening"
    BEARISH_WEAKENING = "bearish_weakening"


class SignalStrength(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RSIInsight:
    """RSI interpretation with state, bias, and summary."""
    value: float
    state: str  # oversold, near_oversold, neutral, bullish_pressure, overbought
    bias: str   # bullish, bearish, neutral, bullish_weakening, bearish_weakening
    strength: str  # high, medium, low
    summary: str
    color: str  # For UI rendering
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MACDInsight:
    """MACD interpretation with state, bias, and summary."""
    macd_value: float
    signal_value: float
    histogram: float
    state: str  # bullish_crossover, bearish_crossover, bullish_momentum_building, bearish_momentum_fading, neutral
    bias: str
    strength: str
    summary: str
    color: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IndicatorInsights:
    """Container for all indicator insights."""
    rsi: Optional[RSIInsight] = None
    macd: Optional[MACDInsight] = None
    
    def to_dict(self) -> Dict:
        result = {}
        if self.rsi:
            result["rsi"] = self.rsi.to_dict()
        if self.macd:
            result["macd"] = self.macd.to_dict()
        return result


class IndicatorInsightsEngine:
    """
    Transforms raw indicator data into meaningful insights.
    
    RSI States:
    - 0-30: oversold
    - 30-40: near_oversold  
    - 40-60: neutral
    - 60-70: bullish_pressure
    - 70+: overbought
    
    MACD States:
    - bullish_crossover: MACD crosses above signal
    - bearish_crossover: MACD crosses below signal
    - bullish_momentum_building: histogram increasing (positive territory)
    - bearish_momentum_fading: histogram decreasing (negative but rising)
    - neutral: weak momentum, no clear direction
    """
    
    def __init__(self):
        self.rsi_thresholds = {
            "oversold": 30,
            "near_oversold": 40,
            "neutral_low": 45,
            "neutral_high": 55,
            "bullish_pressure": 60,
            "overbought": 70
        }
    
    def analyze(
        self,
        panes: List[Dict],
        lookback: int = 5
    ) -> IndicatorInsights:
        """
        Analyze indicator panes and generate insights.
        
        Args:
            panes: List of indicator pane data from indicator_visualization
            lookback: Number of periods to analyze for trend/momentum
        
        Returns:
            IndicatorInsights with RSI and MACD interpretations
        """
        insights = IndicatorInsights()
        
        for pane in panes:
            pane_id = pane.get("id", "").lower()
            
            if pane_id == "rsi":
                insights.rsi = self._analyze_rsi(pane, lookback)
            elif pane_id == "macd":
                insights.macd = self._analyze_macd(pane, lookback)
        
        return insights
    
    def _analyze_rsi(self, pane: Dict, lookback: int = 5) -> Optional[RSIInsight]:
        """Analyze RSI and return insight."""
        data = pane.get("data", [])
        if not data or len(data) < lookback:
            return None
        
        # Get current and recent values
        current_value = data[-1].get("value")
        if current_value is None:
            return None
        
        current_value = float(current_value)
        recent_values = [d.get("value", 0) for d in data[-lookback:]]
        
        # Determine state based on value
        state = self._get_rsi_state(current_value)
        
        # Determine direction/momentum
        avg_change = sum(recent_values[i] - recent_values[i-1] for i in range(1, len(recent_values))) / (len(recent_values) - 1)
        is_rising = avg_change > 0.5
        is_falling = avg_change < -0.5
        
        # Determine bias and summary
        bias, summary, strength = self._get_rsi_interpretation(
            current_value, state, is_rising, is_falling
        )
        
        # Color based on state
        color = self._get_rsi_color(state)
        
        return RSIInsight(
            value=round(current_value, 2),
            state=state,
            bias=bias,
            strength=strength,
            summary=summary,
            color=color
        )
    
    def _get_rsi_state(self, value: float) -> str:
        """Classify RSI value into state."""
        if value <= 30:
            return "oversold"
        elif value <= 40:
            return "near_oversold"
        elif value <= 60:
            return "neutral"
        elif value <= 70:
            return "bullish_pressure"
        else:
            return "overbought"
    
    def _get_rsi_interpretation(
        self, 
        value: float, 
        state: str, 
        is_rising: bool, 
        is_falling: bool
    ) -> tuple[str, str, str]:
        """Get bias, summary and strength for RSI."""
        
        if state == "oversold":
            if is_rising:
                return (
                    "bullish",
                    "RSI oversold and rising — potential reversal forming.",
                    "high"
                )
            else:
                return (
                    "bearish",
                    "RSI in oversold territory — extreme selling pressure.",
                    "medium"
                )
        
        elif state == "near_oversold":
            if is_rising:
                return (
                    "bearish_weakening",
                    "RSI near oversold, momentum weakening — watch for bounce.",
                    "medium"
                )
            else:
                return (
                    "bearish",
                    "RSI approaching oversold — downside momentum continues.",
                    "medium"
                )
        
        elif state == "neutral":
            if is_rising:
                return (
                    "neutral",
                    "RSI neutral, slight bullish tilt — no strong signal.",
                    "low"
                )
            elif is_falling:
                return (
                    "neutral",
                    "RSI neutral, slight bearish tilt — watching for direction.",
                    "low"
                )
            else:
                return (
                    "neutral",
                    "RSI in neutral zone — no clear momentum bias.",
                    "low"
                )
        
        elif state == "bullish_pressure":
            if is_rising:
                return (
                    "bullish",
                    "RSI showing bullish pressure — momentum building.",
                    "medium"
                )
            else:
                return (
                    "bullish_weakening",
                    "RSI in bullish zone but momentum fading.",
                    "low"
                )
        
        else:  # overbought
            if is_falling:
                return (
                    "bearish",
                    "RSI overbought and falling — potential reversal.",
                    "high"
                )
            else:
                return (
                    "bullish",
                    "RSI overbought — strong buying but stretched.",
                    "medium"
                )
    
    def _get_rsi_color(self, state: str) -> str:
        """Get color for RSI state visualization."""
        colors = {
            "oversold": "#22c55e",      # Green - potential buy
            "near_oversold": "#86efac",  # Light green
            "neutral": "#64748b",        # Gray
            "bullish_pressure": "#fbbf24", # Amber
            "overbought": "#ef4444"      # Red - potential sell
        }
        return colors.get(state, "#64748b")
    
    def _analyze_macd(self, pane: Dict, lookback: int = 5) -> Optional[MACDInsight]:
        """Analyze MACD with proper multi-factor classification."""
        data = pane.get("data", [])
        extra_lines = pane.get("extra_lines", [])
        
        if not data or len(data) < lookback:
            return None
        
        # Get MACD line values
        macd_value = data[-1].get("value")
        macd_prev = data[-2].get("value") if len(data) >= 2 else None
        if macd_value is None:
            return None
        macd_value = float(macd_value)
        
        # Get signal line and histogram from extra_lines
        signal_data = None
        histogram_data = None
        for line in extra_lines or []:
            line_id = (line.get("id") or line.get("name") or "").lower()
            if "signal" in line_id:
                signal_data = line.get("data", [])
            elif "histogram" in line_id or "hist" in line_id:
                histogram_data = line.get("data", [])
        
        # Get signal value
        signal_value = 0
        signal_prev = 0
        if signal_data and len(signal_data) > 0:
            signal_value = float(signal_data[-1].get("value", 0) or 0)
            if len(signal_data) >= 2:
                signal_prev = float(signal_data[-2].get("value", 0) or 0)
        
        # Get histogram values (current and previous for momentum)
        histogram = macd_value - signal_value
        histogram_prev = (float(macd_prev) - signal_prev) if macd_prev is not None else 0
        
        if histogram_data and len(histogram_data) >= 2:
            histogram = float(histogram_data[-1].get("value", 0) or 0)
            histogram_prev = float(histogram_data[-2].get("value", 0) or 0)
        
        # Multi-factor classification
        state, bias, strength, summary, color = self._classify_macd(
            macd_value, signal_value, histogram, histogram_prev
        )
        
        return MACDInsight(
            macd_value=round(macd_value, 2),
            signal_value=round(signal_value, 2),
            histogram=round(histogram, 2),
            state=state,
            bias=bias,
            strength=strength,
            summary=summary,
            color=color
        )
    
    def _classify_macd(
        self,
        macd_value: float,
        signal_value: float,
        histogram: float,
        histogram_prev: float
    ) -> tuple[str, str, str, str, str]:
        """
        Classify MACD based on 3 factors:
        1. Position relative to zero
        2. MACD line vs signal line
        3. Histogram dynamics (expanding/shrinking)
        """
        # Factor 1: Position relative to zero
        below_zero = macd_value < 0
        
        # Factor 2: MACD line vs signal
        above_signal = macd_value > signal_value
        
        # Factor 3: Histogram dynamics
        # Calculate percentage change to avoid false signals on small values
        if histogram_prev != 0:
            hist_change_pct = (abs(histogram) - abs(histogram_prev)) / abs(histogram_prev)
        else:
            hist_change_pct = 0
        
        hist_growing = hist_change_pct > 0.15  # 15% threshold for "growing"
        hist_shrinking = hist_change_pct < -0.15  # 15% threshold for "shrinking"
        hist_stable = not hist_growing and not hist_shrinking
        
        # Threshold for "small" histogram (weak momentum)
        hist_small = abs(histogram) < 100
        
        # Classification logic
        
        # NEUTRAL: very small histogram, no clear momentum
        if hist_small and abs(macd_value) < 200:
            return (
                "neutral",
                "neutral",
                "low",
                "MACD near zero — no clear momentum.",
                "#64748b"
            )
        
        # BULLISH cases
        if not below_zero:
            if above_signal and hist_growing:
                return (
                    "bullish_strong",
                    "bullish",
                    "high",
                    "MACD bullish — momentum building.",
                    "#22c55e"
                )
            elif hist_shrinking:
                return (
                    "bullish_weak",
                    "bullish_weakening",
                    "low",
                    "MACD positive but momentum fading.",
                    "#86efac"
                )
            else:
                return (
                    "bullish",
                    "bullish",
                    "medium",
                    "MACD above zero — bullish regime.",
                    "#22c55e"
                )
        
        # BEARISH cases
        if below_zero:
            if not above_signal and hist_growing:
                return (
                    "bearish_strong",
                    "bearish",
                    "high",
                    "MACD bearish — downside momentum building.",
                    "#ef4444"
                )
            elif hist_shrinking:
                return (
                    "bearish_weak",
                    "bearish_weakening",
                    "low",
                    "MACD negative but momentum weakening.",
                    "#fca5a5"
                )
            elif hist_stable:
                return (
                    "bearish",
                    "bearish",
                    "medium",
                    "MACD below zero — bearish regime.",
                    "#f87171"
                )
            else:
                return (
                    "bearish",
                    "bearish",
                    "medium",
                    "MACD below zero — bearish regime.",
                    "#f87171"
                )
        
        # Fallback
        return (
            "neutral",
            "neutral",
            "low",
            "MACD unclear — wait for direction.",
            "#64748b"
        )
    
    def _get_macd_color(self, state: str) -> str:
        """Get color for MACD state visualization."""
        colors = {
            "bullish_crossover": "#22c55e",
            "bullish_momentum_building": "#22c55e",
            "bullish_momentum_fading": "#86efac",
            "bullish_weak": "#a7f3d0",
            "bearish_crossover": "#ef4444",
            "bearish_momentum_building": "#ef4444",
            "bearish_momentum_fading": "#fca5a5",
            "bearish_weak": "#fecaca",
            "neutral": "#64748b"
        }
        return colors.get(state, "#64748b")


# Singleton instance
_insights_engine: Optional[IndicatorInsightsEngine] = None


def get_indicator_insights_engine() -> IndicatorInsightsEngine:
    """Get singleton instance of IndicatorInsightsEngine."""
    global _insights_engine
    if _insights_engine is None:
        _insights_engine = IndicatorInsightsEngine()
    return _insights_engine
