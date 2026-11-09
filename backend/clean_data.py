"""Utility script to clean all database tables and uploaded files.

Usage:
    python clean_data.py
"""

import asyncio
import os
import shutil
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def clean_database():
    print("=" * 50)
    print("  FinSaathi Data Cleaning Utility")
    print("=" * 50)

    db_url = settings.database_url
    print(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    try:
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            # Order tables to respect Foreign Key constraints
            tables_to_clean = [
                "document_extractions",
                "uploaded_documents",
                "service_requests",
                "claim_intimations",
                "chat_sessions",
                "audit_log",
                "guardrail_events",
            ]

            print("\nCleaning Database Tables:")
            is_postgres = "postgresql" in db_url.lower()

            if is_postgres:
                for table in tables_to_clean:
                    try:
                        await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                        print(f"  [DB] Cleared table '{table}' (TRUNCATE CASCADE)")
                    except Exception as err:
                        print(f"  [DB Warning] Failed to truncate {table}: {err}")
            else:
                for table in tables_to_clean:
                    try:
                        await conn.execute(text(f"DELETE FROM {table};"))
                        print(f"  [DB] Cleared table '{table}' (DELETE FROM)")
                    except Exception as err:
                        print(f"  [DB Warning] Failed to delete from {table}: {err}")

        await engine.dispose()
        print("\nDatabase cleaning complete!")

    except Exception as e:
        print(f"\n[DB Error] Could not clean database tables: {e}")

    # Clean Uploads Directory
    upload_path = settings.upload_path
    print(f"\nCleaning Uploads Directory: {upload_path}")
    if upload_path.exists():
        cleaned_count = 0
        for item in upload_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                cleaned_count += 1
            elif item.is_file() and item.name != ".gitkeep":
                os.remove(item)
                cleaned_count += 1
        print(f"  [Disk] Removed {cleaned_count} uploaded folders/files.")
    else:
        upload_path.mkdir(parents=True, exist_ok=True)
        print("  [Disk] Created fresh uploads directory.")

    print("\n" + "=" * 50)
    print("  ALL DATA SUCCESSFULLY CLEANED!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(clean_database())
