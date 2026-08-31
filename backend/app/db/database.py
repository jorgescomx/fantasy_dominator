from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from backend.app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBLeagueConfig(Base):
    __tablename__ = "league_configs"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(String, unique=True, index=True)
    name = Column(String, default="10-Team Dominator League")
    year = Column(Integer, default=2024)
    num_teams = Column(Integer, default=10)
    scoring_type = Column(String, default="PPR")
    is_private = Column(Boolean, default=False)
    roster_settings = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DBDraftState(Base):
    __tablename__ = "draft_states"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(String, index=True)
    current_pick = Column(Integer, default=1)
    current_round = Column(Integer, default=1)
    user_team_id = Column(Integer, default=1)
    picks = Column(JSON, default=list) # List of {pick_num, round, team_id, player_id, player_name, position, vorp}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DBCachedPlayer(Base):
    __tablename__ = "cached_players"
    id = Column(String, primary_key=True, index=True) # e.g. espn_id or normalized key
    name = Column(String, index=True)
    position = Column(String, index=True)
    team = Column(String, index=True)
    adp = Column(Float, default=999.0)
    projected_points_season = Column(Float, default=0.0)
    projected_points_week = Column(Float, default=0.0)
    xfp_per_game = Column(Float, default=0.0)
    route_participation = Column(Float, default=0.0)
    high_value_touches = Column(Float, default=0.0)
    red_zone_share = Column(Float, default=0.0)
    proe = Column(Float, default=0.0)
    injury_status = Column(String, default="ACTIVE")
    espn_ownership_pct = Column(Float, default=0.0)
    espn_projection = Column(Float, default=0.0)
    details = Column(JSON, default=dict)

class DBInjuryRecord(Base):
    __tablename__ = "injury_records"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)  # normalized player key (e.g., "wr-marv")
    player_name = Column(String, index=True)
    status = Column(String, index=True, default="ACTIVE")  # ACTIVE, QUESTIONABLE, OUT, IR, PUP, SUSPENDED, CUT
    body_part = Column(String, nullable=True)  # Hamstring, Calf, Illness, etc. (optional from ESPN)
    timeline = Column(String, nullable=True)  # Day-to-day, Weeks 1-4, etc.
    source = Column(String, index=True)  # ESPN or Sleeper
    discount_factor = Column(Float, default=1.0)  # 0.0-1.0 (calculated from status + body_part)
    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)  # Additional context (coaching quotes, etc.)

class DBPlayerContext(Base):
    __tablename__ = "player_context"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)  # normalized player key
    player_name = Column(String, index=True)
    position = Column(String, index=True)
    team = Column(String, index=True)

    # 2025 Context (previous season)
    qb_2025 = Column(String, nullable=True)  # QB name in 2025
    oc_2025 = Column(String, nullable=True)  # Offensive coordinator in 2025
    hc_2025 = Column(String, nullable=True)  # Head coach in 2025

    # 2026 Context (current season)
    qb_2026 = Column(String, nullable=True)  # QB name in 2026
    oc_2026 = Column(String, nullable=True)  # Offensive coordinator in 2026
    hc_2026 = Column(String, nullable=True)  # Head coach in 2026

    # Context Certainty (calculated)
    context_certainty = Column(Float, default=1.0)  # 0.4-1.0
    context_changes = Column(JSON, default=dict)  # {qb_changed: bool, oc_changed: bool, hc_changed: bool}

    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DBPlayerMetrics(Base):
    __tablename__ = "player_metrics"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)  # normalized player key
    player_name = Column(String, index=True)

    # Historical (2025) Metrics
    xfp_projected = Column(Float, default=0.0)  # 2025 season xFP
    route_participation_projected = Column(Float, default=0.0)  # 2025 route %
    high_value_touches_projected = Column(Float, default=0.0)  # 2025 HVTs
    red_zone_share_projected = Column(Float, default=0.0)  # 2025 RZ share
    target_share_projected = Column(Float, default=0.0)  # 2025 target share
    proe_projected = Column(Float, default=0.0)  # 2025 PROE

    # Recalculated (adjusted by context certainty)
    xfp_recalculated = Column(Float, default=0.0)
    route_participation_recalculated = Column(Float, default=0.0)
    high_value_touches_recalculated = Column(Float, default=0.0)
    red_zone_share_recalculated = Column(Float, default=0.0)
    target_share_recalculated = Column(Float, default=0.0)
    proe_recalculated = Column(Float, default=0.0)

    # Context factor applied
    context_certainty = Column(Float, default=1.0)

    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
