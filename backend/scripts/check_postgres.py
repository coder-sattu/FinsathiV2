import asyncio
import asyncpg

async def main():
    # Connect to default postgres DB
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
    dbs = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
    db_names = [r["datname"] for r in dbs]
    print(f"Existing Databases: {db_names}")
    
    if "claimbot" not in db_names:
        print("Database 'claimbot' does not exist. Creating 'claimbot'...")
        await conn.execute("CREATE DATABASE claimbot;")
        print("Database 'claimbot' created successfully!")
    await conn.close()
    
    # Connect to claimbot DB
    conn_claimbot = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/claimbot")
    tables = await conn_claimbot.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    )
    table_names = [r["table_name"] for r in tables]
    print(f"Tables in 'claimbot' database ({len(table_names)} tables): {table_names}")
    
    for table in table_names:
        count = await conn_claimbot.fetchval(f"SELECT COUNT(*) FROM {table}")
        print(f"  - Table {table}: {count} rows")
        
    await conn_claimbot.close()

if __name__ == "__main__":
    asyncio.run(main())
