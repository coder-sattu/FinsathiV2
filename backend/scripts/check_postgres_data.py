import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_postgres():
    print(f"[INFO] Connecting to database: {settings.database_url}")
    engine = create_async_engine(settings.database_url, echo=False)
    
    tables = [
        "chat_sessions",
        "claim_intimations",
        "service_requests",
        "uploaded_documents",
        "document_extractions",
        "audit_logs",
        "guardrail_logs"
    ]
    
    try:
        async with engine.connect() as conn:
            print("[SUCCESS] PostgreSQL Connection Established Successfully!\n")
            print("=================================================================")
            print(f"{'TABLE NAME':<25} | {'RECORD COUNT':<15} | STATUS")
            print("=================================================================")
            
            for table in tables:
                try:
                    res = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = res.scalar()
                    print(f"{table:<25} | {count:<15} | Active & Storing Data")
                except Exception as e:
                    print(f"{table:<25} | {'N/A':<15} | Table missing or error ({e})")
            print("=================================================================\n")
            
            # Show latest sessions if available
            try:
                res_sess = await conn.execute(text("SELECT id, state, policy_no, created_at FROM chat_sessions ORDER BY created_at DESC LIMIT 3"))
                rows = res_sess.fetchall()
                if rows:
                    print("[INFO] Latest 3 Chat Sessions dumped in PostgreSQL:")
                    for r in rows:
                        print(f" - Session ID: {r[0]} | State: {r[1]} | Policy: {r[2]} | Created: {r[3]}")
                else:
                    print("[INFO] Database connected cleanly. No chat sessions dumped yet.")
            except Exception:
                pass
                
    except Exception as err:
        print(f"[NOTICE] PostgreSQL service connection check: {err}")
        print("[INFO] Note: PostgreSQL container/service status checked. Ensure PostgreSQL server is running on localhost:5432.")

if __name__ == "__main__":
    asyncio.run(check_postgres())
