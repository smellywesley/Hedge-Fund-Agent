"""Phase 2 persistence. SQLite by default (zero setup), Postgres via
DATABASE_URL (docker compose service is already provisioned).

Only the tables the app actually uses are modeled here; db/schema.sql remains
the full Phase 2+ target schema.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# ponytail: sqlite default so the app runs without Docker; set DATABASE_URL
# to the compose postgres (postgresql://terminal:terminal@localhost:5432/terminal_alpha)
# and install psycopg2-binary to switch.
DEFAULT_SQLITE = f"sqlite:///{Path(__file__).resolve().parents[1] / 'terminal_alpha.db'}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE)
# Railway/Heroku hand out postgres:// which SQLAlchemy 2.0 rejects — normalize.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


class Base(DeclarativeBase):
    pass


class WatchlistRow(Base):
    __tablename__ = "watchlist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, unique=True)
    next_action: Mapped[str] = mapped_column(String, default="Research")
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


class PositionRow(Base):
    __tablename__ = "paper_positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String)
    entry_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[float] = mapped_column(Float)
    thesis: Mapped[str] = mapped_column(Text, default="")
    invalidation_point: Mapped[str] = mapped_column(Text, default="")
    catalyst_date: Mapped[str] = mapped_column(String, default="")
    risk_notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String, default="OPEN")
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


class JournalRow(Base):
    __tablename__ = "decision_journal"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String)
    symbol: Mapped[str] = mapped_column(String)
    decision_type: Mapped[str] = mapped_column(String)
    decision_text: Mapped[str] = mapped_column(Text)
    human_note: Mapped[str] = mapped_column(Text, default="")


class FundRow(Base):
    __tablename__ = "fund"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cash_usd: Mapped[float] = mapped_column(Float)


class PriceRow(Base):
    __tablename__ = "market_prices_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[str] = mapped_column(String, index=True)  # ISO yyyy-mm-dd
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float, default=0)


class NavRow(Base):
    __tablename__ = "nav_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String, unique=True)  # ISO yyyy-mm-dd
    nav: Mapped[float] = mapped_column(Float)


class ResearchReportRow(Base):
    """AI-generated research notes (Run Research button), stored only after
    passing the audit gate. JSON-encoded list fields kept as Text for
    SQLite/Postgres parity."""
    __tablename__ = "research_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    snapshot: Mapped[str] = mapped_column(Text, default="")
    business_model: Mapped[str] = mapped_column(Text, default="")
    bull_case: Mapped[str] = mapped_column(Text, default="")
    bear_case: Mapped[str] = mapped_column(Text, default="")
    red_team: Mapped[str] = mapped_column(Text, default="")
    key_risks: Mapped[str] = mapped_column(Text, default="[]")
    sources: Mapped[str] = mapped_column(Text, default="[]")
    missing_data: Mapped[str] = mapped_column(Text, default="[]")
    confidence: Mapped[str] = mapped_column(String, default="Low")
    model: Mapped[str] = mapped_column(String, default="")
    generated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


class AuditRow(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String)
    symbol: Mapped[str] = mapped_column(String, default="")
    detail: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


def audit(session: Session, event_type: str, symbol: str = "", **detail) -> None:
    session.add(AuditRow(event_type=event_type, symbol=symbol, detail=json.dumps(detail)))


# Seed quantities sized so position value ≈ blueprint target % of $1M paper AUM
# at the Phase 1 mock prices.
SEED_POSITIONS = [
    dict(symbol="NVDA", entry_price=148.00, quantity=756, thesis="AI infrastructure capex supercycle; CUDA moat", invalidation_point="Hyperscaler capex guidance cut >10%", catalyst_date="2026-08-26", risk_notes="Valuation sensitivity; sector concentration"),
    dict(symbol="TSM", entry_price=190.50, quantity=539, thesis="Foundry monopoly on leading edge; AI wafer demand", invalidation_point="N2 yield issues or Taiwan-strait escalation", catalyst_date="2026-07-17", risk_notes="Geopolitical tail risk"),
    dict(symbol="MSFT", entry_price=465.00, quantity=214, thesis="Azure AI monetization + Copilot seat expansion", invalidation_point="Azure growth <25% two consecutive quarters", catalyst_date="2026-07-29", risk_notes="Capex intensity compressing FCF"),
    dict(symbol="LLY", entry_price=845.20, quantity=106, thesis="GLP-1 franchise expansion into oral formulations", invalidation_point="Oral candidate misses efficacy endpoint", catalyst_date="2026-09-30", risk_notes="Pricing headlines; pipeline binary events"),
    dict(symbol="GOOGL", entry_price=188.00, quantity=476, thesis="Search resilience + Gemini enterprise traction, undemanding multiple", invalidation_point="Search revenue decline on AI substitution", catalyst_date="2026-07-23", risk_notes="Antitrust remedies overhang"),
]

SEED_WATCHLIST = ["NVDA", "AAPL", "MSFT", "TSM", "LLY"]

SEED_JOURNAL = [
    dict(date="2026-07-03", symbol="NVDA", decision_type="REVIEW", decision_text="Held through roadmap news; thesis intact.", human_note="Watch custom-silicon narrative."),
    dict(date="2026-06-24", symbol="LLY", decision_type="ADD", decision_text="Added paper position after pullback.", human_note="Sized below 10% due to binary pipeline risk."),
    dict(date="2026-06-10", symbol="AMD", decision_type="PASS", decision_text="Passed — thesis overlapped NVDA without diversification benefit.", human_note="Avoid crowding the same trade."),
]


def init_db() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        if not s.query(FundRow).first():
            s.add(FundRow(cash_usd=451_000))
        if not s.query(WatchlistRow).first():
            for sym in SEED_WATCHLIST:
                s.add(WatchlistRow(symbol=sym))
        if not s.query(PositionRow).first():
            for p in SEED_POSITIONS:
                s.add(PositionRow(**p))
        if not s.query(JournalRow).first():
            for j in SEED_JOURNAL:
                s.add(JournalRow(**j))
        audit(s, "seed_check")
        s.commit()
