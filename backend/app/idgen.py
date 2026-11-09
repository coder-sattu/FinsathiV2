"""Sequence-based ID generator for Claim and SR numbers."""

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# fallback sequence counters in memory for tests without DB sequence
_fallback_claim_seq = 100
_fallback_sr_seq = 100


async def generate_claim_no(session: AsyncSession | None = None, year: int | None = None) -> str:
    # generate claim no
    global _fallback_claim_seq
    current_year = year or datetime.now().year
    if session is not None:
        try:
            res = await session.execute(text("SELECT nextval('claim_no_seq')"))
            seq_val = res.scalar_one()
            return f"CLM-{current_year}-{seq_val:06d}"
        except Exception as e:
            try:
                await session.rollback()
            except Exception:
                pass

    _fallback_claim_seq += 1
    return f"CLM-{current_year}-{_fallback_claim_seq:06d}"


async def generate_sr_no(session: AsyncSession | None = None, year: int | None = None) -> str:
    # generate sr no
    global _fallback_sr_seq
    current_year = year or datetime.now().year
    if session is not None:
        try:
            res = await session.execute(text("SELECT nextval('sr_no_seq')"))
            seq_val = res.scalar_one()
            return f"SR-{current_year}-{seq_val:06d}"
        except Exception as e:
            try:
                await session.rollback()
            except Exception:
                pass

    _fallback_sr_seq += 1
    return f"SR-{current_year}-{_fallback_sr_seq:06d}"
