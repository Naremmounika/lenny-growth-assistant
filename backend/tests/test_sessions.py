import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_and_get_session():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        create_response = await client.post(
            "/api/sessions",
            json={
                "title": "Test Conversation",
            },
        )

        assert create_response.status_code in (200, 201)

        created_session = create_response.json()

        assert "id" in created_session

        session_id = created_session["id"]

        get_response = await client.get(
            f"/api/sessions/{session_id}"
        )

        assert get_response.status_code == 200

        session = get_response.json()

        assert session["id"] == session_id
        assert session["title"] == "Test Conversation"