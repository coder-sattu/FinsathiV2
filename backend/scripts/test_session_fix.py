import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import ASGITransport, AsyncClient
from app.main import app

async def test_session_endpoints():
    print("[INFO] Starting test of session endpoints...")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test /chat/start
        res_start = await client.post("/chat/start")
        print(f"1. /chat/start status: {res_start.status_code}")
        assert res_start.status_code == 200
        valid_id = res_start.json()["session_id"]
        print(f" -> Created valid session: {valid_id}")

        # 2. Test /chat/session/{valid_session_id}
        res_valid = await client.get(f"/chat/session/{valid_id}")
        print(f"2. /chat/session/VALID status: {res_valid.status_code}")
        assert res_valid.status_code == 200

        # 3. Test /chat/session/{invalid_session_id}
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        res_invalid = await client.get(f"/chat/session/{fake_uuid}")
        print(f"3. /chat/session/INVALID status: {res_invalid.status_code}")
        print(f" -> Response body: {res_invalid.json()}")
        assert res_invalid.status_code == 404
        assert res_invalid.json()["detail"] == "Session not found"

        print("[SUCCESS] All endpoint tests passed! No 500 error, 404 handled cleanly.")

if __name__ == "__main__":
    asyncio.run(test_session_endpoints())
