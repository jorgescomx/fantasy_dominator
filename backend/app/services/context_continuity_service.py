"""
Context continuity service.
Detects QB/OC/HC changes and calculates context certainty factor.
Adjusts historical metrics based on environmental stability.
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal, DBPlayerContext, DBPlayerMetrics
import logging

logger = logging.getLogger(__name__)

def normalize_name(name: str) -> str:
    """Normalize name for comparison."""
    return name.lower().replace(".", "").replace("'", "").replace("-", " ").strip()

def calculate_context_certainty(
    qb_same: bool,
    oc_same: bool,
    hc_same: bool,
    supporting_cast_stable: bool = True,
    role_same: bool = True
) -> float:
    """
    Calculate context certainty factor (0.4-1.0).

    Scoring:
    - QB same: +0.30
    - OC same: +0.20
    - HC same: +0.20
    - Supporting cast stable: +0.15
    - Same role: +0.15
    = max 1.0, minimum floor 0.40
    """
    score = 0.0

    if qb_same:
        score += 0.30
    if oc_same:
        score += 0.20
    if hc_same:
        score += 0.20
    if supporting_cast_stable:
        score += 0.15
    if role_same:
        score += 0.15

    # Minimum floor for rookies/unknowns
    return max(0.40, min(1.0, score))

def store_player_context(
    player_id: str,
    player_name: str,
    position: str,
    team: str,
    qb_2025: Optional[str],
    oc_2025: Optional[str],
    hc_2025: Optional[str],
    qb_2026: Optional[str],
    oc_2026: Optional[str],
    hc_2026: Optional[str]
) -> Dict[str, Any]:
    """Store player context and calculate certainty."""
    db = SessionLocal()
    try:
        # Detect changes
        qb_same = normalize_name(qb_2025 or "") == normalize_name(qb_2026 or "")
        oc_same = normalize_name(oc_2025 or "") == normalize_name(oc_2026 or "")
        hc_same = normalize_name(hc_2025 or "") == normalize_name(hc_2026 or "")

        context_changes = {
            "qb_changed": not qb_same,
            "oc_changed": not oc_same,
            "hc_changed": not hc_same,
            "major_overhaul": (not qb_same) and (not oc_same)  # Both QB and OC changed
        }

        # Calculate certainty
        certainty = calculate_context_certainty(
            qb_same=qb_same,
            oc_same=oc_same,
            hc_same=hc_same,
            supporting_cast_stable=True,
            role_same=True
        )

        # Upsert into database
        record = db.query(DBPlayerContext).filter(
            DBPlayerContext.player_id == player_id
        ).first()

        if record:
            record.qb_2025 = qb_2025
            record.oc_2025 = oc_2025
            record.hc_2025 = hc_2025
            record.qb_2026 = qb_2026
            record.oc_2026 = oc_2026
            record.hc_2026 = hc_2026
            record.context_certainty = certainty
            record.context_changes = context_changes
            record.last_updated_at = datetime.utcnow()
        else:
            record = DBPlayerContext(
                player_id=player_id,
                player_name=player_name,
                position=position,
                team=team,
                qb_2025=qb_2025,
                oc_2025=oc_2025,
                hc_2025=hc_2025,
                qb_2026=qb_2026,
                oc_2026=oc_2026,
                hc_2026=hc_2026,
                context_certainty=certainty,
                context_changes=context_changes
            )
            db.add(record)

        db.commit()

        return {
            "player_id": player_id,
            "player_name": player_name,
            "context_certainty": certainty,
            "context_changes": context_changes
        }

    except Exception as e:
        logger.error(f"Error storing context for {player_name}: {e}")
        return {}

    finally:
        db.close()

def apply_context_factor_to_metrics(
    player_id: str,
    projected_xfp: float = 0.0,
    projected_route_pct: float = 0.0,
    projected_hvt: float = 0.0,
    projected_rz_share: float = 0.0,
    projected_target_share: float = 0.0,
    projected_proe: float = 0.0
) -> Dict[str, Any]:
    """
    Apply context certainty factor to historical metrics.
    Returns both projected and recalculated values.
    """
    db = SessionLocal()
    try:
        # Get player's context certainty
        context = db.query(DBPlayerContext).filter(
            DBPlayerContext.player_id == player_id
        ).first()

        if not context:
            # No context found (rookie/new player) - use minimum floor
            certainty = 0.40
            changes = {}
        else:
            certainty = context.context_certainty
            changes = context.context_changes or {}

        # Apply factor to all metrics
        factor = certainty
        recalculated_xfp = projected_xfp * factor
        recalculated_route_pct = projected_route_pct * factor
        recalculated_hvt = projected_hvt * factor
        recalculated_rz_share = projected_rz_share * factor
        recalculated_target_share = projected_target_share * factor
        recalculated_proe = projected_proe * factor

        # Store in metrics table
        metrics = db.query(DBPlayerMetrics).filter(
            DBPlayerMetrics.player_id == player_id
        ).first()

        if metrics:
            metrics.xfp_projected = projected_xfp
            metrics.route_participation_projected = projected_route_pct
            metrics.high_value_touches_projected = projected_hvt
            metrics.red_zone_share_projected = projected_rz_share
            metrics.target_share_projected = projected_target_share
            metrics.proe_projected = projected_proe

            metrics.xfp_recalculated = recalculated_xfp
            metrics.route_participation_recalculated = recalculated_route_pct
            metrics.high_value_touches_recalculated = recalculated_hvt
            metrics.red_zone_share_recalculated = recalculated_rz_share
            metrics.target_share_recalculated = recalculated_target_share
            metrics.proe_recalculated = recalculated_proe

            metrics.context_certainty = certainty
            metrics.last_updated_at = datetime.utcnow()
        else:
            metrics = DBPlayerMetrics(
                player_id=player_id,
                player_name="",
                xfp_projected=projected_xfp,
                route_participation_projected=projected_route_pct,
                high_value_touches_projected=projected_hvt,
                red_zone_share_projected=projected_rz_share,
                target_share_projected=projected_target_share,
                proe_projected=projected_proe,
                xfp_recalculated=recalculated_xfp,
                route_participation_recalculated=recalculated_route_pct,
                high_value_touches_recalculated=recalculated_hvt,
                red_zone_share_recalculated=recalculated_rz_share,
                target_share_recalculated=recalculated_target_share,
                proe_recalculated=recalculated_proe,
                context_certainty=certainty
            )
            db.add(metrics)

        db.commit()

        return {
            "player_id": player_id,
            "context_certainty": certainty,
            "context_changes": changes,
            "projected": {
                "xfp": projected_xfp,
                "route_participation": projected_route_pct,
                "high_value_touches": projected_hvt,
                "red_zone_share": projected_rz_share,
                "target_share": projected_target_share,
                "proe": projected_proe
            },
            "recalculated": {
                "xfp": recalculated_xfp,
                "route_participation": recalculated_route_pct,
                "high_value_touches": recalculated_hvt,
                "red_zone_share": recalculated_rz_share,
                "target_share": recalculated_target_share,
                "proe": recalculated_proe
            }
        }

    except Exception as e:
        logger.error(f"Error applying context factor for {player_id}: {e}")
        return {}

    finally:
        db.close()

def get_player_context(player_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve player context and certainty."""
    db = SessionLocal()
    try:
        context = db.query(DBPlayerContext).filter(
            DBPlayerContext.player_id == player_id
        ).first()

        if context:
            return {
                "player_id": context.player_id,
                "player_name": context.player_name,
                "position": context.position,
                "team": context.team,
                "qb_2025": context.qb_2025,
                "oc_2025": context.oc_2025,
                "hc_2025": context.hc_2025,
                "qb_2026": context.qb_2026,
                "oc_2026": context.oc_2026,
                "hc_2026": context.hc_2026,
                "context_certainty": context.context_certainty,
                "context_changes": context.context_changes
            }
        return None

    finally:
        db.close()

def get_player_metrics(player_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve player metrics (projected vs recalculated)."""
    db = SessionLocal()
    try:
        metrics = db.query(DBPlayerMetrics).filter(
            DBPlayerMetrics.player_id == player_id
        ).first()

        if metrics:
            return {
                "player_id": metrics.player_id,
                "player_name": metrics.player_name,
                "context_certainty": metrics.context_certainty,
                "projected": {
                    "xfp": metrics.xfp_projected,
                    "route_participation": metrics.route_participation_projected,
                    "high_value_touches": metrics.high_value_touches_projected,
                    "red_zone_share": metrics.red_zone_share_projected,
                    "target_share": metrics.target_share_projected,
                    "proe": metrics.proe_projected
                },
                "recalculated": {
                    "xfp": metrics.xfp_recalculated,
                    "route_participation": metrics.route_participation_recalculated,
                    "high_value_touches": metrics.high_value_touches_recalculated,
                    "red_zone_share": metrics.red_zone_share_recalculated,
                    "target_share": metrics.target_share_recalculated,
                    "proe": metrics.proe_recalculated
                }
            }
        return None

    finally:
        db.close()
