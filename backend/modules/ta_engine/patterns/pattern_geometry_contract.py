"""
Pattern Geometry Contract
=========================

Universal schema for pattern visualization.
Backend converts ANY pattern to this format.
Frontend renders ONLY primitives (segments, levels, zones, markers).

GEOMETRY CONTRACT:
{
    "type": "ascending_triangle",
    "label": "Ascending Triangle",
    "direction": "bullish",
    "confidence": 0.85,
    "status": "active",
    "geometry": {
        "segments": [
            {"kind": "resistance", "style": "solid", "points": [{"time": t, "price": p}, ...]},
            {"kind": "support_rising", "style": "solid", "points": [...]}
        ],
        "levels": [
            {"kind": "breakout", "price": 73968.0, "label": "Breakout"},
            {"kind": "invalidation", "price": 70236.0, "label": "Invalidation"}
        ],
        "zones": [
            {"kind": "pattern_area", "time_start": t, "time_end": t, "price_top": p, "price_bottom": p}
        ],
        "markers": [
            {"kind": "anchor", "time": t, "price": p, "label": "H1"}
        ]
    }
}

SUPPORTED SEGMENT KINDS:
- resistance, support, support_rising, support_falling
- neckline, upper_channel, lower_channel
- trendline_upper, trendline_lower
- left_shoulder, head, right_shoulder (for H&S)

SUPPORTED LEVEL KINDS:
- breakout, invalidation, neckline, target

SUPPORTED ZONE KINDS:
- pattern_area, consolidation, apex_zone

SUPPORTED MARKER KINDS:
- anchor, peak, trough, shoulder, head
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class GeometrySegment:
    """Line segment for pattern boundary."""
    kind: str  # resistance, support, neckline, etc.
    points: List[Dict[str, float]]  # [{"time": t, "price": p}, ...]
    style: str = "solid"  # solid, dashed, dotted
    color: Optional[str] = None


@dataclass
class GeometryLevel:
    """Horizontal price level."""
    kind: str  # breakout, invalidation, neckline, target
    price: float
    label: Optional[str] = None
    style: str = "dashed"
    color: Optional[str] = None


@dataclass
class GeometryZone:
    """Rectangular area (e.g., consolidation zone)."""
    kind: str  # pattern_area, apex_zone
    time_start: int
    time_end: int
    price_top: float
    price_bottom: float
    color: Optional[str] = None
    opacity: float = 0.1


@dataclass
class GeometryMarker:
    """Point marker with optional label."""
    kind: str  # anchor, peak, trough, shoulder, head
    time: int
    price: float
    label: Optional[str] = None


@dataclass
class PatternGeometry:
    """Universal geometry container."""
    segments: List[GeometrySegment] = field(default_factory=list)
    levels: List[GeometryLevel] = field(default_factory=list)
    zones: List[GeometryZone] = field(default_factory=list)
    markers: List[GeometryMarker] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "segments": [
                {"kind": s.kind, "style": s.style, "points": s.points, "color": s.color}
                for s in self.segments
            ],
            "levels": [
                {"kind": l.kind, "price": l.price, "label": l.label, "style": l.style, "color": l.color}
                for l in self.levels
            ],
            "zones": [
                {"kind": z.kind, "time_start": z.time_start, "time_end": z.time_end, 
                 "price_top": z.price_top, "price_bottom": z.price_bottom, "color": z.color, "opacity": z.opacity}
                for z in self.zones
            ],
            "markers": [
                {"kind": m.kind, "time": m.time, "price": m.price, "label": m.label}
                for m in self.markers
            ],
        }


def normalize_pattern_geometry(pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert any pattern format to universal geometry contract.
    
    This is the SINGLE place where pattern-specific logic lives.
    Frontend NEVER needs to know pattern internals.
    """
    if not pattern:
        return None
    
    pattern_type = pattern.get("type", "").lower()
    points = pattern.get("points", {})
    anchor_points = pattern.get("anchor_points", {})
    breakout = pattern.get("breakout_level")
    invalidation = pattern.get("invalidation")
    
    geometry = PatternGeometry()
    
    # ===========================================
    # TRIANGLES
    # ===========================================
    if "triangle" in pattern_type:
        # Upper line (resistance or descending trendline)
        if "upper" in points:
            upper_pts = points["upper"]
            if len(upper_pts) >= 2:
                kind = "resistance" if "ascending" in pattern_type else "resistance_falling"
                geometry.segments.append(GeometrySegment(
                    kind=kind,
                    points=[{"time": p["time"], "price": p["value"]} for p in upper_pts],
                    style="solid",
                    color="#ef4444" if "descending" in pattern_type else "#64748b"
                ))
        
        # Lower line (support or ascending trendline)
        if "lower" in points:
            lower_pts = points["lower"]
            if len(lower_pts) >= 2:
                kind = "support_rising" if "ascending" in pattern_type else "support"
                geometry.segments.append(GeometrySegment(
                    kind=kind,
                    points=[{"time": p["time"], "price": p["value"]} for p in lower_pts],
                    style="solid",
                    color="#16a34a" if "ascending" in pattern_type else "#64748b"
                ))
        
        # Anchor markers
        for side, anchors in anchor_points.items():
            for i, a in enumerate(anchors):
                geometry.markers.append(GeometryMarker(
                    kind="anchor",
                    time=a["time"],
                    price=a["value"],
                    label=f"{side[0].upper()}{i+1}"  # U1, U2, L1, L2
                ))
    
    # ===========================================
    # CHANNELS (ascending, descending, horizontal)
    # ===========================================
    elif "channel" in pattern_type:
        if "upper" in points:
            geometry.segments.append(GeometrySegment(
                kind="upper_channel",
                points=[{"time": p["time"], "price": p["value"]} for p in points["upper"]],
                style="solid",
                color="#ef4444"
            ))
        if "lower" in points:
            geometry.segments.append(GeometrySegment(
                kind="lower_channel",
                points=[{"time": p["time"], "price": p["value"]} for p in points["lower"]],
                style="solid",
                color="#16a34a"
            ))
    
    # ===========================================
    # HEAD & SHOULDERS
    # ===========================================
    elif "head" in pattern_type and "shoulder" in pattern_type:
        # Neckline
        if "neckline" in points:
            geometry.segments.append(GeometrySegment(
                kind="neckline",
                points=[{"time": p["time"], "price": p["value"]} for p in points["neckline"]],
                style="dashed",
                color="#f59e0b"
            ))
        
        # Shoulders and head markers
        for key in ["left_shoulder", "head", "right_shoulder"]:
            if key in points:
                p = points[key]
                geometry.markers.append(GeometryMarker(
                    kind=key,
                    time=p["time"],
                    price=p["value"],
                    label=key.replace("_", " ").title()
                ))
    
    # ===========================================
    # DOUBLE TOP / BOTTOM
    # ===========================================
    elif "double" in pattern_type:
        if "peaks" in points or "peak1" in points:
            peaks = points.get("peaks", [])
            if not peaks and "peak1" in points:
                peaks = [points["peak1"], points.get("peak2")]
            for i, p in enumerate(peaks):
                if p:
                    geometry.markers.append(GeometryMarker(
                        kind="peak" if "top" in pattern_type else "trough",
                        time=p["time"],
                        price=p["value"],
                        label=f"{'T' if 'top' in pattern_type else 'B'}{i+1}"
                    ))
        
        if "neckline" in points:
            geometry.segments.append(GeometrySegment(
                kind="neckline",
                points=[{"time": p["time"], "price": p["value"]} for p in points["neckline"]],
                style="dashed",
                color="#f59e0b"
            ))
    
    # ===========================================
    # WEDGE (rising, falling)
    # ===========================================
    elif "wedge" in pattern_type:
        if "upper" in points:
            geometry.segments.append(GeometrySegment(
                kind="trendline_upper",
                points=[{"time": p["time"], "price": p["value"]} for p in points["upper"]],
                style="solid",
                color="#ef4444"
            ))
        if "lower" in points:
            geometry.segments.append(GeometrySegment(
                kind="trendline_lower",
                points=[{"time": p["time"], "price": p["value"]} for p in points["lower"]],
                style="solid",
                color="#16a34a"
            ))
    
    # ===========================================
    # FLAG / PENNANT
    # ===========================================
    elif "flag" in pattern_type or "pennant" in pattern_type:
        if "pole" in points:
            geometry.segments.append(GeometrySegment(
                kind="pole",
                points=[{"time": p["time"], "price": p["value"]} for p in points["pole"]],
                style="solid",
                color="#3b82f6"
            ))
        if "flag_upper" in points:
            geometry.segments.append(GeometrySegment(
                kind="flag_upper",
                points=[{"time": p["time"], "price": p["value"]} for p in points["flag_upper"]],
                style="solid"
            ))
        if "flag_lower" in points:
            geometry.segments.append(GeometrySegment(
                kind="flag_lower",
                points=[{"time": p["time"], "price": p["value"]} for p in points["flag_lower"]],
                style="solid"
            ))
    
    # ===========================================
    # RANGE / RECTANGLE
    # ===========================================
    elif "range" in pattern_type or "rectangle" in pattern_type:
        if "resistance" in points:
            geometry.segments.append(GeometrySegment(
                kind="resistance",
                points=[{"time": p["time"], "price": p["value"]} for p in points["resistance"]],
                style="solid",
                color="#ef4444"
            ))
        if "support" in points:
            geometry.segments.append(GeometrySegment(
                kind="support",
                points=[{"time": p["time"], "price": p["value"]} for p in points["support"]],
                style="solid",
                color="#16a34a"
            ))
        
        # Add zone if we have both levels
        if breakout and invalidation:
            # Get time range from points
            all_times = []
            for pts in points.values():
                if isinstance(pts, list):
                    all_times.extend([p.get("time", 0) for p in pts])
            if all_times:
                geometry.zones.append(GeometryZone(
                    kind="pattern_area",
                    time_start=min(all_times),
                    time_end=max(all_times),
                    price_top=max(breakout, invalidation),
                    price_bottom=min(breakout, invalidation),
                    opacity=0.08
                ))
    
    # ===========================================
    # COMMON: LEVELS (breakout, invalidation)
    # ===========================================
    if breakout:
        geometry.levels.append(GeometryLevel(
            kind="breakout",
            price=breakout,
            label="Breakout",
            style="dashed",
            color="#16a34a"
        ))
    
    if invalidation:
        geometry.levels.append(GeometryLevel(
            kind="invalidation",
            price=invalidation,
            label="Invalidation",
            style="dotted",
            color="#ef4444"
        ))
    
    # ===========================================
    # BUILD FINAL CONTRACT
    # ===========================================
    label_map = {
        "ascending_triangle": "Ascending Triangle",
        "descending_triangle": "Descending Triangle",
        "symmetrical_triangle": "Symmetrical Triangle",
        "ascending_channel": "Ascending Channel",
        "descending_channel": "Descending Channel",
        "horizontal_channel": "Horizontal Channel",
        "head_and_shoulders": "Head & Shoulders",
        "inverse_head_and_shoulders": "Inverse Head & Shoulders",
        "double_top": "Double Top",
        "double_bottom": "Double Bottom",
        "triple_top": "Triple Top",
        "triple_bottom": "Triple Bottom",
        "rising_wedge": "Rising Wedge",
        "falling_wedge": "Falling Wedge",
        "bull_flag": "Bull Flag",
        "bear_flag": "Bear Flag",
        "pennant": "Pennant",
        "range": "Trading Range",
        "rectangle": "Rectangle",
    }
    
    return {
        "type": pattern_type,
        "label": label_map.get(pattern_type, pattern_type.replace("_", " ").title()),
        "direction": pattern.get("direction", "neutral"),
        "confidence": round(pattern.get("confidence", 0), 2),
        "status": "active",
        "geometry": geometry.to_dict(),
    }


# Singleton for easy import
def get_geometry_normalizer():
    return normalize_pattern_geometry
