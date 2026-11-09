import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.tables import Base

async def init_tables():
    print(f"Connecting to database: {settings.database_url}")
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        print("Creating all tables and sequences in PostgreSQL database...")
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        await conn.execute(text("CREATE SEQUENCE IF NOT EXISTS claim_no_seq START 100;"))
        await conn.execute(text("CREATE SEQUENCE IF NOT EXISTS sr_no_seq START 100;"))
    await engine.dispose()
    print("All PostgreSQL tables and sequences initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_tables())
