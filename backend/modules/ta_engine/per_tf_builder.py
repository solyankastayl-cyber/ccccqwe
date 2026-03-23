"""
Per-Timeframe TA Builder
========================

Builds COMPLETE TA payload for a single timeframe.
Each TF is an isolated world — NO mixing between timeframes.

Output for each TF:
  {
    "timeframe": "4H",
    "candles": [...],
    "decision": {...},
    "structure_context": {...},
    "liquidity": {...},
    "displacement": {...},
    "fib": {...},
    "poi": {...},
    "primary_pattern": {...},
    "unified_setup": {...},
    "trade_setup": {...},
    "execution": {...},
    "base_layer": {...},
    "chain_map": [...]   # For chain highlighting
  }
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Import all engines
from modules.ta_engine.setup.pattern_validator_v2 import get_pattern_validator_v2
from modules.ta_engine.setup.structure_engine_v2 import get_structure_engine_v2
from modules.ta_engine.setup.structure_context_engine import structure_context_engine
from modules.ta_engine.setup.pattern_ranking_engine import pattern_ranking_engine
from modules.ta_engine.setup.pattern_selector import get_pattern_selector

# Get singleton instance
pattern_selector = get_pattern_selector()
from modules.ta_engine.setup.pattern_expiration import pattern_expiration_engine
from modules.ta_engine.setup.pattern_registry import run_all_detectors, filter_by_structure, penalize_overused_patterns, validate_candidate

# IMPORTANT: Import pattern_detectors_unified to register all detectors
# This triggers @register_pattern decorators at import time
from modules.ta_engine.setup import pattern_detectors_unified  # noqa: F401

from modules.ta_engine.decision import get_decision_engine_v2
from modules.ta_engine.scenario import get_scenario_engine_v3
from modules.ta_engine.structure import get_choch_validation_engine
from modules.ta_engine.liquidity import get_liquidity_engine
from modules.ta_engine.displacement import get_displacement_engine
from modules.ta_engine.poi import get_poi_engine
from modules.ta_engine.fibonacci import get_fibonacci_engine
from modules.ta_engine.trade_setup import get_trade_setup_generator
from modules.ta_engine.setup.unified_setup_engine import get_unified_setup_engine
from modules.ta_engine.execution import get_execution_layer
from modules.ta_engine.setup.indicator_engine import get_indicator_engine
from modules.ta_engine.indicators import get_indicator_registry, get_confluence_engine
from modules.ta_engine.indicators.indicator_visualization import IndicatorVisualizationEngine
from modules.ta_engine.indicators.indicator_insights import get_indicator_insights_engine
from modules.ta_engine.contribution import get_contribution_engine
from modules.ta_engine.render_plan import get_render_plan_engine_v2
from modules.ta_engine.market_state import get_market_state_engine
from modules.ta_engine.patterns.pattern_geometry_contract import normalize_pattern_geometry
from modules.ta_engine.structure import StructureVisualizationBuilder


# Singleton for visualization engine
_indicator_viz_engine = None
_render_plan_engine_v2 = None
_market_state_engine = None
_structure_viz_builder = None

def get_indicator_viz_engine():
    global _indicator_viz_engine
    if _indicator_viz_engine is None:
        _indicator_viz_engine = IndicatorVisualizationEngine()
    return _indicator_viz_engine

def _get_render_plan_engine():
    global _render_plan_engine_v2
    if _render_plan_engine_v2 is None:
        _render_plan_engine_v2 = get_render_plan_engine_v2()
    return _render_plan_engine_v2

def _get_market_state_engine():
    global _market_state_engine
    if _market_state_engine is None:
        _market_state_engine = get_market_state_engine()
    return _market_state_engine

def _get_structure_viz_builder():
    global _structure_viz_builder
    if _structure_viz_builder is None:
        _structure_viz_builder = StructureVisualizationBuilder()
    return _structure_viz_builder


# TF Configuration
TF_CONFIG = {
    "1H": {
        "lookback": 168,        # 7 days of hourly
        "pivot_window": 2,
        "min_pivot_distance": 3,
        "pattern_window": 120,
        "candle_type": "1h",
        "description": "Micro entry timing"
    },
    "4H": {
        "lookback": 200,
        "pivot_window": 3,
        "min_pivot_distance": 5,
        "pattern_window": 150,
        "candle_type": "4h",
        "description": "Entry timing"
    },
    "1D": {
        "lookback": 150,
        "pivot_window": 5,
        "min_pivot_distance": 8,
        "pattern_window": 100,
        "candle_type": "1d",
        "description": "Setup patterns"
    },
    "7D": {
        "lookback": 65,        # ~65 weekly candles = ~1.2 years
        "pivot_window": 2,      # Smaller for aggregated data
        "min_pivot_distance": 2,
        "pattern_window": 50,
        "candle_type": "7d",
        "description": "Weekly formations"
    },
    "30D": {
        "lookback": 42,         # ~42 monthly candles = ~3.5 years
        "pivot_window": 2,      # Very small for monthly
        "min_pivot_distance": 1,
        "pattern_window": 30,
        "candle_type": "30d",
        "description": "Monthly structure"
    },
    "180D": {
        "lookback": 12,         # ~12 half-year candles = ~6 years
        "pivot_window": 1,      # Minimal for 6-month
        "min_pivot_distance": 1,
        "pattern_window": 10,
        "candle_type": "180d",
        "description": "Macro cycles"
    },
    "1Y": {
        "lookback": 11,         # ~11 yearly candles = ~11 years
        "pivot_window": 1,      # Minimal for yearly
        "min_pivot_distance": 1,
        "pattern_window": 8,
        "candle_type": "1Y",
        "description": "Secular trends"
    },
}


class PerTimeframeBuilder:
    """
    Builds complete TA payload for ONE timeframe.
    Isolated from other timeframes — each TF is its own world.
    """
    
    def build(
        self,
        candles: List[Dict[str, Any]],
        symbol: str,
        timeframe: str,
        mtf_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build complete TA for a single timeframe.
        
        Args:
            candles: OHLCV candles for this specific timeframe
            symbol: Trading pair (e.g., "BTCUSDT")
            timeframe: The timeframe string (e.g., "4H", "1D")
            mtf_context: Optional MTF context for alignment calculation
        """
        import time as time_module
        start_time = time_module.time()
        print(f"[PerTF] Starting build for {symbol}:{timeframe} with {len(candles)} candles")
        
        config = TF_CONFIG.get(timeframe, TF_CONFIG["1D"])
        
        # Minimum candles depends on timeframe
        # Higher TFs like 180D and 1Y have limited historical data
        MIN_CANDLES_MAP = {
            "1H": 30,
            "4H": 30,
            "1D": 30,
            "7D": 20,
            "30D": 10,
            "180D": 5,
            "1Y": 5,
        }
        min_candles = MIN_CANDLES_MAP.get(timeframe.upper(), 30)
        
        # Empty result template
        empty = self._empty_result(timeframe, symbol)
        
        if len(candles) < min_candles:
            print(f"[PerTF] Not enough candles ({len(candles)} < {min_candles})")
            return empty
        
        current_price = float(candles[-1]["close"])
        
        # =============================================
        # STEP 1: STRUCTURE ANALYSIS (FIRST!)
        # =============================================
        print(f"[PerTF] Step 1: Structure analysis...")
        structure_v2 = get_structure_engine_v2(timeframe)
        validator = get_pattern_validator_v2(timeframe.upper(), config)
        pivot_highs_raw, pivot_lows_raw = validator.find_pivots(candles)
        print(f"[PerTF] Found {len(pivot_highs_raw)} highs, {len(pivot_lows_raw)} lows")
        
        # Convert Pivot objects to dicts for engines that need dict
        pivot_highs = [
            {"price": p.value, "index": p.index, "time": p.time}
            for p in pivot_highs_raw
        ]
        pivot_lows = [
            {"price": p.value, "index": p.index, "time": p.time}
            for p in pivot_lows_raw
        ]
        
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            print(f"[PerTF] Not enough pivots (highs={len(pivot_highs)}, lows={len(pivot_lows)})")
            # For higher timeframes with limited data, proceed with available pivots
            if timeframe.upper() in ("180D", "1Y") and (len(pivot_highs) >= 1 or len(pivot_lows) >= 1):
                print(f"[PerTF] Proceeding with limited pivots for {timeframe}")
            else:
                return empty
        
        print(f"[PerTF] Building structure_state...")
        structure_state = structure_v2.build(
            candles=candles,
            pivots_high=pivot_highs,
            pivots_low=pivot_lows,
        )
        
        print(f"[PerTF] Building structure_context...")
        structure_context = structure_context_engine.build(
            candles=candles,
            pivots_high=pivot_highs,
            pivots_low=pivot_lows,
        )
        
        # Convert to dict for engines that need dict
        structure_context_dict = structure_context.to_dict()
        
        # =============================================
        # STEP 2: LIQUIDITY & DISPLACEMENT
        # =============================================
        print(f"[PerTF] Step 2: Liquidity & Displacement...")
        liquidity_engine = get_liquidity_engine()
        liquidity = liquidity_engine.build(candles)
        
        displacement_engine = get_displacement_engine()
        displacement = displacement_engine.build(candles)
        
        # =============================================
        # STEP 3: CHOCH VALIDATION
        # =============================================
        print(f"[PerTF] Step 3: CHOCH validation...")
        choch_engine = get_choch_validation_engine()
        choch_validation = choch_engine.build(
            structure_context=structure_context_dict,
            liquidity=liquidity,
            displacement=displacement,
            base_layer={},
        )
        
        # =============================================
        # STEP 4: POI & FIBONACCI
        # =============================================
        print(f"[PerTF] Step 4: POI & Fibonacci...")
        poi_engine = get_poi_engine()
        poi = poi_engine.build(candles, displacement)
        
        fib_engine = get_fibonacci_engine()
        fib = fib_engine.build(candles, pivot_highs, pivot_lows, structure_context_dict, timeframe)
        
        # =============================================
        # STEP 5: PATTERN DETECTION
        # =============================================
        print(f"[PerTF] Step 5: Pattern detection...")
        # Run all detectors with correct arguments
        all_candidates = run_all_detectors(
            candles=candles,
            pivots_high=pivot_highs_raw,
            pivots_low=pivot_lows_raw,
            levels=[],  # Levels calculated after patterns
            structure_ctx=structure_context,
            timeframe=timeframe,
            config=config
        )
        print(f"[PerTF] Pattern candidates found: {len(all_candidates)}")
        for c in all_candidates:
            print(f"[PerTF]   - {c.type}: geo={c.geometry_score:.2f}, conf={c.confidence:.2f}")
        
        # Validate and filter
        validated = [c for c in all_candidates if validate_candidate(c)]
        print(f"[PerTF] After validation: {len(validated)}")
        
        gated = filter_by_structure(validated, structure_context)
        print(f"[PerTF] After structure filter: {len(gated)}")
        
        # Hard filter for recency
        filtered = self._hard_filter_recency(gated, candles)
        print(f"[PerTF] After recency filter: {len(filtered)}")
        
        # Expire old patterns
        live = pattern_expiration_engine.filter_expired(filtered, len(candles) - 1, timeframe)
        print(f"[PerTF] After expiration: {len(live)}")
        
        # Rank patterns
        ranked = pattern_ranking_engine.rank(
            candidates=live,
            structure_ctx=structure_context,
            levels=[],
            current_price=current_price,
        )
        
        # Penalize overused
        diversified = penalize_overused_patterns(ranked)
        
        # Select best with market context using PSE v2.0
        primary_pattern, alternatives = pattern_selector.select(
            diversified,
            candles=candles,
            current_price=current_price,
            market_state=structure_context_dict,
            structure_context=structure_context_dict,
            levels=[],  # Levels calculated later
            liquidity=liquidity,
            fib=fib,
            poi=poi,
        )
        print(f"[PerTF] Pattern selected: {primary_pattern.type if primary_pattern else 'None'}")
        
        # =============================================
        # STEP 6: INDICATORS & TA CONTEXT
        # =============================================
        print(f"[PerTF] Step 6: Indicators...")
        indicator_engine = get_indicator_engine()
        indicator_result = indicator_engine.analyze_all(candles)
        
        # Convert indicator results to dict format expected by decision engine
        indicator_signals = [s.to_dict() if hasattr(s, 'to_dict') else s for s in indicator_result] if indicator_result else []
        
        # Count bullish/bearish signals
        bullish_count = sum(1 for s in indicator_signals if s.get('bias') == 'bullish')
        bearish_count = sum(1 for s in indicator_signals if s.get('bias') == 'bearish')
        neutral_count = len(indicator_signals) - bullish_count - bearish_count
        
        # Compute indicator visualization data (overlays + panes for chart)
        print(f"[PerTF] Step 6b: Indicator visualization...")
        indicator_viz_engine = get_indicator_viz_engine()
        indicators_viz = indicator_viz_engine.compute_all(candles)
        
        # Compute indicator insights (interpretations for Research view)
        print(f"[PerTF] Step 6c: Indicator insights...")
        insights_engine = get_indicator_insights_engine()
        indicator_insights = insights_engine.analyze(indicators_viz.get("panes", []))
        
        # Build TA context with proper structure
        ta_context = {
            "regime": structure_context.regime if structure_context else "unknown",
            "bias": structure_context.bias if structure_context else "neutral",
            "indicators": {
                "total": len(indicator_signals),
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": neutral_count,
                "signals": indicator_signals,
            },
            "pattern": primary_pattern.to_dict() if primary_pattern else None,
        }
        
        # =============================================
        # STEP 7: DECISION ENGINE
        # =============================================
        print(f"[PerTF] Step 7: Decision engine...")
        decision_engine = get_decision_engine_v2()
        decision = decision_engine.build(
            mtf_context=mtf_context or {},
            structure_context=structure_context_dict,
            primary_pattern=primary_pattern.to_dict() if primary_pattern else None,
            ta_context=ta_context,
        )
        
        # =============================================
        # STEP 8: UNIFIED SETUP & TRADE SETUP
        # =============================================
        print(f"[PerTF] Step 8: Unified setup...")
        unified_engine = get_unified_setup_engine()
        unified_setup = unified_engine.build(
            decision=decision,
            structure_context=structure_context_dict,
            liquidity=liquidity,
            displacement=displacement,
            choch_validation=choch_validation,
            poi=poi,
            fib=fib,
            active_pattern=primary_pattern.to_dict() if primary_pattern else None,
            ta_context=ta_context,
            current_price=current_price,
        )
        
        trade_setup_gen = get_trade_setup_generator()
        trade_setup = trade_setup_gen.build(
            decision=decision,
            scenarios=[],  # No scenarios in per-TF mode
            base_layer={},
            structure_context=structure_context_dict,
            current_price=current_price,
        )
        
        # =============================================
        # STEP 9: EXECUTION LAYER
        # =============================================
        print(f"[PerTF] Step 9: Execution layer...")
        execution_layer = get_execution_layer()
        
        # Use MTF context if provided, otherwise create simple context
        exec_mtf_context = mtf_context or {
            "alignment": "mixed",
            "tradeability": "medium",
        }
        
        execution = execution_layer.build(
            mtf_context=exec_mtf_context,
            unified_setup=unified_setup,
            trade_setup=trade_setup,
            active_pattern=primary_pattern.to_dict() if primary_pattern else None,
            poi=poi,
            fib=fib,
            current_price=current_price,
        )
        print(f"[PerTF] Execution status: {execution.get('status')}")
        
        # =============================================
        # STEP 10: BUILD CHAIN MAP (for highlighting)
        # =============================================
        print(f"[PerTF] Step 10: Chain map...")
        chain_map = self._build_chain_map(
            unified_setup=unified_setup,
            liquidity=liquidity,
            displacement=displacement,
            choch_validation=choch_validation,
            poi=poi,
            primary_pattern=primary_pattern.to_dict() if primary_pattern else None,
            candles=candles,
        )
        
        # =============================================
        # STEP 11: BUILD RENDER PLAN V2 (for clean chart rendering)
        # =============================================
        print(f"[PerTF] Step 11: Render plan v2...")
        try:
            # Compute market state
            ms_engine = _get_market_state_engine()
            market_state = ms_engine.analyze(candles)
            
            # Build structure visualization with swings
            viz_builder = _get_structure_viz_builder()
            structure_viz = viz_builder.build(
                pivots_high=pivot_highs_raw,
                pivots_low=pivot_lows_raw,
                structure_context=structure_context_dict,
                candles=candles,
            )
            
            # Merge structure_context with visualization
            events = structure_viz.get("events", [])
            bos_event = next((e for e in events if "bos" in e.get("type", "")), None)
            choch_event = next((e for e in events if "choch" in e.get("type", "")), None)
            
            structure_for_render = {
                **structure_context_dict,
                "swings": structure_viz.get("pivot_points", []),
                "bos": bos_event,
                "choch": choch_event,
            }
            
            # Get patterns as list
            patterns = []
            if primary_pattern:
                patterns.append(primary_pattern.to_dict())
            
            # Build render plan
            rp_engine = _get_render_plan_engine()
            render_plan = rp_engine.build(
                timeframe=timeframe,
                current_price=current_price,
                market_state=market_state.to_dict(),
                structure=structure_for_render,
                indicators=indicators_viz,
                patterns=patterns,
                liquidity=liquidity,
                execution=execution,
                poi=poi,
            )
            print(f"[PerTF] Render plan built: swings={len(render_plan.get('structure', {}).get('swings', []))}")
        except Exception as e:
            print(f"[PerTF] Render plan error: {e}")
            render_plan = None
        
        # =============================================
        # ASSEMBLE RESULT
        # =============================================
        elapsed = time_module.time() - start_time
        print(f"[PerTF] Build completed in {elapsed:.2f}s")
        
        return {
            "timeframe": timeframe,
            "symbol": symbol,
            "candles": candles,
            "candle_count": len(candles),
            "current_price": current_price,
            
            # Structure (use dict, not object)
            "structure_context": structure_context_dict,
            "structure_state": structure_state.to_dict() if hasattr(structure_state, 'to_dict') else structure_state,
            
            # Smart Money
            "liquidity": liquidity,
            "displacement": displacement,
            "choch_validation": choch_validation,
            "poi": poi,
            "fib": fib,
            
            # Patterns
            "primary_pattern": primary_pattern.to_dict() if primary_pattern else None,
            "pattern_geometry": normalize_pattern_geometry(primary_pattern.to_dict()) if primary_pattern else None,
            "alternative_patterns": [a.to_dict() for a in alternatives] if alternatives else [],
            
            # Indicators (convert IndicatorSignal objects to dicts)
            "indicator_result": [s.to_dict() if hasattr(s, 'to_dict') else s for s in indicator_result] if indicator_result else [],
            "indicators": indicators_viz,  # {overlays: [...], panes: [...]} for chart rendering
            "indicator_insights": indicator_insights.to_dict(),  # RSI/MACD interpretations for Research
            "ta_context": ta_context,
            
            # Decision & Setup
            "decision": decision,
            "unified_setup": unified_setup,
            "trade_setup": trade_setup,
            "execution": execution,
            
            # Chain highlighting
            "chain_map": chain_map,
            
            # RENDER PLAN V2 — for clean chart rendering
            "render_plan": render_plan,
            
            # Meta
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def _hard_filter_recency(self, candidates: List, candles: List[Dict]) -> List:
        """Filter patterns that are too old."""
        if not candidates or not candles:
            return candidates
        
        total = len(candles)
        filtered = []
        
        for c in candidates:
            recency = (total - 1 - c.last_touch_index) / max(total, 1)
            if recency > 0.35:
                continue
            if c.end_index < total * 0.7:
                continue
            filtered.append(c)
        
        return filtered
    
    def _build_chain_map(
        self,
        unified_setup: Dict[str, Any],
        liquidity: Dict[str, Any],
        displacement: Dict[str, Any],
        choch_validation: Dict[str, Any],
        poi: Dict[str, Any],
        primary_pattern: Optional[Dict[str, Any]],
        candles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Build chain_map for chart highlighting.
        
        Maps each chain element to chart coordinates.
        """
        chain_map = []
        chain = unified_setup.get("chain", [])
        
        # Map sweeps
        sweeps = liquidity.get("sweeps", []) if liquidity else []
        for sweep in sweeps[:2]:
            chain_map.append({
                "type": "sweep",
                "label": sweep.get("label", "sweep"),
                "direction": sweep.get("direction"),
                "candle_index": sweep.get("candle_index"),
                "price": sweep.get("price"),
            })
        
        # Map displacement events
        events = displacement.get("events", []) if displacement else []
        for event in events[:2]:
            chain_map.append({
                "type": "displacement",
                "direction": event.get("direction"),
                "start_index": event.get("start_index"),
                "end_index": event.get("end_index"),
                "impulse": event.get("impulse"),
            })
        
        # Map CHOCH
        if choch_validation and choch_validation.get("is_valid"):
            chain_map.append({
                "type": "choch",
                "direction": choch_validation.get("direction"),
                "price": choch_validation.get("price"),
                "candle_index": choch_validation.get("candle_index"),
            })
        
        # Map POI zones
        zones = poi.get("zones", []) if poi else []
        for zone in zones[:3]:
            chain_map.append({
                "type": "poi",
                "zone_type": zone.get("type"),
                "price_low": zone.get("price_low", zone.get("lower")),
                "price_high": zone.get("price_high", zone.get("upper")),
            })
        
        # Map pattern
        if primary_pattern:
            chain_map.append({
                "type": "pattern",
                "pattern_type": primary_pattern.get("type"),
                "direction_bias": primary_pattern.get("direction_bias"),
                "breakout_level": primary_pattern.get("breakout_level"),
                "invalidation": primary_pattern.get("invalidation"),
            })
        
        return chain_map
    
    def _empty_result(self, timeframe: str, symbol: str) -> Dict[str, Any]:
        """Return empty result template."""
        return {
            "timeframe": timeframe,
            "symbol": symbol,
            "candles": [],
            "candle_count": 0,
            "current_price": 0,
            "structure_context": None,
            "liquidity": None,
            "displacement": None,
            "choch_validation": None,
            "poi": None,
            "fib": None,
            "primary_pattern": None,
            "alternative_patterns": [],
            "indicator_result": None,
            "indicators": {"overlays": [], "panes": []},  # Empty renderable indicators
            "indicator_insights": {},  # Empty insights
            "ta_context": None,
            "decision": None,
            "unified_setup": {"valid": False, "direction": "no_trade", "chain": []},
            "trade_setup": None,
            "execution": {"valid": False},
            "chain_map": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Factory
_per_tf_builder = None

def get_per_timeframe_builder() -> PerTimeframeBuilder:
    global _per_tf_builder
    if _per_tf_builder is None:
        _per_tf_builder = PerTimeframeBuilder()
    return _per_tf_builder
