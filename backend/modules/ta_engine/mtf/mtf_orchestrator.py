"""
MTF Orchestrator
================

Multi-Timeframe Orchestration Layer.

NOT mixing signals — HIERARCHICAL context:
  HTF → bias layer (1D/30D/180D)
  MTF → setup layer (4H/1D)
  LTF → entry layer (1H/4H)

Each timeframe is its own world.
Orchestrator only combines CONTEXTS, not signals.

Output:
  {
    "bias_tf": "1D",
    "setup_tf": "4H", 
    "entry_tf": "1H",
    "global_bias": "bearish",
    "alignment": "counter_trend",
    "tradeability": "low",
    "summary": "...",
    "timeframes": {...}
  }
"""

from __future__ import annotations
from typing import Dict, Any, Optional


class MTFOrchestrator:
    """
    Orchestrates multiple timeframe contexts into one coherent view.
    
    Key principle:
    - HTF controls direction filter
    - MTF selects setup
    - LTF refines entry
    
    Does NOT mix indicators/patterns across TFs.
    Only provides alignment and tradeability assessment.
    """

    def build(
        self,
        tf_map: Dict[str, Dict[str, Any]],
        bias_tf: str = "1D",
        setup_tf: str = "4H",
        entry_tf: str = "1H",
    ) -> Dict[str, Any]:
        """
        Build MTF orchestration from per-timeframe TA data.
        
        Args:
            tf_map: Dict of {timeframe: ta_payload}
            bias_tf: Higher timeframe for direction bias
            setup_tf: Setup timeframe for pattern/setup selection
            entry_tf: Lower timeframe for entry refinement
        """
        htf = tf_map.get(bias_tf, {})
        stf = tf_map.get(setup_tf, {})
        ltf = tf_map.get(entry_tf, {})

        global_bias = self._extract_bias(htf)
        setup_bias = self._extract_bias(stf)
        entry_bias = self._extract_bias(ltf)

        alignment = self._compute_alignment(global_bias, setup_bias, entry_bias)
        tradeability = self._compute_tradeability(
            global_bias=global_bias,
            setup=stf.get("unified_setup"),
            entry=ltf.get("trade_setup"),
            alignment=alignment,
        )

        return {
            "bias_tf": bias_tf,
            "setup_tf": setup_tf,
            "entry_tf": entry_tf,
            "global_bias": global_bias,
            "setup_bias": setup_bias,
            "entry_bias": entry_bias,
            "alignment": alignment,
            "tradeability": tradeability,
            "summary": self._build_summary(global_bias, stf, ltf, alignment),
            "timeframes": {
                bias_tf: self._compact(htf, bias_tf),
                setup_tf: self._compact(stf, setup_tf),
                entry_tf: self._compact(ltf, entry_tf),
            },
        }

    def _extract_bias(self, tf_payload: Dict[str, Any]) -> str:
        """Extract directional bias from timeframe payload."""
        if not tf_payload:
            return "neutral"
        
        # Try decision first
        decision = tf_payload.get("decision") or {}
        bias = decision.get("bias") or decision.get("direction")
        if bias and bias != "neutral":
            return bias.lower()
        
        # Try structure context
        structure = tf_payload.get("structure_context") or {}
        struct_bias = structure.get("bias")
        if struct_bias and struct_bias != "neutral":
            return struct_bias.lower()
        
        # Try unified setup
        unified = tf_payload.get("unified_setup") or {}
        unified_dir = unified.get("direction")
        if unified_dir and unified_dir not in {"no_trade", "neutral"}:
            return "bullish" if unified_dir == "long" else "bearish"
        
        return "neutral"

    def _compute_alignment(self, global_bias: str, setup_bias: str, entry_bias: str) -> str:
        """
        Compute alignment between timeframes.
        
        aligned: all TFs agree
        counter_trend: setup against HTF
        mixed: no clear alignment
        """
        if global_bias == "neutral":
            return "mixed"
        
        # Perfect alignment
        if setup_bias == global_bias and entry_bias in {global_bias, "neutral"}:
            return "aligned"
        
        # Setup against HTF bias
        if setup_bias != "neutral" and setup_bias != global_bias:
            return "counter_trend"
        
        # Entry against but setup aligned
        if setup_bias == global_bias and entry_bias != "neutral" and entry_bias != global_bias:
            return "mixed"
        
        return "mixed"

    def _compute_tradeability(
        self,
        global_bias: str,
        setup: Optional[Dict[str, Any]],
        entry: Optional[Dict[str, Any]],
        alignment: str,
    ) -> str:
        """
        Compute overall tradeability score.
        
        high: aligned + valid setup + valid entry
        medium: some conditions met
        low: counter-trend or missing validations
        """
        # No valid setup = low
        if not setup or not setup.get("valid", False):
            return "low"
        
        # Check entry
        entry_valid = False
        if entry:
            primary = entry.get("primary", {})
            entry_valid = primary.get("valid", False)
        
        # Perfect conditions
        if alignment == "aligned" and global_bias != "neutral" and entry_valid:
            return "high"
        
        # Good setup but no entry yet
        if alignment == "aligned" and global_bias != "neutral":
            return "medium"
        
        # Counter-trend = always low
        if alignment == "counter_trend":
            return "low"
        
        return "medium"

    def _build_summary(
        self,
        global_bias: str,
        stf: Dict[str, Any],
        ltf: Dict[str, Any],
        alignment: str,
    ) -> str:
        """Build human-readable summary."""
        parts = []
        
        # HTF bias
        parts.append(f"Higher timeframe {global_bias}")
        
        # Setup pattern
        pattern = (stf.get("primary_pattern") or stf.get("pattern_v2", {}).get("primary_pattern") or {}).get("type")
        if pattern:
            pattern_bias = (stf.get("primary_pattern") or {}).get("direction_bias", "")
            if pattern_bias:
                parts.append(f"setup shows {pattern} ({pattern_bias})")
            else:
                parts.append(f"setup shows {pattern}")
        
        # Entry direction
        entry_setup = (ltf.get("trade_setup") or {}).get("primary") or {}
        entry_dir = entry_setup.get("direction")
        if entry_dir:
            parts.append(f"entry favors {entry_dir}")
        
        # Alignment
        if alignment == "counter_trend":
            parts.append("WARNING: counter-trend setup")
        elif alignment == "aligned":
            parts.append("timeframes aligned")
        
        return ". ".join(parts) + "."

    def _compact(self, payload: Dict[str, Any], tf: str) -> Dict[str, Any]:
        """Extract compact view of timeframe data."""
        decision = payload.get("decision", {})
        pattern = payload.get("primary_pattern") or (payload.get("pattern_v2") or {}).get("primary_pattern")
        
        return {
            "timeframe": tf,
            "bias": self._extract_bias(payload),
            "regime": (payload.get("structure_context") or {}).get("regime"),
            "pattern": {
                "type": pattern.get("type") if pattern else None,
                "direction_bias": pattern.get("direction_bias") if pattern else None,
                "score": pattern.get("score") if pattern else None,
            } if pattern else None,
            "unified_setup_valid": (payload.get("unified_setup") or {}).get("valid", False),
            "trade_setup_valid": ((payload.get("trade_setup") or {}).get("primary") or {}).get("valid", False),
        }


# Factory function
_mtf_orchestrator = None

def get_mtf_orchestrator() -> MTFOrchestrator:
    global _mtf_orchestrator
    if _mtf_orchestrator is None:
        _mtf_orchestrator = MTFOrchestrator()
    return _mtf_orchestrator
